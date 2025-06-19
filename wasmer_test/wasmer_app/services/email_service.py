from dataclasses import dataclass

from django.conf import settings
from django.utils import timezone
from starlette.requests import Request
from wasmer_app.email_providers.email_event_handler import Smtp2GoEmailEventHandler
from wasmer_app.email_providers.email_provider import send_email
from wasmer_app.models import Plan
from wasmer_app.repositories.deployed_app_repository import DeployedAppRepository
from wasmer_app.repositories.email_repository import EmailRepository
from wasmer_app.repositories.user_repository import UserRepository


@dataclass
class SendEmailResponse:
    successful: bool
    message: str = None


class EventHandlerError(Exception):
    pass


class EmailService:
    @staticmethod
    async def send_email(app_id: str, to: str, subject: str, html: str):

        deployed_app = await DeployedAppRepository.get_object(app_id)
        user = await UserRepository.get_object(deployed_app.owner_id)
        if user.plan == Plan.HOBBY:
            period_start_at = max(
                user.plan_changed_at,
                timezone.now() - timezone.timedelta(days=settings.EMAIL_LIMIT_PERIOD),
            )
            emails_count = await EmailRepository.get_count_per_trial_period(
                user_id=user.id, period_start_at=period_start_at
            )
            if emails_count >= settings.EMAIL_LIMIT_COUNT:
                return SendEmailResponse(
                    successful=False, message="Email limit reached for hobby plan."
                )

        email = await EmailRepository.create_email(
            app_id=app_id,
            subject=subject,
            html=html,
            receiver=to,
        )
        await send_email(email, deployed_app)
        return SendEmailResponse(successful=True)

    @staticmethod
    async def process_event_smpt2go(request: Request):
        try:
            data = await request.json()
        except ValueError:
            raise EventHandlerError("Invalid JSON")

        if not isinstance(data, list):
            raise EventHandlerError("Expected a list of events")

        for event in data:
            if not isinstance(event, dict):
                raise EventHandlerError("Each event must be a dictionary")
        for event in data:
            if "message_id" not in event or "status" not in event:
                raise EventHandlerError(
                    "Each event must contain 'message_id' and 'status'"
                )
            await Smtp2GoEmailEventHandler(event).process()
