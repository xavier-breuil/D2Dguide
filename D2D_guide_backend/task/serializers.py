"""
Serializers for task app.
"""
from rest_framework import serializers

from task.models import DatedTask

class DatedTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatedTask
        fields = ['name', 'date']
