# Generated by Django 4.2 on 2025-06-16 17:55

import django.db.models.deletion
import wasmer_app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.CharField(
                        default=wasmer_app.models.user_id,
                        editable=False,
                        max_length=34,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("username", models.CharField(max_length=100)),
                (
                    "plan",
                    models.CharField(
                        choices=[("HOBBY", "Hobby"), ("PRO", "Pro")],
                        default="HOBBY",
                        max_length=10,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="DeployedApp",
            fields=[
                (
                    "id",
                    models.CharField(
                        default=wasmer_app.models.deployed_app_id,
                        editable=False,
                        max_length=36,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("active", models.BooleanField(default=True)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="apps",
                        to="wasmer_app.user",
                    ),
                ),
            ],
        ),
    ]
