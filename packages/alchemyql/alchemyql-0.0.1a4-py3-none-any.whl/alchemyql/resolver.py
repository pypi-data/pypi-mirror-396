from enum import Enum
from typing import Any

from sqlalchemy import Select, desc, select
from sqlalchemy.orm import joinedload, load_only

from .errors import QueryExecutionError
from .models import Table


def serialize(obj, selected_fields):
    """
    Serialize ORM objects to graphql response format.
    """
    # Handle lists / tuples
    if isinstance(obj, (list, tuple)):
        return [serialize(o, selected_fields) for o in obj]

    # ORM object
    if hasattr(obj, "__mapper__"):
        data = {}
        mapper = obj.__mapper__
        for field, subfields in selected_fields.items():
            if field in mapper.columns:
                val = getattr(obj, field)
                # Convert enum if column value is enum
                data[field] = val.name if isinstance(val, Enum) else val
            elif field in mapper.relationships:
                rel_obj = getattr(obj, field)
                if isinstance(rel_obj, list):
                    data[field] = [serialize(r, subfields) for r in rel_obj]
                else:
                    data[field] = serialize(rel_obj, subfields)
        return data


def extract_selected_fields(
    selection_set, max_depth: int | None, depth: int = 1
) -> dict:
    """
    Recursively extract selected fields from GraphQL AST.
    Builds nested dictionary of fields where key is the field name and value is True (if column), dict (if relationship)
    """
    if max_depth and depth > max_depth:
        raise QueryExecutionError(f"Max query depth exceeded ({max_depth=})")

    result = {}

    for sel in selection_set.selections:
        name = sel.name.value
        if sel.selection_set:
            result[name] = extract_selected_fields(
                sel.selection_set, max_depth, depth + 1
            )
        else:
            result[name] = True

    return result


def build_rels(sqlalchemy_cls, fields: dict):
    """
    Recursively build joinedload options for nested relationships.
    This uses the input field list format from "extract_selected_fields"
    """
    joins = []
    for field_name, subfields in fields.items():
        if isinstance(subfields, dict):
            # Relationship attribute
            rel = getattr(sqlalchemy_cls, field_name)

            # Relationship SQLAlchemy class
            rel_cls = rel.prop.mapper.class_

            join = joinedload(rel)

            # Columns to load for this relationship
            if cols := [
                getattr(rel_cls, col) for col, v in subfields.items() if v is True
            ]:
                join = join.load_only(*cols)

            # Nested relationships to load
            if nested_rels := {
                rel_name: rel_fields
                for rel_name, rel_fields in subfields.items()
                if isinstance(rel_fields, dict)
            }:
                join = join.options(*build_rels(rel_cls, nested_rels))

            joins.append(join)

    return joins


def build_sql_select_stmt(
    table: Table,
    fields: dict,
    filters: dict[str, Any] | None = None,
    offset: int | None = None,
    limit: int | None = None,
    order: dict[str, Any] | None = None,
) -> Select:
    """
    Build a SQLAlchemy Select statement based on GraphQL args.
    """
    # Step 1 - Build SELECT & FROM clauses
    cols = [
        getattr(table.sqlalchemy_cls, name)
        for name, val in fields.items()
        if val is True
    ]
    rels = {name: val for name, val in fields.items() if isinstance(val, dict)}

    stmt = select(table.sqlalchemy_cls)
    stmt = stmt.options(load_only(*cols))
    if rels:
        stmt = stmt.options(*build_rels(table.sqlalchemy_cls, rels))

    # Step 2 - Build WHERE clause
    if filters:
        for col_name, operations in filters.items():
            column = getattr(table.sqlalchemy_cls, col_name)
            for op, val in operations.items():
                if op == "eq":
                    stmt = stmt.where(column == val)
                elif op == "ne":
                    stmt = stmt.where(column != val)
                elif op == "lt":
                    stmt = stmt.where(column < val)
                elif op == "le":
                    stmt = stmt.where(column <= val)
                elif op == "gt":
                    stmt = stmt.where(column > val)
                elif op == "ge":
                    stmt = stmt.where(column >= val)
                elif op == "contains":
                    stmt = stmt.where(column.contains(val))
                elif op == "in":
                    stmt = stmt.where(column.in_(val))
                elif op == "startswith":
                    stmt = stmt.where(column.startswith(val))
                elif op == "endswith":
                    stmt = stmt.where(column.endswith(val))

    # Step 3 - Build pagination clauses (OFFSET, LIMIT)
    if offset is not None:
        stmt = stmt.offset(offset)

    if limit is not None:
        stmt = stmt.limit(limit)

    # Step 4 - Build ORDER BY clause
    if order:
        for col_name, direction in order.items():
            column = getattr(table.sqlalchemy_cls, col_name)
            if str(direction).upper() == "DESC":
                column = desc(column)
            stmt = stmt.order_by(column)
    return stmt


def validations(table: Table, **kwargs):
    # Validate limit
    if limit := kwargs.get("limit"):
        if limit < 1 or (table.max_limit and limit > table.max_limit):
            raise QueryExecutionError(
                f"Provided Limit is out of bounds (Value: {limit}, Min: 1, Max: {table.max_limit})"
            )

    # Validate offset
    if offset := kwargs.get("offset"):
        if offset < 0:
            raise QueryExecutionError(
                f"Provided Offset is negative (Value: {offset}, Min: 0)"
            )


def build_async_resolver(table: Table):
    """
    Resolver function for Async queries.
    Returns a function that can be called at query execution to resolve query.
    """

    async def resolver(root, info, **kwargs):
        validations(table, **kwargs)

        db_session = info.context["session"]
        max_query_depth = info.context["max_query_depth"]

        selection = info.field_nodes[0].selection_set
        fields = extract_selected_fields(selection, max_query_depth)

        query = build_sql_select_stmt(
            table=table,
            fields=fields,
            filters=kwargs.get("filter", {}),
            offset=kwargs.get("offset", 0),
            limit=kwargs.get("limit", table.default_limit),
            order=kwargs.get("order", table.default_order),
        )

        res = await db_session.execute(query)

        return serialize(res.unique().scalars().all(), fields)

    return resolver


def build_sync_resolver(table: Table):
    """
    Resolver function for Sync queries.
    Returns a function that can be called at query execution to resolve query.
    """

    def resolver(root, info, **kwargs):
        validations(table, **kwargs)

        db_session = info.context["session"]
        max_query_depth = info.context["max_query_depth"]

        selection = info.field_nodes[0].selection_set
        fields = extract_selected_fields(selection, max_query_depth)

        query = build_sql_select_stmt(
            table=table,
            fields=fields,
            filters=kwargs.get("filter", {}),
            offset=kwargs.get("offset", 0),
            limit=kwargs.get("limit", table.default_limit),
            order=kwargs.get("order", table.default_order),
        )

        res = db_session.execute(query)

        return serialize(res.unique().scalars().all(), fields)

    return resolver
