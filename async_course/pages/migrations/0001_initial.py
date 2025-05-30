# Generated by Django 4.1 on 2022-08-18 00:24

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('pubref', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('markdown', models.TextField(default='')),
                ('html', models.TextField(default='')),
                ('valid', models.BooleanField(default=False)),
                ('error', models.TextField(null=True)),
                ('slug', models.CharField(max_length=40)),
                ('publications', models.ManyToManyField(to='pubref.publication')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
