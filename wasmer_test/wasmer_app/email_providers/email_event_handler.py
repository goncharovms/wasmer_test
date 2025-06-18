from wasmer_app.models import Email, EmailStatus


class BaseEmailEventHandler:
    def __init__(self, event: dict):
        self.event = event

    async def get_email(self) -> Email:
        raise NotImplementedError("Provider must implement process_status method")

    def get_status(self) -> EmailStatus:
        raise NotImplementedError("Provider must implement process_status method")

    @staticmethod
    async def set_status(email: Email, status: EmailStatus):
        email.status = status
        await email.asave()

    async def process(self):
        email = await self.get_email()
        status = self.get_status()
        await self.set_status(email, status)
