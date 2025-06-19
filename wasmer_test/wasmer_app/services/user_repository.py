from wasmer_app.models import Plan, User
from wasmer_app.services.base_repository import BaseRepository


class UserRepository(BaseRepository):
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
