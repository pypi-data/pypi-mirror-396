from sqlalchemy.sql import Select
from typing import (
    TYPE_CHECKING,
    Annotated,
    Callable,
    Dict,
    Tuple,
    TypeVar,
    Union,
    get_args,
    get_origin,
    Type
)
import base64
from sqlalchemy.dialects.postgresql import array
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKeyConstraint, func
from sqlalchemy.inspection import inspect
from strawberry.federation.schema_directives import Shareable
from strawberry.tools import merge_types
from strawberry.types.field import StrawberryField
from .models import OrderBy, OrderByInput
from ..database.operations import delete_item, get_items, put_item
from ..dl import Dl, ManyRelation



if TYPE_CHECKING:
    from ..models import Graphemy

T = TypeVar("T")

class GraphemyFilterMode:
    EXACT = "EXACT"
    CONTAINS = "CONTAINS"
    STARTSWITH = "STARTSWITH"
    ENDSWITH = "ENDSWITH"
    IN = "IN"
    IN_STRING_ARRAY = "IN_STRING_ARRAY"
    CUSTOM_FILTER_BUILDER = "CUSTOM_FILTER_BUILDER"



from sqlalchemy import text

def process_order_by(cls, orderBy, stmt):
    """
    Process the orderBy parameter and return the order column and a statement with ordering applied.
    
    Args:
        cls: The model class
        orderBy: Either a string column name, an OrderByInput instance, or a list of OrderByInput instances
        
    Returns:
        Tuple of (primary_order_column, stmt_with_ordering_applied)
    """
    # --------------------------------------------------------------
    # HIDDEN ORDERING RULE
    # If the model class defines a hidden raw SQL ordering rule, apply it
    # at the end to ensure it remains last in the ORDER BY clause.
    # --------------------------------------------------------------
    hidden_order_clause = cls.__sql_preset_order_by__
    if hidden_order_clause:
        stmt = stmt.order_by(text(hidden_order_clause))

    # If explicit "orderBy" is provided as a list of OrderByInput
    if isinstance(orderBy, list) and orderBy:
        primary_order = orderBy[0]  # First one is the primary for cursors
        primary_order_column = getattr(cls, primary_order.field)
        
        # Apply all user-defined orderings
        for order_item in orderBy:
            col = getattr(cls, order_item.field)
            if order_item.direction == OrderBy.DESC:
                stmt = stmt.order_by(col.desc())
            else:
                stmt = stmt.order_by(col.asc())
    
    else:
        # Fall back to default ordering from the model
        default_order_by = getattr(cls, "__default_order_by__", None)
        if not default_order_by:
            raise Exception(f"No orderBy specified and no default on {cls.__name__}")

        if isinstance(default_order_by, dict):
            # Use the first key as the primary order column for cursors
            column_name = next(iter(default_order_by))
            direction = default_order_by[column_name]
            primary_order_column = getattr(cls, column_name)

            # Apply all default orderings to the statement
            for col_name, dir_value in default_order_by.items():
                col = getattr(cls, col_name)
                if dir_value == "DESC":
                    stmt = stmt.order_by(col.desc())
                else:
                    stmt = stmt.order_by(col.asc())
        else:
            raise Exception(f"Invalid default_order_by on {cls.__name__}: {default_order_by}")

    return primary_order_column, stmt


