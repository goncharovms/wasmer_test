from typing import Optional

import strawberry
from strawberry import Info
from wasmer_app.schema.email_schema import EmailCreatedResponse
from wasmer_app.schema.user_schema import User
from wasmer_app.services.email_service import EmailService
from wasmer_app.services.user_service import UserService


@strawberry.type
class Mutation:

    @strawberry.mutation
    async def upgrade_account(self, _: Info, user_id: strawberry.ID) -> Optional[User]:
        return await UserService.upgrade_account(user_id)

    @strawberry.mutation
    async def downgrade_account(
        self, _: Info, user_id: strawberry.ID
    ) -> Optional[User]:
        return await UserService.downgrade_account(user_id)

    @strawberry.mutation
    async def send_email(
        self, _: Info, app_id: strawberry.ID, to: str, subject: str, html: str
    ) -> Optional[EmailCreatedResponse]:
        return await EmailService.send_email(app_id, to, subject, html)
