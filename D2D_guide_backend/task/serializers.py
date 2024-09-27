"""
Serializers for task app.
"""
from rest_framework import serializers

from task.models import DatedTask, WeekTask


class DatedTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatedTask
        fields = ['name', 'date', 'done', 'id']


class WeekTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeekTask
        fields = ['name', 'week_number', 'year', 'done', 'id']
