# Generated by Django 5.1 on 2024-09-21 18:57

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0003_datedtask_done_weektask_done'),
    ]

    operations = [
        migrations.AddField(
            model_name='weektask',
            name='year',
            field=models.PositiveSmallIntegerField(default=2024, validators=[django.core.validators.MinValueValidator(2024)]),
            preserve_default=False,
        ),
    ]