import strawberry_django
from strawberry import ID, auto

from wasmer_app.schema import PlainTextNode
from wasmer_app.models import User as User_
from wasmer_app.services.user_service import UserService


@strawberry_django.type(User_, name="User")
@PlainTextNode.register_type('u')
class User(PlainTextNode):
    id: ID
    username: auto
    plan: auto

    @classmethod
    async def resolve_node(cls, node_id: str):
        return await UserService.get_object(node_id)
