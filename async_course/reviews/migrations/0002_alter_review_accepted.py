# Generated by Django 4.1 on 2022-08-19 22:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='accepted',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