def set_schema(
        cls: "Graphemy",
        functions: Dict[str, Tuple[Callable, "Graphemy"]],
        auto_foreign_keys,
) -> None:
    """Set the Strawberry schema for a Graphemy class."""

    # Define a class to hold Strawberry schema fields
    class Schema:
        pass

    foreign_keys_info = []
    for attr in [attr for attr in cls.__dict__.values() if hasattr(attr, "dl")]:
        returned_class: "Graphemy" = Setup.classes[attr.dl]
        setattr(
            Schema,
            attr.__name__,
            strawberry.field(
                attr,
                permission_classes=[
                    Setup.get_auth(
                        returned_class,
                        "query",
                    )
                ],
            ),
        )
        if attr.foreign_key or (
                attr.foreign_key == None and auto_foreign_keys and not attr.many
        ):
            source = attr.source if isinstance(attr.source, list) else [attr.source]
            target = attr.target if isinstance(attr.target, list) else [attr.target]
            target = [returned_class.__tablename__ + "." + t for t in target]

            if (
                    len(source) > 0
                    and len(target) > 0
                    and not any(
                isinstance(item, int)
                or (isinstance(item, str) and item.startswith("_"))
                for item in source + target
            )
            ):
                cls.__table__.append_constraint(ForeignKeyConstraint(source, target))
                foreign_keys_info.append((source, target))
        if not attr.dl_name in functions:
            functions[attr.dl_name] = (
                get_dl_field(attr, returned_class),
                returned_class,
            )
    if cls.__custom_resolvers__:
        for custom_resolver in cls.__custom_resolvers__:
            setattr(Schema, custom_resolver.__name__, strawberry.field(
                resolver=custom_resolver
            ))

    directives = cls.__directives__ if cls.__directives__ else []
    if not cls.__strawberry_schema__:
        extra_schema = strawberry.type(cls.Strawberry, name=f"{cls.__name__}")

        strawberry_schema = strawberry.experimental.pydantic.type(
            cls, all_fields=True, name=cls.__name__, directives=directives
        )(Schema)
        if extra_schema.__annotations__:
            strawberry_schema = merge_types(
                cls.__name__, (strawberry_schema, extra_schema)
            )
        if hasattr(cls, "resolve_reference"):
            setattr(strawberry_schema, "resolve_reference", cls.resolve_reference)
        cls.__strawberry_schema__ = strawberry_schema


def get_dl_field(attr, returned_class: "Graphemy") -> callable:
    returned_schema = returned_class.__strawberry_schema__
    if attr.many:
        returned_schema = Optional[list[returned_schema]]
    else:
        returned_schema = Optional[returned_schema]

    async def dataloader(
            keys: list[tuple],
    ) -> returned_schema:
        return await get_items(returned_class, keys, attr.target, attr.many)

    dataloader.__name__ = attr.dl_name
    return dataloader

