from strawberry import Info

from .base_node import PlainTextNode

from wasmer_app.schema.user_schema import User
from wasmer_app.schema.deployed_app_schema import DeployedApp
import strawberry
from typing import Optional

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
        return await UserService.upgrade_user(user_id)

    @strawberry.mutation
    async def downgrade_account(self, _: Info, user_id: strawberry.ID) -> Optional[User]:
        return await UserService.downgrade_user(user_id)


schema = strawberry.Schema(query=Query, mutation=Mutation)
