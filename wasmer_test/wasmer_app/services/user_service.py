from typing import Optional

from wasmer_app.models import Plan
from wasmer_app.repositories.user_repository import UserRepository


class UserService:
    @staticmethod
    async def upgrade_account(user_id: str) -> Optional["User"]:
        user = await UserRepository.get_object(user_id)
        if user.plan == Plan.PRO:
            raise ValueError("Cannot downgrade a user already on the PRO plan.")
        return await UserRepository.upgrade_user(user)

    @staticmethod
    async def downgrade_account(user_id: str) -> Optional["User"]:
        user = await UserRepository.get_object(user_id)
        if user.plan == Plan.HOBBY:
            raise ValueError("Cannot downgrade a user already on the HOBBY plan.")
        return await UserRepository.downgrade_user(user)
