import inspect
import sys
from types import GenericAlias
from typing import Callable, Dict

import strawberry
import strawberry.tools
import strawberry.utils
import strawberry.utils.typing
from fastapi import Request, Response
from graphql.error import GraphQLError
from graphql.error.graphql_error import format_error as format_graphql_error
from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.asyncio import AsyncEngine
from strawberry.fastapi import GraphQLRouter
from strawberry.http import GraphQLHTTPResponse
from strawberry.types import ExecutionResult

from .dl import GraphemyDataLoader
from .schemas.generators import (
    get_query,
    set_schema,
    get_mutations
)
from .setup import Setup


async def fake_dl_one(keys):
    """
    A placeholder asynchronous function that simulates fetching single items for each key.
    Args:
        keys (iterable): A collection of keys for which data needs to be fetched.
    Returns:
        An iterable of None values corresponding to each key.
    """
    return {k: None for k in keys}.values()


async def fake_dl_list(keys):
    """
    A placeholder asynchronous function that simulates fetching lists of items for each key.
    Args:
        keys (iterable): A collection of keys for which data needs to be fetched.
    Returns:
        An iterable of empty lists corresponding to each key.
    """
    return {k: [] for k in keys}.values()


def genre_empty_query():
    class Query:
        """
        A class used as a container for defining GraphQL queries. All the resolvers associated
        with fetching data are attached to instances of this class or its subclasses.
        """

        pass

    return Query


def genre_empty_mutation():
    class Mutation:
        __auto_generated__ = True
        """
        A class used as a container for defining GraphQL mutations. It contains methods that
        alter data state in the database, typically involving create, update, and delete operations.
        """

        pass

    return Mutation


async def hello_world(self, info) -> str:
    """
    A simple resolver function returning a greeting message.
    Returns:
        A string greeting 'Hello World'.
    """
    return "Hello World"


