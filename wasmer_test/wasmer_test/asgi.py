"""
ASGI config for wasmer_test project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

import django
from strawberry.asgi import GraphQL
from wasmer_app.schema import schema

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wasmer_test.settings")

django.setup()

graphql_app = GraphQL(schema)

application = graphql_app
