from datetime import datetime

from wasmer_app.models import Email
from wasmer_app.services.base_service import BaseService


class EmailService(BaseService):
    model_class = Email

    @classmethod
    async def get_count_per_trial_period(cls, user_id: str, period_start_at:datetime) -> int:
        email_count = await Email.objects.filter(
            deployed_app__owner_id=user_id,
            created_at__gt=period_start_at,
        ).acount()
        return email_count

    @classmethod
    async def create_email(
        cls,
        app_id: str,
        subject: str,
        html: str
    ) -> Email:
        email = Email(
            deployed_app_id=app_id,
            subject=subject,
            html=html
        )
        await email.asave()
        return email
