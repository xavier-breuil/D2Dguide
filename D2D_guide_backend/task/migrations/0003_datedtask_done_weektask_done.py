# Generated by Django 5.1 on 2024-08-31 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0002_weektask'),
    ]

    operations = [
        migrations.AddField(
            model_name='datedtask',
            name='done',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='weektask',
            name='done',
            field=models.BooleanField(default=False),
        ),
    ]
