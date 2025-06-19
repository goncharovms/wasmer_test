from wasmer_app.models import ProviderCredential, DeployedApp
from wasmer_app.services.base_repository import BaseRepository


class ProviderCredentialsRepository(BaseRepository):
    model_class = ProviderCredential

    @classmethod
    async def get_by_app(cls, deployed_app: DeployedApp) -> ProviderCredential:
        credentials = await ProviderCredential.objects.filter(user_id=deployed_app.owner_id, is_active=True).aget()
        if not credentials:
            raise ValueError(
                f"No active credentials found for user {deployed_app.owner_id} associated with app {deployed_app.id}"
            )
        return credentials