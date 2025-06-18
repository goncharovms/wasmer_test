import email.message
import re
import ssl

import aiosmtplib
import certifi
from asgiref.sync import sync_to_async
from wasmer_app.models import Email, EmailStatus, Provider, ProviderCredential

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
    def message(self) -> email.message.EmailMessage:
        message = email.message.EmailMessage()
        message["From"] = self.credentials.credentials["username"]
        message["To"] = "albina.upton37@ethereal.email"
        message["Subject"] = self.email.subject
        message.set_content(self.email.html)
        message.add_alternative(self.email.html, subtype="html")
        return message

    @staticmethod
    def _parse_response(response_message) -> str | None:
        if "Accepted" not in response_message:
            raise SendEmailException("Message not accepted")

        match = re.search(r"MSGID=([^\]]+)", response_message)
        if match:
            msg_id = match.group(1)
            return msg_id

    async def send_email(self):
        try:
            response_message = await self._send()
            message_id = self._parse_response(response_message)
        except Exception:
            self.email.status = EmailStatus.FAILED
            await self.email.asave()
            raise
        else:
            self.email.status = EmailStatus.SENT
            self.email.provider_credential = self.credentials
            self.email.external_id = message_id
        await self.email.asave()


async def send_email(email: Email):
    PROVIDER_MAP = {
        Provider.SMTP2GO: EmailSender,
        Provider.AMAZON_SES: EmailSender,
        Provider.MAILGUN: EmailSender,
    }

    def sync_get_creds():
        return email.deployed_app.owner.credentials.filter(is_active=True).first()

    credential = await sync_to_async(sync_get_creds)()

    provider = PROVIDER_MAP[credential.provider](email, credential)
    await provider.send_email()