class GraphemyRouter(GraphQLRouter):
    """
    A custom router class that sets up a GraphQL API using schemas generated from SQLModel classes.
    It handles dynamic query and mutation generation, permissions, and context setup for each request.

    Args:
        query (object): A class containing GraphQL query resolvers.
        mutation (object): A class containing GraphQL mutation resolvers.
        context_getter (Callable): A function to get additional context for each request.
        permission_getter (Callable): A function to determine permissions for operations.
        dl_filter (Callable): A function to apply filters to data loaders.
        query_filter (Callable): A function to apply filters to queries.
        engine (Engine | Dict[str, Engine]): Database engine(s) used for SQL operations.
        extensions (list): List of Strawberry extensions to be applied to the schema.
        enable_queries (bool): Flag to enable query generation.
        enable_put_mutations (bool): Flag to enable PUT mutations.
        enable_delete_mutations (bool): Flag to enable DELETE mutations.
        auto_foreign_keys (bool): Flag to automatically handle foreign keys.
        **kwargs: Additional keyword arguments passed to the base GraphQLRouter.
    """

    functions = []

    def __init__(
        self,
        query: object | None = None,
        mutation: object | None = None,
        context_session: Callable | None = None,
        context_getter: Callable | None = None,
        permission_getter: Callable | None = None,
        dl_filter: Callable | None = None,
        query_filter: Callable | None = None,
        engine: AsyncEngine | Engine | Dict[str, Engine] = None,
        extensions: list = None,
        enable_queries: bool = True,
        enable_put_mutations: bool = False,
        enable_delete_mutations: bool = False,
        auto_foreign_keys: bool = False,
        enable_federation_2: bool = False,
        **kwargs,
    ):
        if not query:
            query = genre_empty_query()
        if not mutation:
            mutation = genre_empty_mutation()
        if not extensions:
            extensions = []
        functions: Dict[str, tuple] = {}
        Setup.setup(
            engine=engine,
            permission_getter=permission_getter,
            query_filter=query_filter,
        )
        need_query = True
        need_mutation = True
        for cls in Setup.classes.values():
            set_schema(cls, functions, auto_foreign_keys)
            if cls.__enable_query__ == None:
                cls.__enable_query__ = enable_queries
            if cls.__enable_put_mutation__ == None:
                cls.__enable_put_mutation__ = enable_put_mutations
            if cls.__enable_delete_mutation__ == None:
                cls.__enable_delete_mutation__ = enable_delete_mutations
            cls_query, cls_filter = get_query(cls)
            setattr(
                sys.modules[__name__],
                cls.__name__,
                cls.__strawberry_schema__,
            )
            setattr(
                sys.modules[__name__],
                cls.__name__ + "Filter",
                cls_filter,
            )
            if cls.__enable_query__:
                need_query = False

                def model_query_resolver() -> cls_query:
                    return cls_query()  # return an instance of the ModelQuery type

                # Create a Strawberry field for this query
                query_field = strawberry.field(description=f"Queries for {cls.__queryname__}")(model_query_resolver)

                setattr(query, cls.__queryname__, query_field)

            cls_mutations = get_mutations(cls)
            # model_mutation_fields = {}
            if cls_mutations:
                # Create a resolver that returns an instance of ModelMutations
                def make_mutation_resolver(mutations):
                    def resolver() -> mutations:
                        return mutations()

                    return resolver

                resolver = make_mutation_resolver(cls_mutations)

                # Create a Strawberry field for this query
                mutation_field = strawberry.field(description=f"Mutations for {cls.__queryname__}")(resolver)

                need_mutation = False
                setattr(mutation, cls.__queryname__, mutation_field)
        if need_query:
            setattr(
                query,
                "hello_world",
                strawberry.field(hello_world),
            )

        async def get_context(request: Request, response: Response) -> dict:
            context = {}
            if getattr(request, "state") and getattr(request.state, "db"):
                session = request.state.db
                context = {"engine": engine, "session": session}

            if context_getter:
                context = await context_getter(request, response, context)
            for k, (func, return_class) in functions.items():
                context[k] = GraphemyDataLoader(
                    load_fn=(
                        func
                        if await Setup.permission_getter(return_class, context, "query")
                        else (
                            fake_dl_list
                            if type(inspect.signature(func).return_annotation)
                            == GenericAlias
                            else fake_dl_one
                        )
                    ),
                    filter_method=dl_filter,
                    context=context,
                )
            return context
        if enable_federation_2:
            schema = strawberry.federation.Schema(
                query=strawberry.type(query),
                mutation=(
                    None
                    if need_mutation and hasattr(mutation, "__auto_generated__")
                    else strawberry.type(mutation)
                ),
                extensions=extensions,
                enable_federation_2=True
            )
        else:
            schema = strawberry.Schema(
                query=strawberry.type(query),
                mutation=(
                    None
                    if need_mutation and hasattr(mutation, "__auto_generated__")
                    else strawberry.type(mutation)
                ),
                extensions=extensions,
            )
        super().__init__(schema=schema, context_getter=get_context, **kwargs)

    async def process_result(
        self, request: Request, result: ExecutionResult
    ) -> GraphQLHTTPResponse:
        """
        Processes the GraphQL execution result, formatting errors and managing permissions.
        Args:
            request (Request): The incoming HTTP request.
            result (ExecutionResult): The result from executing a GraphQL operation.
        Returns:
            GraphQLHTTPResponse: The formatted response to be returned to the client.
        """
        data: GraphQLHTTPResponse = {"data": result.data}
        errors = []
        if "errors" in request.scope:
            errors.append(
                format_graphql_error(
                    GraphQLError(
                        "User don't have necessary permissions for this path",
                        path=[c.__tablename__ for c in request.scope["errors"]],
                    )
                )
            )
        if result.errors:
            errors.extend([format_graphql_error(err) for err in result.errors])
        if len(errors) > 0:
            data["errors"] = errors
        return data
