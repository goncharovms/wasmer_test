from django.conf import settings
from django.test import TransactionTestCase
from django.utils import timezone
from uuid import uuid4
from wasmer_app.models import User, DeployedApp, Plan
from strawberry_django.test.client import AsyncTestClient
from unittest.mock import AsyncMock, patch


class GraphQLUserTests(TransactionTestCase):

    def setUp(self):
        self.hobby_user = User.objects.create(
            id=f"u_{uuid4().hex}",
            username="hobby_user",
            plan=Plan.HOBBY,
            plan_changed_at=timezone.now() - timezone.timedelta(days=10)
        )

        self.pro_user = User.objects.create(
            id=f"u_{uuid4().hex}",
            username="pro_user",
            plan=Plan.PRO,
            plan_changed_at=timezone.now() - timezone.timedelta(days=10)
        )

        self.hobby_app = DeployedApp.objects.create(id=f"app_{uuid4().hex}", owner=self.hobby_user)
        self.pro_app = DeployedApp.objects.create(id=f"app_{uuid4().hex}", owner=self.pro_user)
        self.async_client = AsyncTestClient("/graphql")
        self.send_email_query = """
            mutation SendEmail($appId: ID!, $subject: String!, $html: String!) {
                sendEmail(appId: $appId, subject: $subject, html: $html) {
                    successful message
                }
            }
        """

    @patch("wasmer_app.services.email_service.EmailService.get_count_per_trial_period", new_callable=AsyncMock)
    @patch("wasmer_app.services.email_service.EmailService.create_email", new_callable=AsyncMock)
    async def test_send_email_hobby_user_within_limit(self, mock_create_email, mock_get_count):
        mock_get_count.return_value = settings.EMAIL_LIMIT_COUNT - 1
        mock_create_email.return_value = type("Email", (), {"id": "email_123"})

        variables = {
            "appId": str(self.hobby_app.id),
            "subject": "Test Subject",
            "html": "<p>Test HTML</p>"
        }

        response = await self.async_client.query(self.send_email_query, variables=variables)

        self.assertTrue(response.data["sendEmail"]["successful"])

    @patch("wasmer_app.services.email_service.EmailService.get_count_per_trial_period", new_callable=AsyncMock)
    @patch("wasmer_app.services.email_service.EmailService.create_email", new_callable=AsyncMock)
    async def test_send_email_hobby_user_over_limit(self, mock_create_email, mock_get_count):
        mock_get_count.return_value = settings.EMAIL_LIMIT_COUNT
        mock_create_email.return_value = type("Email", (), {"id": "email_123"})

        variables = {
            "appId": str(self.hobby_app.id),
            "subject": "Test Subject",
            "html": "<p>Test HTML</p>"
        }

        response = await self.async_client.query(self.send_email_query, variables=variables)

        self.assertFalse(response.data["sendEmail"]["successful"])

