# Generated by Django 4.1 on 2022-08-18 16:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pubref', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='publication',
            name='contributor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='publications', to=settings.AUTH_USER_MODEL),
        ),
    ]
