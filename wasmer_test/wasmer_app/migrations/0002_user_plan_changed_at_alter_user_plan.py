# Generated by Django 4.2 on 2025-06-17 18:06

import django.utils.timezone
import django_choices_field.fields
import wasmer_app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wasmer_app", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="plan_changed_at",
            field=models.DateTimeField(
                auto_created=True, default=django.utils.timezone.now
            ),
        ),
    ]
