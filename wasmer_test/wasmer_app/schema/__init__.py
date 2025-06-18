from django.conf import settings
from django.utils import timezone
from strawberry import Info

from .base_node import PlainTextNode

from wasmer_app.schema.user_schema import User
from wasmer_app.schema.deployed_app_schema import DeployedApp
import strawberry
from typing import Optional

from .email_schema import EmailCreatedResponse
from ..models import Plan
from ..services.email_service import EmailService
from ..services.user_service import UserService

Node = strawberry.union(
    "Node",
    (
        User,
        DeployedApp
    )
)


@strawberry.type
class Query:
    @strawberry.field
    async def node(self, info, id: str) -> Optional[Node]:
        return await PlainTextNode.resolve(id, info)


@strawberry.type
class Mutation:

    @strawberry.mutation
    async def upgrade_account(self, _: Info, user_id: strawberry.ID) -> Optional[User]:
        user = await UserService.get_object(user_id)
        if user.plan == Plan.PRO:
            raise ValueError("Cannot downgrade a user already on the PRO plan.")
        return await UserService.upgrade_user(user)

    @strawberry.mutation
    async def downgrade_account(self, _: Info, user_id: strawberry.ID) -> Optional[User]:
        user = await UserService.get_object(user_id)
        if user.plan == Plan.HOBBY:
            raise ValueError("Cannot downgrade a user already on the HOBBY plan.")
        return await UserService.downgrade_user(user)

    @strawberry.mutation
    async def send_email(self, _: Info, app_id: strawberry.ID, subject: str, html: str) -> Optional[EmailCreatedResponse]:
        user = await UserService.get_by_app_id(app_id)
        if user.plan == Plan.HOBBY:
            period_start_at = max(
                user.plan_changed_at,
                timezone.now() - timezone.timedelta(days=settings.EMAIL_LIMIT_PERIOD)
            )
            emails_count = await EmailService.get_count_per_trial_period(
                user_id=user.id,
                period_start_at=period_start_at
            )
            if emails_count >= settings.EMAIL_LIMIT_COUNT:

                return EmailCreatedResponse(successful=False, message="Email limit reached for hobby plan.")

        await EmailService.create_email(
            app_id=app_id,
            subject=subject,
            html=html
        )
        return EmailCreatedResponse(successful=True)


schema = strawberry.Schema(query=Query, mutation=Mutation)
