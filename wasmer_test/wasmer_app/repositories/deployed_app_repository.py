from wasmer_app.models import DeployedApp
from wasmer_app.repositories.base_repository import BaseRepository


class DeployedAppRepository(BaseRepository):
    model_class = DeployedApp
