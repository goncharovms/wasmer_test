from .models import User, Plan


async def upgrade_user(user_id: str):
    await User.objects.filter(id=user_id).aupdate(plan=Plan.PRO)

async def downgrade_user(user_id: str):
    await User.objects.filter(id=user_id).aupdate(plan=Plan.HOBBY)