def get_many_relation_function(
        field_name: str,
        field_type: T,
        field_value: ManyRelation,
        source_model: Type["Graphemy"]
) -> Callable[[], Union["Graphemy", list["Graphemy"]]]:
    """Generates a DataLoader function dynamically based on the field's specifications."""
    # Determine if the field_type is a list and extract the inner type
    is_list = get_origin(field_type) == list
    class_type = get_args(field_type)[0] if is_list else field_type

    cls = field_value.response_class

    # return get_query()

    # Formulate DataLoader name with consideration for lazy-loaded types
    dl_name = (
        field_value.target
        if isinstance(field_value.target, str)
        else "_".join(field_value.target)
    )
    dl_name = f"dl_{class_type}_{dl_name}"

    # Define the return type using Strawberry's lazy type resolution
    return_type = Annotated[
        f"{class_type}",
        strawberry.lazy("bootgraph.router"),
    ]
    if is_list:
        return_type = CountableConnection[return_type]
    else:
        raise Exception("ManyRelation can not resolve one")


    async def loader_func(
            self,
            info: "Info",
            first: Optional[int] = None,
            after: Optional[str] = None,
            last: Optional[int] = None,
            before: Optional[str] = None,
            filters: (
                    Annotated[
                        f"{class_type}Filter",
                        strawberry.lazy("bootgraph.router"),
                    ]
                    | None
            ) = None,
            orderBy: Optional[list[OrderByInput]] = None,
    ) -> return_type:
        # Check permissions asynchronously
        if not await Setup.has_permission(cls, info.context, "query"):
            # Return empty connection if no permission
            return convert_to_countable_connection([], first, after, last, before, return_type)

        # Obtain the engine for this model
        engine = Setup.engine[cls.__enginename__]

        relation_class = field_value.relation_class
        source_field = getattr(source_model, field_value.source)  # e.g., Shop.id
        source_relation_field = getattr(relation_class, field_value.source_relation)  # e.g., ReviewShop.shop_id
        target_field = getattr(cls, field_value.target)  # e.g., Review.id
        target_relation_field = getattr(relation_class, field_value.target_relation)  # e.g., Review.review_id

        # We have three models
        # cls - Review with id field
        # source_model - Shop which has field_value.source (e.g., id field)
        # relation_class - ReviewShop which has field_value.target (e.g., shop_id and review_id)

        source_value = (
            [
                (
                    attr
                    if type(attr) == int
                    else attr[1:] if attr.startswith("_") else getattr(self, attr)
                )
                for attr in field_value.source
            ]
            if isinstance(field_value.source, list)
            else getattr(self, field_value.source)
        )

        stmt = (
            select(cls)
            .join(relation_class, target_relation_field == target_field)
            .join(source_model, source_field == source_relation_field)
            .filter(source_field == source_value)
        )
        count_stmt = (select(func.count())
            .join(relation_class, target_relation_field == target_field)
            .join(source_model, source_field == source_relation_field)
            .filter(source_field == source_value).select_from(cls))

        # Apply filters if provided
        stmt, count_stmt = apply_filters(stmt, count_stmt, cls, filters)

        # Apply any additional query filters defined by Setup
        qf = Setup.query_filter(cls, info.context)
        if qf and callable(qf):
            stmt = qf(stmt)
            count_stmt = qf(count_stmt)

        # Determine ordering
        order_column, stmt = process_order_by(cls, orderBy, stmt)

        # Handle pagination cursors: decode them and apply filters
        # We assume the cursors are encoded in a way that allows retrieval of the order_column value.
        # decode_cursor returns something like: {"order_value": ..., "id": ...}
        after_value = decode_cursor(after) if after else None
        before_value = decode_cursor(before) if before else None

        # Apply 'after' cursor filter: we want all rows strictly greater than the after_value
        if after_value is not None:
            # TODO: if we need more filters, we need to prccess them here
            after_cursor_value = after_value["o"]
            stmt = stmt.filter(order_column > after_cursor_value)

        # Apply 'before' cursor filter: we want all rows strictly less than the before_value
        if before_value is not None:
            before_cursor_value = before_value["o"]
            stmt = stmt.filter(order_column < before_cursor_value)

        # Apply limit based on `first` or `last`
        # If using forward pagination:
        if first is not None:
            stmt = stmt.limit(first + 1)  # Fetch one extra to determine if there's a next page

        # If using backward pagination (via `last`), you may need to reverse the order, fetch `last + 1` items,
        # then reverse results in memory. For simplicity:
        # If last is used, re-order descending, limit last + 1, then post-process.
        # This is a simplistic approach; a robust approach requires careful logic.
        if last is not None and before is not None:
            stmt = stmt.order_by(order_column.desc()).limit(last + 1)

        # Execute query depending on sync or async engine
        if Setup.async_engine:
            async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
            async with async_session() as session:
                total_count = (await session.execute(count_stmt)).scalar()
                results = (await session.execute(stmt)).scalars().all()
        else:
            with Session(engine) as session:
                total_count = session.execute(count_stmt).scalar()
                results = session.execute(stmt).scalars().all()

        # If last pagination was requested, reverse the results back to original order
        # (because we fetched them in descending order)
        if last is not None and before is not None:
            results = list(reversed(results))

        # Convert results to a countable connection structure
        # `convert_to_countable_connection` should handle encoding the cursors for next and previous pages.
        connection = convert_to_countable_connection(
            results,
            first,
            after,
            last,
            before,
            return_type,
            filters=filters,
            total_count=total_count
        )

        return connection

    # Customize the function attributes for introspection or other purposes
    loader_func.__name__ = field_name
    loader_func.dl = class_type
    loader_func.many = is_list
    loader_func.target = field_value.target
    loader_func.source = field_value.source
    loader_func.foreign_key = field_value.foreign_key
    loader_func.dl_name = dl_name

    return loader_func


def get_dl_function(
        field_name: str,
        field_type: T,
        field_value: Dl,
) -> Callable[[], Union["Graphemy", list["Graphemy"]]]:
    """Generates a DataLoader function dynamically based on the field's specifications."""
    # Determine if the field_type is a list and extract the inner type
    is_list = get_origin(field_type) == list
    class_type = get_args(field_type)[0] if is_list else field_type

    # Formulate DataLoader name with consideration for lazy-loaded types
    dl_name = (
        field_value.target
        if isinstance(field_value.target, str)
        else "_".join(field_value.target)
    )
    dl_name = f"dl_{class_type}_{dl_name}"

    # Define the return type using Strawberry's lazy type resolution
    return_type = Annotated[
        f"{class_type}" if not field_value.return_class else field_value.return_class,
        strawberry.lazy("bootgraph.router"),
    ]
    if is_list:
        return_type = Optional[list[return_type]]
    else:
        return_type = Optional[return_type]

    async def loader_func(
        self,
        info: Info,
        filters: (
            Annotated[
                f"{class_type}Filter",
                strawberry.lazy("bootgraph.router"),
            ]
            | None
        ) = None,
    ) -> return_type:
        """The dynamically generated DataLoader function."""
        filter_args = vars(filters) if filters else None
        source_value = (
            [
                (
                    attr
                    if type(attr) == int
                    else attr[1:] if attr.startswith("_") else getattr(self, attr)
                )
                for attr in field_value.source
            ]
            if isinstance(field_value.source, list)
            else getattr(self, field_value.source)
        )
        resp = await info.context[dl_name].load(source_value, {"filters": filter_args})
        if field_value.extract_from_nested_dl:
            if isinstance(resp, list):
                # If the response is a list, apply getattr to each item
                not_null_response = []
                for item in resp:
                    loaded_item = await getattr(item, field_value.extract_from_nested_dl)(info)
                    if loaded_item:
                        not_null_response.append(loaded_item)
                return not_null_response
            else:
                # Single object
                return await getattr(resp, field_value.extract_from_nested_dl)(info)
        return resp

    # Customize the function attributes for introspection or other purposes
    loader_func.__name__ = field_name
    loader_func.dl = class_type
    loader_func.many = is_list
    loader_func.target = field_value.target
    loader_func.source = field_value.source
    loader_func.foreign_key = field_value.foreign_key
    loader_func.dl_name = dl_name

    return loader_func


