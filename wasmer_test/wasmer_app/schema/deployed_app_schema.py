import strawberry_django
from strawberry import ID, auto
from wasmer_app.models import DeployedApp as DeployedApp_

from wasmer_app.schema import PlainTextNode
from wasmer_app.services.deployed_app_service import DeployedAppService


@strawberry_django.type(DeployedApp_, name="DeployedApp")
@PlainTextNode.register_type('app')
class DeployedApp(PlainTextNode):
    id: ID
    active: auto

    @classmethod
    async def resolve_node(cls, node_id):
        return await DeployedAppService.get_object(node_id)
