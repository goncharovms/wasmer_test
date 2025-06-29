# Generated by Django 4.2 on 2025-06-17 19:43

import django.db.models.deletion
import django_choices_field.fields
import wasmer_app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wasmer_app", "0002_user_plan_changed_at_alter_user_plan"),
    ]

    operations = [
        migrations.AlterField(
            model_name="deployedapp",
            name="id",
            field=models.CharField(
                default=wasmer_app.models.deployed_app_id,
                editable=False,
                max_length=50,
                primary_key=True,
                serialize=False,
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="id",
            field=models.CharField(
                default=wasmer_app.models.user_id,
                editable=False,
                max_length=50,
                primary_key=True,
                serialize=False,
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="plan",
            field=django_choices_field.fields.TextChoicesField(
                choices=[("HOBBY", "HOBBY"), ("PRO", "PRO")],
                choices_enum=wasmer_app.models.Plan,
                default="HOBBY",
                max_length=5,
            ),
        ),
        migrations.CreateModel(
            name="ProviderCredential",
            fields=[
                (
                    "id",
                    models.CharField(
                        default=wasmer_app.models.provider_credential_id,
                        editable=False,
                        max_length=50,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                (
                    "provider",
                    django_choices_field.fields.TextChoicesField(
                        choices=[
                            ("SMTP2GO", "SMTP2GO"),
                            ("MAILGUN", "MAILGUN"),
                            ("AMAZON_SES", "AMAZON_SES"),
                        ],
                        choices_enum=wasmer_app.models.Provider,
                        max_length=10,
                    ),
                ),
                ("credentials", models.JSONField(blank=True, default=dict, null=True)),
                (
                    "credentials_hash",
                    models.CharField(blank=True, max_length=64, null=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="credentials",
                        to="wasmer_app.user",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Email",
            fields=[
                (
                    "id",
                    models.CharField(
                        default=wasmer_app.models.email_id,
                        editable=False,
                        max_length=35,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("external_id", models.CharField(max_length=100, null=True)),
                ("sent_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("subject", models.CharField(blank=True, max_length=511, null=True)),
                ("html", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "status",
                    django_choices_field.fields.TextChoicesField(
                        choices=[
                            ("PENDING", "PENDING"),
                            ("SENT", "SENT"),
                            ("FAILED", "FAILED"),
                            ("READ", "READ"),
                        ],
                        choices_enum=wasmer_app.models.EmailStatus,
                        max_length=7,
                    ),
                ),
                (
                    "deployed_app",
                    models.ForeignKey(
                        blank=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="emails",
                        to="wasmer_app.deployedapp",
                    ),
                ),
                (
                    "provider_credential",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="emails",
                        to="wasmer_app.providercredential",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="providercredential",
            constraint=models.UniqueConstraint(
                condition=models.Q(("is_active", True)),
                fields=("user",),
                name="unique_active_credential_per_user",
            ),
        ),
        migrations.AddConstraint(
            model_name="providercredential",
            constraint=models.UniqueConstraint(
                fields=("user", "provider", "credentials_hash"),
                name="unique_user_provider_hash",
            ),
        ),
    ]
