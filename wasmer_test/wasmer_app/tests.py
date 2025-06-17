from django.test import TransactionTestCase
from strawberry_django.test.client import AsyncTestClient
from wasmer_app.models import User, DeployedApp, Plan


class GraphQLUserTests(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create(
            id="u_test123",
            username="alice",
            plan=Plan.HOBBY
        )

        self.deployed_app = DeployedApp.objects.create(
            id="app_abc123",
            owner=self.user,
            active=True
        )
        self.async_client = AsyncTestClient("/graphql")

    async def test_fetch_user_node(self):

        response = await self.async_client.query(
            """
            query getUser {
              node(id: "u_test123") {
                ...on User {
                  id
                  username
                  plan
                }
              }
            }
            """
        )

        self.assertEqual(
            response.data["node"],
            {'id': 'u_test123', 'username': 'alice', 'plan': 'HOBBY'}
        )

    async def test_fetch_deployed_app(self):

        response = await self.async_client.query(
            """
            query getApp {node(id: "app_abc123"){
              ...on DeployedApp{
                    id
                    active
                  }
                }}
            """
        )
        self.assertEqual(
            response.data["node"],
            {'id': 'app_abc123', 'active': True}
        )

    async def test_upgrade_account(self):
        response = await self.async_client.query(
            """
            mutation upgradeAccount($userId: ID!) {
              upgradeAccount(userId: $userId) {
                id
                plan
              }
            }
            """,
            variables={"userId": "u_test123"}
        )

        self.assertEqual(
            response.data["upgradeAccount"],
            {'id': 'u_test123', 'plan': 'PRO'}
        )

        user = await User.objects.aget(id="u_test123")
        self.assertEqual(user.plan, Plan.PRO)


    async def test_downgrade_account(self):
        response = await self.async_client.query(
            """
            mutation downgradeAccount($userId: ID!) {
              downgradeAccount(userId: $userId) {
                id
                plan
              }
            }
            """,
            variables={"userId": "u_test123"}
        )

        self.assertEqual(
            response.data["downgradeAccount"],
            {'id': 'u_test123', 'plan': 'HOBBY'}
        )

        user = await User.objects.aget(id="u_test123")
        self.assertEqual(user.plan, Plan.HOBBY)
