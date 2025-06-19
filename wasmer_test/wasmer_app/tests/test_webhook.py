from uuid import uuid4

from django.test import TransactionTestCase
from django.utils import timezone
from starlette.testclient import TestClient
from wasmer_app.models import (
    DeployedApp,
    Email,
    EmailStatus,
    Plan,
    Provider,
    ProviderCredential,
    User,
)

from wasmer_test.asgi import application


class WebhookSMTP2GoTests(TransactionTestCase):
    def setUp(self):
        self.client = TestClient(application)
        self.hobby_user = User.objects.create(
            id=f"u_{uuid4().hex}",
            username="hobby_user",
            plan=Plan.HOBBY,
            plan_changed_at=timezone.now() - timezone.timedelta(days=10),
        )
        self.hobby_app = DeployedApp.objects.create(
            id=f"app_{uuid4().hex}", owner=self.hobby_user
        )
        self.creds = ProviderCredential.objects.create(
            user=self.hobby_user,
            is_active=True,
            provider=Provider.SMTP2GO,
            credentials={},
            credentials_hash="9e9dbf69d960739dbbc67aa6d7902029025ad646c823c918e99338a576df5ef6",
        )
        self.email1 = Email.objects.create(
            id="123",
            deployed_app=self.hobby_app,
            subject="Test Email",
            receiver="some@email.com",
            external_id="123",
            html="This is a test email.",
            status=EmailStatus.SENT,
        )
        self.email2 = Email.objects.create(
            id="1233",
            deployed_app=self.hobby_app,
            subject="Test Email",
            receiver="some@email.com",
            external_id="456",
            html="This is a test email.",
            status=EmailStatus.SENT,
        )

    def test_valid_webhook(self):
        payload = [
            {"message_id": "123", "status": "bounce"},
            {"message_id": "456", "status": "open"},
        ]

        response = self.client.post("/webhook_smtp2go", json=payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "success"})
        self.email1.refresh_from_db()
        self.email2.refresh_from_db()
        self.assertEqual(self.email1.status, EmailStatus.FAILED)
        self.assertEqual(self.email2.status, EmailStatus.READ)

    def test_invalid_json(self):
        response = self.client.post("/webhook_smtp2go", data="invalid json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Invalid JSON"})

    def test_invalid_type(self):
        response = self.client.post("/webhook_smtp2go", json={"not": "a list"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Expected a list of events"})

    def test_event_not_dict(self):
        response = self.client.post("/webhook_smtp2go", json=["not-a-dict"])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Each event must be a dictionary"})

    def test_missing_fields(self):
        response = self.client.post("/webhook_smtp2go", json=[{"message_id": "123"}])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {"error": "Each event must contain 'message_id' and 'status'"},
        )
