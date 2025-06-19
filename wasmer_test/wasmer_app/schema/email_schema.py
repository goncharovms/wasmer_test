from typing import Optional

import strawberry
import strawberry_django
from strawberry import ID
from wasmer_app.models import Email as Email_
from wasmer_app.schema.base_node import PlainTextNode


@strawberry_django.type(Email_, name="Email")
class Email(PlainTextNode):
    id: ID


@strawberry.type
class EmailCreatedResponse:
    successful: bool
    message: Optional[str] = None
