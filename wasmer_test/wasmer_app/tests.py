from django.test import TransactionTestCase
from strawberry_django.test.client import AsyncTestClient
from wasmer_app.models import User, DeployedApp, Plan


class GraphQLUserTests(TransactionTestCase):
    def setUp(self):
        self.user_hobby = User.objects.create(
            id="u_test_hobby",
            username="alice",
            plan=Plan.HOBBY
        )
        self.user_pro = User.objects.create(
            id="u_test_pro",
            username="alice",
            plan=Plan.PRO
        )

        self.deployed_app = DeployedApp.objects.create(
            id="app_test_pro",
            owner=self.user_pro,
            active=True
        )
        self.async_client = AsyncTestClient("/graphql")

    async def test_fetch_user_node(self):

        response = await self.async_client.query(
            """
            query getUser($id: String!) {
              node(id: $id) {
                ...on User {
                  id
                  username
                  plan
                }
              }
            }
            """, variables={"id": self.user_hobby.id}
        )
        self.assertEqual(
            response.data["node"],
            {'id': self.user_hobby.id, 'username': self.user_hobby.username, 'plan': self.user_hobby.plan.value}
        )

    async def test_fetch_deployed_app(self):

        response = await self.async_client.query(
            """
            query getApp($id: String!) {
              node(id: $id) {
                ... on DeployedApp {
                  id
                  active
                }
              }
            }
            """, variables={"id": self.deployed_app.id}
        )
        self.assertEqual(
            response.data["node"],
            {'id': self.deployed_app.id, 'active': True}
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
            variables={"userId": self.user_hobby.id}
        )

        self.assertEqual(
            response.data["upgradeAccount"],
            {'id': self.user_hobby.id, 'plan': Plan.PRO.value}
        )

        user = await User.objects.aget(id=self.user_hobby.id)
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
            variables={"userId": self.user_pro.id}
        )

        self.assertEqual(
            response.data["downgradeAccount"],
            {'id': self.user_pro.id, 'plan': Plan.HOBBY.value}
        )

        user = await User.objects.aget(id=self.user_pro.id)
        self.assertEqual(user.plan, Plan.HOBBY)
