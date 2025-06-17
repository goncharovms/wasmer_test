from wasmer_app.models import User, Plan
from wasmer_app.services.base_service import BaseService


class UserService(BaseService):
    model_class = User

    @classmethod
    async def upgrade_user(cls, user_id: str) -> User:
        await User.objects.filter(id=user_id).aupdate(plan=Plan.PRO)
        return await cls.get_object(user_id)

    @classmethod
    async def downgrade_user(cls, user_id: str) -> User:
        await User.objects.filter(id=user_id).aupdate(plan=Plan.HOBBY)
        return await cls.get_object(user_id)