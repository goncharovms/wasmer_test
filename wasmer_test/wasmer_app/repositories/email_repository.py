from datetime import datetime

from django.db.models import Count, Q
from django.db.models.functions import TruncDay, TruncMonth, TruncWeek
from wasmer_app.models import Email, EmailStatus
from wasmer_app.repositories.base_repository import BaseRepository
from wasmer_app.structures.input_enums import GroupByEnum
from wasmer_app.structures.strawbery_types import EmailUsageGrouped, EmailUsageSummary


class EmailRepository(BaseRepository):
    model_class = Email

    @classmethod
    async def get_by_message_id(cls, message_id: str) -> Email:
        return await Email.objects.aget(external_id=message_id)

    @classmethod
    async def get_count_per_trial_period(
        cls, user_id: str, period_start_at: datetime
    ) -> int:
        email_count = await Email.objects.filter(
            deployed_app__owner_id=user_id,
            created_at__gt=period_start_at,
        ).acount()
        return email_count

    @classmethod
    async def create_email(
        cls, app_id: str, subject: str, html: str, receiver: str
    ) -> Email:
        email = Email(
            deployed_app_id=app_id, subject=subject, html=html, receiver=receiver
        )
        await email.asave()
        return email

    @staticmethod
    async def get_sent_email_count(user_id: str) -> int:
        acount_ = await Email.objects.filter(deployed_app__owner_id=user_id).acount()
        return acount_

    @staticmethod
    async def update_email(email: Email, **kwargs) -> Email:
        for key, value in kwargs.items():
            setattr(email, key, value)
        await email.asave()
        return email

    @staticmethod
    async def get_usage_summary(user_id: str, group_by: GroupByEnum, time_window=None):
        trunc_map = {
            GroupByEnum.DAY: TruncDay,
            GroupByEnum.WEEK: TruncWeek,
            GroupByEnum.MONTH: TruncMonth,
        }
        trunc_fn = trunc_map[group_by]

        queryset = Email.objects.filter(deployed_app__owner_id=user_id)

        if time_window:
            queryset = queryset.filter(
                created_at__gte=time_window.start,
                created_at__lte=time_window.end,
            )

        queryset = (
            queryset.annotate(period=trunc_fn("created_at"))
            .values("period")
            .annotate(
                total=Count("id"),
                sent=Count("id", filter=Q(status=EmailStatus.SENT)),
                failed=Count("id", filter=Q(status=EmailStatus.FAILED)),
                read=Count("id", filter=Q(status=EmailStatus.READ)),
            )
            .order_by("period")
        )

        results = []
        async for row in queryset.aiterator():
            results.append(
                EmailUsageGrouped(
                    timestamp=row["period"],
                    emails=EmailUsageSummary(
                        total=row["total"],
                        sent=row["sent"],
                        failed=row["failed"],
                        read=row["read"],
                    ),
                )
            )
        return results
