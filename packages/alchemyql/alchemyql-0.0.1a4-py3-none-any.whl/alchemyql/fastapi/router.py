from typing import Any, Callable

# This might create import errors if fastapi/pydantic are not installed
from fastapi import APIRouter, Depends, Security, status
from pydantic import BaseModel, Field

from ..engine import AlchemyQLAsync, AlchemyQLSync


class GraphQLRequest(BaseModel):
    query: str = Field(..., description="GraphQL query string")
    variables: dict[str, Any] | None = Field(
        None, description="Optional GraphQL variables"
    )
    operationName: str | None = Field(None, description="Optional operation name")


class GraphQLResponse(BaseModel):
    data: Any | None = Field(None, description="GraphQL response payload")
    errors: list[str] | None = Field(
        None, description="List of error messages (if any)"
    )


def create_alchemyql_router_sync(
    engine: AlchemyQLSync,
    db_dependency: Callable,
    auth_dependency: Callable | None = None,
    path="/graphql",
    tags=["GraphQL"],
) -> APIRouter:
    router = APIRouter(tags=tags)

    def auth_helper():
        if auth_dependency:
            return Security(auth_dependency)
        return None

    @router.get(
        path,
        status_code=status.HTTP_200_OK,
        summary="Retrieve GraphQL Schema",
        description="Returns the full GraphQL schema in SDL format.",
    )
    def graphql_schema(_=auth_helper()):
        return engine.get_schema()

    @router.post(
        path,
        status_code=status.HTTP_200_OK,
        summary="Execute GraphQL Query",
        description="Executes a GraphQL query and returns the result.",
    )
    def graphql_execute(
        request: GraphQLRequest, db=Depends(db_dependency), _=auth_helper()
    ) -> GraphQLResponse:
        res = engine.execute_query(
            request.query,
            variables=request.variables,
            operation=request.operationName,
            db_session=db,
        )

        return GraphQLResponse(
            data=res.data,
            errors=[str(err) for err in res.errors] if res.errors else None,
        )

    return router


def create_alchemyql_router_async(
    engine: AlchemyQLAsync,
    db_dependency: Callable,
    auth_dependency: Callable | None = None,
    path="/graphql",
    tags=["GraphQL"],
) -> APIRouter:
    router = APIRouter(tags=tags)

    def auth_helper():
        if auth_dependency:
            return Security(auth_dependency)
        return None

    @router.get(
        path,
        status_code=status.HTTP_200_OK,
        summary="Retrieve GraphQL Schema",
        description="Returns the full GraphQL schema in SDL format.",
    )
    def graphql_schema(_=auth_helper()):
        return engine.get_schema()

    @router.post(
        path,
        status_code=status.HTTP_200_OK,
        summary="Execute GraphQL Query",
        description="Executes a GraphQL query and returns the result.",
    )
    async def graphql_execute(
        request: GraphQLRequest, db=Depends(db_dependency), _=auth_helper()
    ) -> GraphQLResponse:
        res = await engine.execute_query(
            request.query,
            variables=request.variables,
            operation=request.operationName,
            db_session=db,
        )

        return GraphQLResponse(
            data=res.data,
            errors=[str(err) for err in res.errors] if res.errors else None,
        )

    return router
