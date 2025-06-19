from  email.message import EmailMessage
import re
import ssl

import aiosmtplib
import certifi
from wasmer_app.models import Email, EmailStatus, Provider, ProviderCredential, DeployedApp
from wasmer_app.services.credentials_repository import ProviderCredentialsRepository
from wasmer_app.services.email_repository import EmailRepository

ssl_context = ssl.create_default_context(cafile=certifi.where())


class SendEmailException(Exception):
    pass


class EmailSender:

    def __init__(self, email: Email, credentials: ProviderCredential):
        self.email = email
        self.credentials = credentials

    async def _send(self):
        _, response_message = await aiosmtplib.send(
            self.message,
            hostname=self.credentials.credentials["host"],
            port=self.credentials.credentials["port"],
            username=self.credentials.credentials["username"],
            password=self.credentials.credentials["password"],
            start_tls=self.credentials.credentials.get("start_tls", True),
            tls_context=ssl_context,
        )
        return response_message

    @property
    def message(self) -> EmailMessage:
        message = EmailMessage()
        message["From"] = self.credentials.credentials["username"]
        message["To"] = self.email.receiver
        message["Subject"] = self.email.subject
        message.set_content(self.email.html)
        message.add_alternative(self.email.html, subtype="html")
        return message

    @staticmethod
    def _get_message_id(response_message) -> str | None:
        if "Accepted" not in response_message:
            raise SendEmailException("Message not accepted")

        match = re.search(r"MSGID=([^\]]+)", response_message)
        if match:
            msg_id = match.group(1)
            return msg_id
        return None

    async def send_email(self):
        try:
            response_message = await self._send()
            message_id = self._get_message_id(response_message)
        except Exception:
            self.email = await EmailRepository.update_email(
                self.email,
                status=EmailStatus.FAILED,
                provider_credential=self.credentials,
            )
            raise
        else:
            await EmailRepository.update_email(
                self.email,
                status=EmailStatus.SENT,
                provider_credential=self.credentials,
                external_id=message_id,
            )


async def send_email(email: Email, deployed_app: DeployedApp):
    provider_map = {
        Provider.SMTP2GO: EmailSender,
        Provider.AMAZON_SES: EmailSender,
        Provider.MAILGUN: EmailSender,
    }

    credential = await ProviderCredentialsRepository.get_by_app(deployed_app)
    provider = provider_map[credential.provider](email, credential)
    await provider.send_email()
