from wasmer_app.models import DeployedApp
from wasmer_app.services.base_repository import BaseRepository


class DeployedAppRepository(BaseRepository):
    model_class = DeployedApp
