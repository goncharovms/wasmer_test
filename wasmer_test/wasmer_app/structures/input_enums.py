import enum

import strawberry


@strawberry.enum
class GroupByEnum(enum.Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
