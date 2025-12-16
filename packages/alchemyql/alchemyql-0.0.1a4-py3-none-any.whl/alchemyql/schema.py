from graphql import (
    GraphQLArgument,
    GraphQLField,
    GraphQLInputField,
    GraphQLInputObjectType,
    GraphQLList,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLSchema,
)

from .errors import ConfigurationError
from .filters import FILTERS
from .models import Table
from .resolver import build_async_resolver, build_sync_resolver
from .scalars import IntScalar, OrderingEnumScalar, convert_to_scalar


def _validate_relationships(tables: list[Table], class_to_gql: dict):
    """
    Validate that the relationships target tables which are also registered.
    """
    for table in tables:
        for rel in table.inspected.relationships:
            if rel.key not in table.relationships:
                continue

            if rel.mapper.class_ not in class_to_gql:
                raise ConfigurationError(
                    f"Relationship target table has not been registered (relationship={rel})"
                )


def _build_fields(table: Table, class_to_gql: dict, scalar_map: dict):
    """
    Build the fields for a specified table. This includes columns and relationships.
    """
    fields = {}

    # Table columns
    for col in table.inspected.columns:
        if col.key not in table.fields:
            continue

        # reuse scalar if already built
        py_type = col.type.python_type
        if py_type in scalar_map:
            gql_type = scalar_map[py_type]
        else:
            gql_type = convert_to_scalar(col)
            scalar_map[py_type] = gql_type

        if col.nullable:
            fields[col.key] = GraphQLField(gql_type)  # type: ignore
        else:
            fields[col.key] = GraphQLField(GraphQLNonNull(gql_type))  # type: ignore

    # Table relationships
    for rel in table.inspected.relationships:
        if rel.key not in table.relationships:
            continue

        target_gql = class_to_gql[rel.mapper.class_]
        gql_rel_type = GraphQLList(target_gql) if rel.uselist else target_gql
        fields[rel.key] = GraphQLField(gql_rel_type)

    return fields


def build_gql_schema(tables: list[Table], is_async: bool) -> GraphQLSchema:
    """
    Construct the graphql schema using the registered tables.
    """
    scalar_map: dict[type, object] = {}
    filter_map: dict[type, object] = {}

    # Step 1 — create empty GraphQLObjectType shells
    gql_objects = {
        t.graphql_name: GraphQLObjectType(
            name=t.graphql_name,
            description=t.description,
            fields=lambda: {},
        )
        for t in tables
    }
    class_to_gql = {
        table.sqlalchemy_cls: gql_objects[table.graphql_name] for table in tables
    }
    _validate_relationships(tables, class_to_gql)

    # Step 2 — populate fields (columns + relationships)
    for table in tables:
        gql_objects[table.graphql_name]._fields = lambda t=table: _build_fields(  # type: ignore
            t, class_to_gql, scalar_map
        )

    # Step 3 — build query arguments with filters, pagination, ordering
    query_fields = {}

    for table in tables:
        base_object = gql_objects[table.graphql_name]

        filter_fields = {}
        for col in table.inspected.columns:
            if col.key not in table.filter_fields:
                continue

            py_type = col.type.python_type

            # reuse filter input if already built
            if py_type in filter_map:
                gql_filter = filter_map[py_type]
            else:
                # pick FILTERS builder
                if py_type in FILTERS:
                    key = py_type
                else:
                    key = next(it for it in FILTERS.keys() if issubclass(py_type, it))

                gql_type = scalar_map.get(py_type)
                if gql_type is None:
                    gql_type = convert_to_scalar(col)
                    scalar_map[py_type] = gql_type

                gql_filter = FILTERS[key](gql_type)  # type: ignore
                filter_map[py_type] = gql_filter

            filter_fields[col.key] = gql_filter

        # Build query arguments
        args = {}
        if filter_fields:
            args["filter"] = GraphQLArgument(
                GraphQLInputObjectType(
                    name=f"{table.graphql_name}_filter",
                    fields=lambda f=filter_fields: f,
                )  # type: ignore
            )

        if table.pagination:
            args["limit"] = GraphQLArgument(
                IntScalar, default_value=table.default_limit
            )
            args["offset"] = GraphQLArgument(IntScalar, default_value=0)

        if table.order_fields:
            order_fields = {
                f: GraphQLInputField(OrderingEnumScalar) for f in table.order_fields
            }
            args["order"] = GraphQLArgument(
                GraphQLInputObjectType(
                    name=f"{table.graphql_name}_order", fields=lambda o=order_fields: o
                )  # type: ignore
            )

        # Resolver
        resolver = (
            build_async_resolver(table) if is_async else build_sync_resolver(table)
        )

        # Final query field
        if table.query:
            query_fields[table.graphql_name + "s"] = GraphQLField(
                GraphQLList(base_object), args=args, resolve=resolver
            )

    # Step 4 — Build root query
    query = GraphQLObjectType(name="Query", fields=lambda q=query_fields: q)

    return GraphQLSchema(query=query)  # type: ignore