from typing import Tuple, Optional, List, Any, Dict, Type
from sqlalchemy.orm import Session
from strawberry.types import Info
from sqlmodel import SQLModel, select
from ..setup import Setup
from sqlalchemy import inspect


def get_pk_name(model_cls) -> str:
    """
    Return the name of the *single* primary key column
    for the given model_cls. Raises ValueError for multi-column PKs.
    """
    mapper = inspect(model_cls)
    pk_attrs = mapper.primary_key

    if len(pk_attrs) != 1:
        raise ValueError(
            f"Model {model_cls.__name__} has {len(pk_attrs)} primary key columns; "
            "multi-column PK not supported here."
        )

    # pk_attrs[0].key should be the attribute name
    # (e.g. "id" or "some_other_primary_key") on the SQLAlchemy model.
    return pk_attrs[0].key


def apply_filters(
        stmt: Select,
        count_stmt: Optional[Select],
        cls,
        filter_obj: Optional["Filter"]
) -> Tuple[Select, Optional[Select]]:
    """
    Apply filters from `filter_obj` (if provided) to both `stmt` and `count_stmt`.
    If `count_stmt` is None, only `stmt` is updated.
    Returns: (updated_stmt, updated_count_stmt)
    """
    if not filter_obj:
        # If no filter_obj given, continue with the existing statements.
        # But we still want to check hidden filtering.
        pass
    else:

        declared_filters = getattr(cls, "__filter_attributes__", {})

        # Loop over all fields in the filter object
        for key, value in vars(filter_obj).items():
            if value is None or key not in declared_filters:
                continue

            cfg = declared_filters[key]
            mode = cfg.get("mode", GraphemyFilterMode.EXACT)

            join_model = cfg.get("join_model")
            join_source_col = cfg.get("join_source_col")
            join_target_col = cfg.get("join_target_col")

            # If there's a join, handle that first
            if join_model and join_source_col and join_target_col:
                pk_name = get_pk_name(cls)
                # Example: stmt = stmt.join(join_model, join_model.shop_id == cls.id)
                stmt = stmt.join(
                    join_model,
                    getattr(join_model, join_source_col) == getattr(cls, pk_name)
                )
                if count_stmt is not None:
                    count_stmt = count_stmt.join(
                        join_model,
                        getattr(join_model, join_source_col) == getattr(cls, pk_name)
                    )

                if mode == GraphemyFilterMode.IN:
                    stmt = stmt.where(getattr(join_model, join_target_col).in_(value))
                    if count_stmt is not None:
                        count_stmt = count_stmt.where(getattr(join_model, join_target_col).in_(value))
                # If you have other modes you want to handle with a join, handle them here.
                continue

            # No join => normal column filtering
            column = getattr(cls, key, None)

            if mode == GraphemyFilterMode.EXACT:
                if isinstance(value, str):
                    stmt = stmt.filter(column.ilike(value))
                    if count_stmt is not None:
                        count_stmt = count_stmt.filter(column.ilike(value))
                else:
                    stmt = stmt.filter(column == value)
                    if count_stmt is not None:
                        count_stmt = count_stmt.filter(column == value)

            elif mode == GraphemyFilterMode.CONTAINS:
                stmt = stmt.filter(column.ilike(f"%{value}%"))
                if count_stmt is not None:
                    count_stmt = count_stmt.filter(column.ilike(f"%{value}%"))

            elif mode == GraphemyFilterMode.STARTSWITH:
                stmt = stmt.filter(column.ilike(f"{value}%"))
                if count_stmt is not None:
                    count_stmt = count_stmt.filter(column.ilike(f"{value}%"))

            elif mode == GraphemyFilterMode.ENDSWITH:
                stmt = stmt.filter(column.ilike(f"%{value}"))
                if count_stmt is not None:
                    count_stmt = count_stmt.filter(column.ilike(f"%{value}"))

            elif mode == GraphemyFilterMode.IN:
                stmt = stmt.where(column.in_(value))
                if count_stmt is not None:
                    count_stmt = count_stmt.where(column.in_(value))

            elif mode == GraphemyFilterMode.IN_STRING_ARRAY:
                # Example for Postgres: check if array fields overlap
                stmt = stmt.where(
                    func.string_to_array(column, ",").op("&&")(func.array(value))
                )
                if count_stmt is not None:
                    count_stmt = count_stmt.where(
                        func.string_to_array(column, ",").op("&&")(func.array(value))
                    )

            elif mode == GraphemyFilterMode.CUSTOM_FILTER_BUILDER:
                filter_builder = cfg.get("filter_builder")
                if callable(filter_builder):
                    stmt, count_stmt = filter_builder(stmt, count_stmt, value, cls, key)
    
    # ----------------------------------------------------------------
    # HIDDEN FILTERING LOGIC
    # If the model class defines a hidden raw SQL filter condition,
    # apply it at the end so it's always enforced.
    # ----------------------------------------------------------------
    hidden_filter = getattr(cls, "__sql_preset_filter__", None)
    if hidden_filter:
        stmt = stmt.where(text(hidden_filter))
        if count_stmt is not None:
            count_stmt = count_stmt.where(text(hidden_filter))

    return stmt, count_stmt


