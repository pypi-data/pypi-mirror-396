from datetime import date
import enum

import strawberry


@strawberry.input
class DateFilter:
    range: list[date | None] | None = None
    items: list[date] | None = None
    year: int | None = None


@strawberry.enum
class OrderBy(str, enum.Enum):
    """
    Enum representing the ordering direction for database queries.
    """
    ASC = "ASC"
    DESC = "DESC"


@strawberry.input
class OrderByInput:
    field: str
    direction: OrderBy = OrderBy.ASC