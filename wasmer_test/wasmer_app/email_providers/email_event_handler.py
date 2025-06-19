from wasmer_app.models import Email, EmailStatus
from wasmer_app.repositories.email_repository import EmailRepository


class BaseEmailEventHandler:
    def __init__(self, event: dict):
        self.event = event

    def get_message_id(self) -> str:
        raise NotImplementedError("Provider must implement get_message_id method")

    async def get_email(self, message_id) -> Email:
        email = await EmailRepository.get_by_message_id(message_id)
        return email

    def get_status(self) -> EmailStatus:
        raise NotImplementedError("Provider must implement process_status method")

    async def process(self) -> Email:
        message_id = self.get_message_id()
        email = await self.get_email(message_id)
        status = self.get_status()
        email = await EmailRepository.update_email(email=email, status=status)
        return email


class Smtp2GoEmailEventHandler(BaseEmailEventHandler):
    def get_message_id(self) -> str:
        return self.event.get("message_id")

    def get_status(self) -> EmailStatus:
        status_map = {
            "delivered": EmailStatus.SENT,
            "bounce": EmailStatus.FAILED,
            "spam": EmailStatus.SENT,
            "click": EmailStatus.READ,
            "open": EmailStatus.READ,
        }
        return status_map.get(self.event["status"])
