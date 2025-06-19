from typing import Optional

import strawberry
from strawberry.scalars import JSON
from wasmer_app.repositories.credentials_repository import ProviderCredentialsRepository
from wasmer_app.repositories.deployed_app_repository import DeployedAppRepository
from wasmer_app.schema.base_node import PlainTextNode
from wasmer_app.schema.deployed_app_schema import DeployedApp
from wasmer_app.schema.user_schema import User

Node = strawberry.union("Node", (User, DeployedApp))


@strawberry.type
class Query:
    @strawberry.field
    async def node(self, info, id: str) -> Optional[Node]:
        return await PlainTextNode.resolve(id, info)

    @strawberry.field
    async def get_SMTP_credentials(self, info, app_id: strawberry.ID) -> Optional[JSON]:
        app = await DeployedAppRepository.get_object(app_id)
        creds = await ProviderCredentialsRepository.get_by_app(app)
        if not creds:
            return None
        return creds.credentials
