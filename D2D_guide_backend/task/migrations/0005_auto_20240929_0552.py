# Generated by Django 5.1 on 2024-09-29 05:52

from django.db import migrations
from django.contrib.postgres.operations import HStoreExtension

# necessary operation to use HStoreField:
# https://docs.djangoproject.com/en/5.1/ref/contrib/postgres/operations/
class Migration(migrations.Migration):

    dependencies = [
        ('task', '0004_weektask_year'),
    ]

    operations = [
        HStoreExtension(),
    ]
