from datetime import timedelta
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from django.conf import settings
from django.test import TransactionTestCase
from django.utils import timezone
from strawberry_django.test.client import AsyncTestClient
from wasmer_app.models import (
    DeployedApp,
    Email,
    EmailStatus,
    Plan,
    Provider,
    ProviderCredential,
    User,
)


class GraphQLUserTests(TransactionTestCase):

    def setUp(self):
        self.hobby_user = User.objects.create(
            id=f"u_{uuid4().hex}",
            username="hobby_user",
            plan=Plan.HOBBY,
            plan_changed_at=timezone.now() - timezone.timedelta(days=10),
        )

        self.pro_user = User.objects.create(
            id=f"u_{uuid4().hex}",
            username="pro_user",
            plan=Plan.PRO,
            plan_changed_at=timezone.now() - timezone.timedelta(days=10),
        )

        self.hobby_app = DeployedApp.objects.create(
            id=f"app_{uuid4().hex}", owner=self.hobby_user
        )
        self.pro_app = DeployedApp.objects.create(
            id=f"app_{uuid4().hex}", owner=self.pro_user
        )
        self.creds = ProviderCredential.objects.create(
            user=self.hobby_user,
            is_active=True,
            provider=Provider.AMAZON_SES,
            credentials={
                "host": "smtp.ethereal.email",
                "port": 587,
                "username": "albina.upton37@ethereal.email",
                "password": "cbr1CGtZAufYkM9Xgu",
                "use_tls": True,
            },
            credentials_hash="9e9dbf69d960739dbbc67aa6d7902029025ad646c823c918e99338a576df5ef6",
        )
        self.async_client = AsyncTestClient("/graphql")
        self.send_email_query = """
            mutation SendEmail($appId: ID!, $to: String!, $subject: String!, $html: String!) {
                sendEmail(appId: $appId, to: $to, subject: $subject, html: $html) {
                    successful message
                }
            }
        """

        self.get_creds_query = """
            query GetCredentials($appId: ID!) {
                getSmtpCredentials(appId: $appId)
            }
        """
        now = timezone.now()
        Email.objects.bulk_create(
            [
                Email(
                    id=f"e_{uuid4().hex}",
                    deployed_app=self.hobby_app,
                    status=EmailStatus.SENT,
                    created_at=now - timedelta(days=1),
                ),
                Email(
                    id=f"e_{uuid4().hex}",
                    deployed_app=self.hobby_app,
                    status=EmailStatus.FAILED,
                    created_at=now - timedelta(days=1),
                ),
                Email(
                    id=f"e_{uuid4().hex}",
                    deployed_app=self.hobby_app,
                    status=EmailStatus.READ,
                    created_at=now - timedelta(days=2),
                ),
            ]
        )

    async def test_get_credentials(self):
        variables = {"appId": self.hobby_app.id}

        response = await self.async_client.query(
            self.get_creds_query, variables=variables
        )

        self.assertIsNotNone(response.data["getSmtpCredentials"])
        creds = response.data["getSmtpCredentials"]
        self.assertEqual(creds, self.creds.credentials)

    @patch(
        "wasmer_app.repositories.email_repository.EmailRepository.get_count_per_trial_period",
        new_callable=AsyncMock,
    )
    @patch(
        "wasmer_app.email_providers.email_provider.EmailSender._send",
        new_callable=AsyncMock,
    )
    async def test_send_email_hobby_user_within_limit(self, mock_send, mock_get_count):
        mock_get_count.return_value = settings.EMAIL_LIMIT_COUNT - 1
        mock_send.return_value = (
            "Accepted [STATUS=new MSGID=aFLx7W5F3rtNsImJaFMW-9mj0IJfKetc]"
        )

        variables = {
            "appId": self.hobby_app.id,
            "subject": "Test Subject",
            "html": "<p>Test HTML</p>",
            "to": "test_mail@gmail.com",
        }

        response = await self.async_client.query(
            self.send_email_query, variables=variables
        )

        self.assertTrue(response.data["sendEmail"]["successful"])
        email = (
            await Email.objects.filter(deployed_app=self.hobby_app)
            .order_by("-created_at")
            .afirst()
        )
        self.assertEqual(email.status, EmailStatus.SENT)
        self.assertEqual(email.external_id, "aFLx7W5F3rtNsImJaFMW-9mj0IJfKetc")

    @patch(
        "wasmer_app.repositories.email_repository.EmailRepository.get_count_per_trial_period",
        new_callable=AsyncMock,
    )
    async def test_send_email_hobby_user_over_limit(self, mock_get_count):
        mock_get_count.return_value = settings.EMAIL_LIMIT_COUNT

        variables = {
            "appId": self.hobby_app.id,
            "subject": "Test Subject",
            "html": "<p>Test HTML</p>",
            "to": "test_mail@gmail.com",
        }

        response = await self.async_client.query(
            self.send_email_query, variables=variables
        )

        self.assertFalse(response.data["sendEmail"]["successful"])

    async def test_user_email_usage(self):
        start = (timezone.now() - timedelta(days=3)).isoformat()
        end = timezone.now().isoformat()

        query = """
        query UserEmailStats($id: String!, $groupBy: GroupByEnum!, $timeWindow: TimeWindow) {
          node(id: $id) {
            ... on User {
              id
              username
              plan
              emails {
                sentEmailsCount
                usage(groupBy: $groupBy, timeWindow: $timeWindow) {
                  timestamp
                  emails {
                    total
                    sent
                    failed
                    read
                  }
                }
              }
            }
          }
        }
        """

        # Encode the global relay Node ID if using Node interface

        variables = {
            "id": self.hobby_user.id,
            "groupBy": "DAY",
            "timeWindow": {
                "start": start,
                "end": end,
            },
        }

        response = await self.async_client.query(query=query, variables=variables)

        user_data = response.data["node"]
        self.assertEqual(user_data["id"], self.hobby_user.id)
        self.assertEqual(user_data["username"], "hobby_user")
        self.assertEqual(user_data["plan"], "HOBBY")
        self.assertEqual(user_data["emails"]["sentEmailsCount"], 3)

        usage_data = user_data["emails"]["usage"]
        self.assertGreater(len(usage_data), 0)
        totals = {
            "sent": sum(day["emails"]["sent"] for day in usage_data),
            "failed": sum(day["emails"]["failed"] for day in usage_data),
            "read": sum(day["emails"]["read"] for day in usage_data),
            "total": sum(day["emails"]["total"] for day in usage_data),
        }

        self.assertEqual(totals["sent"], 1)
        self.assertEqual(totals["failed"], 1)
        self.assertEqual(totals["read"], 1)
        self.assertEqual(totals["total"], 3)
