from wasmer_app.models import DeployedApp
from wasmer_app.services.base_service import BaseService


class DeployedAppService(BaseService):
    model_class = DeployedApp
