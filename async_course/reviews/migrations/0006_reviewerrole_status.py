# Generated by Django 4.1 on 2022-09-19 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0005_alter_review_options_review_date_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='reviewerrole',
            name='status',
            field=models.CharField(choices=[('0', 'Not started'), ('1', 'Waiting for review'), ('2', 'Waiting for submission'), ('3', 'Complete')], default='0', max_length=1),
        ),
    ]
