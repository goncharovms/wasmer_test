import uuid

from django.db import models
from django.db.models import Q
from django.utils import timezone
from django_choices_field import TextChoicesField


class Plan(models.TextChoices):
    HOBBY = "HOBBY", "HOBBY"
    PRO = "PRO", "PRO"


class Provider(models.TextChoices):
    SMTP2GO = "SMTP2GO", "SMTP2GO"
    MAILGUN = "MAILGUN", "MAILGUN"
    AMAZON_SES = "AMAZON_SES", "AMAZON_SES"


class EmailStatus(models.TextChoices):
    PENDING = "PENDING", "PENDING"
    SENT = "SENT", "SENT"
    FAILED = "FAILED", "FAILED"
    READ = "READ", "READ"


def user_id():
    return f"u_{uuid.uuid4().hex}"


def deployed_app_id():
    return f"app_{uuid.uuid4().hex}"


def provider_credential_id():
    return f"cred_{uuid.uuid4().hex}"


def email_id():
    return f"em_{uuid.uuid4().hex}"


class User(models.Model):
    id = models.CharField(
        primary_key=True, default=user_id, editable=False, max_length=50
    )
    username = models.CharField(max_length=100)
    plan = TextChoicesField(choices_enum=Plan, default=Plan.HOBBY)
    plan_changed_at = models.DateTimeField(auto_created=True, default=timezone.now)


class DeployedApp(models.Model):
    id = models.CharField(
        primary_key=True, default=deployed_app_id, editable=False, max_length=50
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="apps")
    active = models.BooleanField(default=True)


class ProviderCredential(models.Model):
    id = models.CharField(
        primary_key=True, default=provider_credential_id, editable=False, max_length=50
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="credentials")
    is_active = models.BooleanField(default=True)
    provider = TextChoicesField(choices_enum=Provider)
    credentials = models.JSONField(default=dict, blank=True, null=True)
    credentials_hash = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=Q(is_active=True),
                name="unique_active_credential_per_user",
            ),
            models.UniqueConstraint(
                fields=["user", "provider", "credentials_hash"],
                name="unique_user_provider_hash",
            ),
        ]


class Email(models.Model):
    id = models.CharField(
        primary_key=True, default=email_id, editable=False, max_length=35
    )
    deployed_app = models.ForeignKey(
        DeployedApp,
        on_delete=models.DO_NOTHING,
        related_name="emails",
        blank=True,
        db_index=True,
    )

    provider_credential = models.ForeignKey(
        ProviderCredential,
        on_delete=models.CASCADE,
        related_name="emails",
        blank=True,
        null=True,
        db_index=True,
    )
    receiver = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    external_id = models.CharField(max_length=100, null=True, db_index=True)
    subject = models.CharField(max_length=511, blank=True, null=True)
    html = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    status = TextChoicesField(choices_enum=EmailStatus, default=EmailStatus.PENDING)
