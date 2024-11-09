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
            'every_year', 'every_last_day_of_month', 'number_a_day', 'number_a_week', 'task_name'
        ]

    def to_internal_value(self, data):
        # Handle the case of empty string posted for number_a_day and number_a_week
        if data.get('number_a_day', None) == '':
            data['number_a_day'] = None
        if data.get('number_a_week', None) == '':
            data['number_a_week'] = None
        return super(MultiOccurencesTaskSerializer, self).to_internal_value(data)