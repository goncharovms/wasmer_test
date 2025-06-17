from wasmer_app.models import User, Plan
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