async def get_one(cls: Type[SQLModel], filter_obj: Any, query_filter: callable = None):
    """
    Retrieve a single item from the database according to the fields in `filter_obj`.
    We assume `filter_obj` is a dict of {field_name: value} pairs for filtering.
    """
    engine = Setup.engine[cls.__enginename__]
    stmt = select(cls)

    # Apply filters from filter_obj if provided
    stmt, _ = apply_filters(stmt, None, cls, filter_obj)

    # Apply additional query_filter if provided
    if query_filter and callable(query_filter):
        stmt = query_filter(stmt)

    if Setup.async_engine:
        async_session = sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        async with async_session() as session:
            result = await session.execute(stmt)
            return result.scalars().first()
    else:
        with Session(engine) as session:
            return session.execute(stmt).scalars().first()


def encode_cursor(offset: int) -> str:
    return base64.b64encode(str(offset).encode()).decode()

def decode_cursor(cursor: Optional[str]) -> Optional[int]:
    if cursor is None:
        return None
    try:
        return int(base64.b64decode(cursor).decode())
    except Exception:
        return None


def convert_to_countable_connection(
        results: List[Any],
        first: Optional[int],
        after: Optional[str],
        last: Optional[int],
        before: Optional[str],
        ConnectionClass: Type[Any],
        *,
        start_offset: int = 0,
        filters: Any = None,
        total_count: Optional[int] = None
) -> Any:
    """
    Convert a list of ORM results into a countable connection structure.
    Assumes that `results` has already been fetched with any extra items included
    (one extra item to determine next/previous pages).

    Arguments:
    - results: The fetched list of items (could include one extra for pagination).
    - first, after, last, before: Relay-style pagination arguments.
    - ConnectionClass: The GraphQL connection class to instantiate.
    - order_column: The column used for ordering (e.g., cls.id).
    - filters: Filter conditions used, if needed to reconstruct the context.
    - total_count: If not provided, must be fetched separately. For demonstration,
      assume it's passed in or can be computed here.

    Returns:
    A `ConnectionClass` instance with `edges`, `pageInfo`, and `totalCount`.
    """

    # If total_count not provided, you would need to run a count query here.
    if total_count is None:
        # This is pseudo-logic. In reality, you'd need your model/class context
        # and filters to compute this. For now, assume total_count == len(results)
        # or do a proper COUNT query if you have the session and model class.
        total_count = len(results)

    # Determine if we fetched an extra item for pagination detection.
    extra_fetched = 0
    if first is not None:
        # If we wanted first items, we might have fetched first + 1
        if len(results) > first:
            extra_fetched = len(results) - first
    if last is not None:
        # Similarly, if we wanted last items, we might have fetched last + 1 in reverse.
        if len(results) > last:
            extra_fetched = len(results) - last

    # Adjust results to remove the extra item(s)
    edges_results = results
    if extra_fetched > 0:
        if first is not None:
            # For forward pagination, we keep the first 'first' items
            edges_results = results[:first]
        elif last is not None:
            # For backward pagination, we keep the last 'last' items
            edges_results = results[-last:]

    # Create edges: each edge needs a cursor.
    # We assume each result has a primary key `id` and we used `order_column` for ordering.
    edges = []

    @strawberry.type
    class EdgeClass:
        node: Any
        cursor: str

    for idx, node in enumerate(edges_results):
        cursor = encode_cursor(start_offset + idx)
        edges.append(EdgeClass(node=node, cursor=cursor))

    # Compute pageInfo
    has_next_page = False
    has_previous_page = False

    # Logic for hasNextPage and hasPreviousPage:
    # If we had a limit (first), and we got one extra item initially (not shown in edges_results after trimming),
    # that indicates there is a next page.
    if first is not None and len(results) > first:
        has_next_page = True

    # If we had a limit (last), and we got one extra item initially,
    # that indicates there is a previous page.
    if last is not None and len(results) > last:
        has_previous_page = True

    # If no pagination arguments but total_count > len(edges_results),
    # we could deduce future pages exist. That depends on your logic.
    # For simplicity, rely on the extra item logic above.

    # startCursor and endCursor come from the first and last edges
    start_cursor = edges[0].cursor if edges else None
    end_cursor = edges[-1].cursor if edges else None

    page_info = PageInfo(
        start_cursor=start_cursor,
        end_cursor=end_cursor,
        has_next_page=has_next_page,
        has_previous_page=has_previous_page,
    )
    # Instantiate the connection object. The exact initialization depends on your schema.
    # Assume `CountableConnectionForModel` or `ConnectionClass` takes edges, pageInfo, totalCount.
    connection = ConnectionClass(
        edges=edges,
        pageInfo=page_info,
        totalCount=total_count
    )

    return connection


