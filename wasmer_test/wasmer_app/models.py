from django.db import models

import uuid
from django.db import models
from django.utils import timezone
from django_choices_field import TextChoicesField


class Plan(models.TextChoices):
    HOBBY = "HOBBY", "HOBBY"
    PRO = "PRO", "PRO"

def user_id():
    return f"u_{uuid.uuid4().hex}"

def deployed_app_id():
    return f"app_{uuid.uuid4().hex}"

class User(models.Model):
    id = models.CharField(primary_key=True, default=user_id, editable=False, max_length=34)
    username = models.CharField(max_length=100)
    plan = TextChoicesField(choices_enum=Plan, default=Plan.HOBBY)
    plan_changed_at = models.DateTimeField(auto_created=True, default=timezone.now)


class DeployedApp(models.Model):
    id = models.CharField(primary_key=True, default=deployed_app_id, editable=False, max_length=36)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='apps')
    active = models.BooleanField(default=True)
