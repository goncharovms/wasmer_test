import os

import django
from starlette.applications import Starlette
from starlette.routing import Route
from strawberry.asgi import GraphQL
from wasmer_app.email_providers.webhook_controller import webhook_smtp2go_view
from wasmer_app.schema.schema import schema

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wasmer_test.settings")

django.setup()


graphql_app = GraphQL(schema)


application = Starlette(
    routes=[
        Route("/graphql", graphql_app),
        Route("/webhook_smtp2go", webhook_smtp2go_view, methods=["POST"]),
    ]
)
