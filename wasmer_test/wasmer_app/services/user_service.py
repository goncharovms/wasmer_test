from wasmer_app.models import Plan, User
from wasmer_app.services.base_service import BaseService


class UserService(BaseService):
    model_class = User

    @classmethod
    async def upgrade_user(cls, user: User) -> User:
        user.plan = Plan.PRO
        await user.asave()
        return user

    @classmethod
    async def downgrade_user(cls, user: User) -> User:
        user.plan = Plan.HOBBY
        await user.asave()
        return user

    @classmethod
    async def get_by_app_id(cls, app_id: str) -> User:
        user = await User.objects.filter(apps__id=app_id).aget()
        return user