def create_filter_input(cls: Type[SQLModel], name_suffix="Filter"):
    """
    Dynamically create a Strawberry input type from the __annotations__ of the SQLModel class.
    All fields are optional, allowing flexible filtering.
    """
    declared_filters = getattr(cls, "__filter_attributes__", {})
    if not declared_filters:
        return None

    class FilterInput:
        pass

    internal_type_filters = set()
    for field_name, field_type in cls.__annotations__.items():
        if field_name in declared_filters:
            internal_type_filters.add(field_name)
            if declared_filters[field_name].get("is_list"):
                graphql_type = List[field_type]
            else:
                graphql_type = field_type

            if not declared_filters[field_name].get("required"):
                graphql_type = Optional[graphql_type]
            setattr(
                FilterInput,
                field_name,
                strawberry.field(
                    default=declared_filters[field_name].get("default"), graphql_type=graphql_type,
                    description=declared_filters[field_name].get("description"),
                ),
            )

    # process external field_names
    for field_name in (set(declared_filters.keys()) - internal_type_filters):
        graphql_type = declared_filters[field_name]["type"]
        if declared_filters[field_name].get("is_list"):
            graphql_type = List[graphql_type]
        else:
            graphql_type = graphql_type

        if not declared_filters[field_name].get("required"):
            graphql_type = Optional[graphql_type]
        setattr(
            FilterInput,
            field_name,
            strawberry.field(
                default=declared_filters[field_name].get("default"), graphql_type=graphql_type,
                description=declared_filters[field_name].get("description"),
            ),
        )
    return strawberry.input(name=f"{cls.__name__}{name_suffix}")(FilterInput)


from typing import Generic, TypeVar, List, Optional
import strawberry

# Type variable for node type
T = TypeVar("T")


@strawberry.type
class PageInfo:
    has_next_page: bool = strawberry.field(
        description="When paginating forwards, are there more items?",
        directives=[Shareable()],
    )
    has_previous_page: bool = strawberry.field(
        description="When paginating backwards, are there more items?",
        directives=[Shareable()],
    )
    start_cursor: Optional[str] = strawberry.field(
        description="When paginating backwards, the cursor to continue.",
        directives=[Shareable()],
    )
    end_cursor: Optional[str] = strawberry.field(
        description="When paginating forwards, the cursor to continue.",
        directives=[Shareable()],
    )


