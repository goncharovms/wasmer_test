import strawberry_django
from strawberry import ID, auto
from wasmer_app.models import DeployedApp as DeployedApp_
from wasmer_app.repositories.deployed_app_repository import DeployedAppRepository
from wasmer_app.schema.base_node import PlainTextNode


@strawberry_django.type(DeployedApp_, name="DeployedApp")
@PlainTextNode.register_type("app")
class DeployedApp(PlainTextNode):
    id: ID
    active: auto

    @classmethod
    async def resolve_node(cls, node_id):
        return await DeployedAppRepository.get_object(node_id)
