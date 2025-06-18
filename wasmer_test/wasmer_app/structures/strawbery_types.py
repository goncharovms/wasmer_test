from datetime import datetime

import strawberry


@strawberry.type
class EmailUsageSummary:
    total: int
    sent: int
    failed: int
    read: int


@strawberry.type
class EmailUsageGrouped:
    timestamp: datetime
    emails: EmailUsageSummary


@strawberry.input
class TimeWindow:
    start: datetime
    end: datetime
