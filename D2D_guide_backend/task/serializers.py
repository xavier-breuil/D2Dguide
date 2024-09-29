"""
Serializers for task app.
"""
from rest_framework import serializers

from task.models import DatedTask, WeekTask, MultiOccurencesTask


class DatedTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatedTask
        fields = ['name', 'date', 'done', 'id']


class WeekTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeekTask
        fields = ['name', 'week_number', 'year', 'done', 'id']

class MultiOccurencesTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiOccurencesTask
        fields = [
            'name', 'done', 'id', 'start_date', 'end_date', 'every_week', 'every_month',
            'every_year', 'every_last_day_of_month', 'number_a_day', 'number_a_week'
        ]
