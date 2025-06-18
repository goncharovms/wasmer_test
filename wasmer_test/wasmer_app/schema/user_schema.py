from typing import List, Optional

import strawberry
import strawberry_django
from strawberry import ID, auto
from wasmer_app.models import User as User_
from wasmer_app.schema import PlainTextNode
from wasmer_app.services.email_service import EmailService
from wasmer_app.services.user_service import UserService
from wasmer_app.structures.input_enums import GroupByEnum
from wasmer_app.structures.strawbery_types import EmailUsageGrouped, TimeWindow


@strawberry.type
class UserEmails:
    user_id: strawberry.ID

    @strawberry.field
    async def sent_emails_count(self) -> int:
        return await EmailService.get_sent_email_count(str(self.user_id))

    @strawberry.field
    async def usage(
        self,
        group_by: GroupByEnum,
        time_window: Optional[TimeWindow] = None,
    ) -> List[EmailUsageGrouped]:
        return await EmailService.get_usage_summary(
            str(self.user_id), group_by, time_window
        )


@strawberry_django.type(User_, name="User")
@PlainTextNode.register_type("u")
class User(PlainTextNode):
    id: ID
    username: auto
    plan: auto

    @strawberry.field
    def emails(self) -> UserEmails:
        return UserEmails(user_id=self.id)

    @classmethod
    async def resolve_node(cls, node_id: str):
        return await UserService.get_object(node_id)
