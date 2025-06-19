from typing import Optional

import strawberry
from wasmer_app.schema.base_node import PlainTextNode
from wasmer_app.schema.deployed_app_schema import DeployedApp
from wasmer_app.schema.user_schema import User

Node = strawberry.union("Node", (User, DeployedApp))


@strawberry.type
class Query:
    @strawberry.field
    async def node(self, info, id: str) -> Optional[Node]:
        return await PlainTextNode.resolve(id, info)
