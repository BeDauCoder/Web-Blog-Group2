# Generated by Django 4.2.16 on 2024-10-08 16:04

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("web", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="item",
            name="created_at",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name="item",
            name="end_date",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="item",
            name="image",
            field=models.ImageField(blank=True, null=True, upload_to="static/images/"),
        ),
        migrations.AddField(
            model_name="item",
            name="start_date",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