@strawberry.type
class Edge(Generic[T]):
    node: T
    cursor: str


@strawberry.type
class CountableConnection(Generic[T]):
    edges: List[Edge[T]]
    pageInfo: PageInfo
    totalCount: int


# ----------------------------------------
# Integration with the refactored get_query code
# ----------------------------------------

def get_query(cls: "Graphemy"):
    # Create the filter input types
    # One-type filters (for unique lookups) might be the same as many filters, or separate if needed.
    # Here we assume one and many queries can use the same filter input.
    Filter = create_filter_input(cls, "Filter")

    async def one_resolver(self, info: Info, filter: Filter) -> Optional[cls.__strawberry_schema__]:
        if not await Setup.has_permission(cls, info.context, "query"):
            return None
        data = await get_one(cls, filter, Setup.query_filter(cls, info.context))
        return data

    CountableConnectionForModel = CountableConnection[cls.__strawberry_schema__]

    async def many_resolver(
            self,
            info: "Info",
            first: Optional[int] = 100,
            after: Optional[str] = None,
            last: Optional[int] = None,
            before: Optional[str] = None,
            filter: Optional[Filter] = None,
            orderBy: Optional[list[OrderByInput]] = None,
    ) -> CountableConnectionForModel:
        # Check permissions asynchronously
        context_with_args = dict(info.context)
        context_with_args["__resolver_args__"] = {
            "first": first,
            "after": after,
            "last": last,
            "before": before,
            "filter": filter,
            "orderBy": orderBy,
        }
        permission_allowed = await Setup.has_permission(cls, context_with_args, "query")
        if not permission_allowed:
            # Return empty connection if no permission
            raise ValueError("NO_PERMISSION")
        
        if first and first > 100 or last and last > 100:
            raise ValueError("first and last must be less than 100")
        

        # Obtain the engine for this model
        engine = Setup.engine[cls.__enginename__]

        # Prepare the base select statement
        stmt = select(cls)
        count_stmt = select(func.count()).select_from(cls)

        stmt, count_stmt = apply_filters(stmt, count_stmt, cls, filter)

        # Apply any additional query filters defined by Setup
        qf = Setup.query_filter(cls, info.context)
        if qf and callable(qf):
            stmt = qf(stmt)
            count_stmt = qf(count_stmt)

        # Determine ordering
        order_column, stmt = process_order_by(cls, orderBy, stmt)

        # Offset based pagination under the hood
        after_offset = decode_cursor(after) if after else None
        before_offset = decode_cursor(before) if before else None

        offset = 0
        limit = first or last or 100

        if after_offset is not None:
            offset = after_offset + 1
        elif before_offset is not None:
            offset = max(before_offset - limit, 0)

        stmt = stmt.offset(offset).limit(limit + 1)

        # Execute query depending on sync or async engine
        if Setup.async_engine:
            async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
            async with async_session() as session:
                results = (await session.execute(stmt)).scalars().all()
                total_count = (await session.execute(count_stmt)).scalar()
        else:
            with Session(engine) as session:
                results = session.execute(stmt).scalars().all()
                total_count = session.execute(count_stmt).scalar()

        # If last pagination was requested, reverse the results back to original order
        # (because we fetched them in descending order)
        if last is not None and before is not None:
            results = list(reversed(results))
            # pass

        # Convert results to a countable connection structure
        # `convert_to_countable_connection` should handle encoding the cursors for next and previous pages.
        connection = convert_to_countable_connection(
            results,
            first,
            after,
            last,
            before,
            CountableConnectionForModel,
            start_offset=offset,
            filters=filter,
            total_count=total_count
        )

        return connection

    one_field = strawberry.field(permission_classes=[Setup.get_auth(cls, "query")])(one_resolver)
    many_field = strawberry.field(permission_classes=[Setup.get_auth(cls, "query")])(many_resolver)

    class ModelQuery:
        one = one_field
        many = many_field

    # Now apply strawberry.type after fields are assigned
    ModelQuery = strawberry.type(name=f"{cls.__name__}Query")(ModelQuery)

    return ModelQuery, Filter



