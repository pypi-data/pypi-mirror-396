import logging
import time
from abc import ABC
from typing import Any

from graphql import ExecutionResult, GraphQLSchema, graphql, graphql_sync
from graphql.utilities import print_schema
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Session

from .errors import ConfigurationError
from .models import Order, Table
from .register import register_transform
from .schema import build_gql_schema

log = logging.getLogger("alchemyql")


class AlchemyQL(ABC):
    """
    Alchemy QL Engine Definition.

    An Engine supports adding tables, building Graph QL schema and executing queries.
    """

    def __init__(self, max_query_depth: int | None = None):
        """
        Initialize Alchemy QL Engine.

        Options:
            - max_query_depth - Maximum number of nested relationships that can be queries in 1 query
        """
        self.schema: GraphQLSchema | None = None
        self.tables: list[Table] = []
        self.is_async: bool
        self.max_query_depth = max_query_depth

    def register(
        self,
        sqlalchemy_cls,
        graphql_name: str | None = None,
        description: str | None = None,
        query: bool = True,
        include_fields: list[str] | None = None,
        exclude_fields: list[str] | None = None,
        relationships: list[str] | None = None,
        filter_fields: list[str] | None = None,
        order_fields: list[str] | None = None,
        default_order: dict[str, Order] | None = None,
        pagination: bool = False,
        default_limit: int | None = None,
        max_limit: int | None = None,
    ):
        """
        Register a SQL Alchemy Table into your Alchemy QL engine.

        Options:
         - graphql_name - Name to give GraphQL type (defaults to tablename)
         - description - Description to give GraphQL type
         - query - whether to support direct querying of table
         - include_fields - list of column names to expose
         - exclude_fields - list of column names not to expose
         - relationships - list of relationship names to expose (target table must also be registered before schema is built)
         - filter_fields - list of column names to allow filtering by
         - order_fields - list of column names to allow ordering by
         - default_order - column -> order map to be applied by default
         - pagination - whether to support pagination
         - default_limit - default max number of rows to return
         - max_limit - max limit to allow
        """

        table = register_transform(
            sqlalchemy_cls,
            graphql_name,
            description,
            query,
            include_fields,
            exclude_fields,
            relationships,
            filter_fields,
            order_fields,
            default_order,
            pagination,
            default_limit,
            max_limit,
        )

        # Checks the table is not already registerd
        if any(it.sqlalchemy_cls is sqlalchemy_cls for it in self.tables):
            raise ConfigurationError("Sqlalchemy Table is already registered")

        # Checks the name is not already in use
        if any(it.graphql_name == table.graphql_name for it in self.tables):
            raise ConfigurationError("Table with same Graph QL name already registerd")

        self.tables.append(table)
        log.debug(
            f"Registerd table {table.graphql_name}! (Now {len(self.tables)} tables registered!)"
        )

    def register_all_tables(self, base: type[DeclarativeBase]):
        """
        Register all tables under a DeclarativeBase.

        NOTE: This does not allow any customisations. It will default to use all columns.
        """
        for mapper in base.registry.mappers:
            self.register(mapper.class_)

    def build_schema(self):
        """
        Builds a Graph QL Schema using all registered SQL Alchemy Tables.

        NOTE: This must be run before the AlchemyQL engine can be used
        """
        start = time.perf_counter()

        self.schema = build_gql_schema(self.tables, self.is_async)

        log.debug(
            "Build schema complete! (Time taken: %.6f seconds)",
            time.perf_counter() - start,
        )

    def get_schema(self) -> str:
        """
        Returns the Graph QL Schema in a pretty print str format.
        """
        if not self.schema:
            raise ConfigurationError(
                "Schema is not setup yet. You must run 'build_schema()' first"
            )
        return print_schema(self.schema)


class AlchemyQLSync(AlchemyQL):
    def __init__(self, max_query_depth: int | None = None, *args, **kwargs):
        super().__init__(max_query_depth=max_query_depth, *args, **kwargs)
        self.is_async = False

    def execute_query(
        self,
        query: str,
        db_session: Session,
        variables: dict[str, Any] | None = None,
        operation: str | None = None,
    ) -> ExecutionResult:
        """
        Executes a Graph QL query on the Alchemy QL engine.
        """
        if not self.schema:
            raise ConfigurationError(
                "Schema is not setup yet. You must run 'build_schema()' first"
            )

        start = time.perf_counter()

        result = graphql_sync(
            self.schema,
            query,
            variable_values=variables,
            operation_name=operation,
            context_value={
                "session": db_session,
                "max_query_depth": self.max_query_depth,
            },
        )

        log.debug(
            "Query execution complete! (Time taken: %.6f seconds)",
            time.perf_counter() - start,
        )

        return result


class AlchemyQLAsync(AlchemyQL):
    def __init__(self, max_query_depth: int | None = None, *args, **kwargs):
        super().__init__(max_query_depth=max_query_depth, *args, **kwargs)
        self.is_async = True

    async def execute_query(
        self,
        query: str,
        db_session: AsyncSession,
        variables: dict[str, Any] | None = None,
        operation: str | None = None,
    ) -> ExecutionResult:
        """
        Executes a Graph QL query on the Alchemy QL engine.
        """
        if not self.schema:
            raise ConfigurationError(
                "Schema is not setup yet. You must run 'build_schema()' first"
            )

        start = time.perf_counter()

        result = await graphql(
            self.schema,
            query,
            variable_values=variables,
            operation_name=operation,
            context_value={
                "session": db_session,
                "max_query_depth": self.max_query_depth,
            },
        )

        log.debug(
            "Query execution complete! (Time taken: %.6f seconds)",
            time.perf_counter() - start,
        )

        return result