def get_delete_mutation(cls: "Graphemy") -> StrawberryField:
    pk = [pk.name for pk in inspect(cls).primary_key]

    class Filter:
        pass

    for field_name, field in cls.__annotations__.items():
        if field_name in pk:
            setattr(
                Filter,
                field_name,
                strawberry.field(default=None, graphql_type=Optional[field]),
            )
    input = strawberry.input(name=f"{cls.__name__}InputPk")(Filter)

    async def mutation(self, params: input) -> cls.__strawberry_schema__:
        return await delete_item(cls, params, pk)

    return strawberry.mutation(
        mutation,
        permission_classes=[Setup.get_auth(cls, "delete_mutation")],
    )


def create_input_type_for_put(cls: SQLModel):
    """
    Dynamically create a Strawberry input type for the PUT mutation.
    All fields from the model are optional for partial updates.
    """
    fields_dict = {}
    for field_name, field_type in cls.__annotations__.items():
        if get_origin(field_type) == Mapped:
            # Exclude types which can not be transformed to strawberry.input
            # Like sqlalchemy.orm.base.Mapped[typing.List[Any]]
            mapped_type = get_args(field_type)[0]  # Extract the inner type -> typing.List
            if get_origin(mapped_type) == list or get_origin(mapped_type) == List:
                continue
        fields_dict[field_name] = strawberry.field(default=None, graphql_type=Optional[field_type])

    InputType = strawberry.input(
        type(
            f"Put{cls.__name__}Input",
            (object,),
            fields_dict
        )
    )
    return InputType


def create_input_type_for_pk(cls: SQLModel, pk_fields):
    """
    Dynamically create a Strawberry input type that includes only primary key fields.
    Used for DELETE mutations or any operation needing to uniquely identify a record.
    """
    fields_dict = {}
    for field_name, field_type in cls.__annotations__.items():
        if field_name in pk_fields:
            fields_dict[field_name] = strawberry.field(default=None, graphql_type=Optional[field_type])

    PkInputType = strawberry.input(
        type(
            f"Delete{cls.__name__}InputPk",
            (object,),
            fields_dict
        )
    )
    return PkInputType


def get_put_mutation(cls: SQLModel):
    pk = [pk.name for pk in inspect(cls).primary_key]
    Input = create_input_type_for_put(cls)

    @strawberry.mutation(permission_classes=[Setup.get_auth(cls, "mutation")])
    async def putModel(self, info: Info, input: Input) -> cls.__strawberry_schema__:
        # Perform update/insert operation
        return await put_item(cls, input, pk)

    return putModel


def get_delete_mutation(cls: SQLModel):
    pk = [pk.name for pk in inspect(cls).primary_key]
    InputPk = create_input_type_for_pk(cls, pk)

    @strawberry.mutation(permission_classes=[Setup.get_auth(cls, "delete_mutation")])
    async def deleteModel(self, info: Info, input: InputPk) -> Optional[cls.__strawberry_schema__]:
        # Perform delete operation
        return await delete_item(cls, input, pk)

    return deleteModel


def get_mutations(cls: "Graphemy"):
    """
    Combine all model-specific mutations (put, delete) into a single ModelMutations type.
    If the model has put or delete enabled, add those fields.
    """
    fields = {}

    @strawberry.type
    class ModelMutations:
        pass

    if cls.__enable_put_mutation__:
        fields["putModel"] = get_put_mutation(cls)
        setattr(
            ModelMutations,
            "put",
            get_put_mutation(cls),
        )

    if cls.__enable_delete_mutation__:
        fields["deleteModel"] = get_delete_mutation(cls)
        setattr(
            ModelMutations,
            "delete",
            get_delete_mutation(cls),
        )

    if cls.__custom_mutations__:
        for custom_mutation in cls.__custom_mutations__:
            # Fetch the permission classes for this specific mutation
            # If none defined, it defaults to empty (no permissions).
            permission_classes = cls.__mutation_permission_classes__.get(
                custom_mutation.__name__, []
            )
            for permission_class in permission_classes:
                permission_class.item_model = cls

            fields[f"{custom_mutation.__name__}Model"] = strawberry.mutation(
                    resolver=custom_mutation,
                    permission_classes=permission_classes
                )
            setattr(
                ModelMutations,
                custom_mutation.__name__,
                strawberry.mutation(
                    resolver=custom_mutation,
                    permission_classes=permission_classes
                )
            )

    # If no mutations are enabled, return None
    if not fields:
        return None

    ModelMutations = strawberry.type(name=f"{cls.__name__}Mutations")(ModelMutations)
    return ModelMutations