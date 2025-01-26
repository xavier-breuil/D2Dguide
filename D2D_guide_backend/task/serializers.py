"""
Serializers for task app.
"""
from rest_framework import serializers

from task.models import DatedTask, WeekTask, MultiOccurencesTask, Label


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ['name', 'id']


class LabelTaskSerializer(serializers.ModelSerializer):
    # https://github.com/encode/django-rest-framework/issues/2114
    # Id need to be explicitelly mentionned to be used on posting tasks.
    id = serializers.IntegerField()

    class Meta:
        model = Label
        fields = ['name', 'id']


class DatedTaskSerializer(serializers.ModelSerializer):
    label = LabelTaskSerializer(many=True)

    class Meta:
        model = DatedTask
        fields = ['name', 'date', 'done', 'id', 'label']

    def create(self, validated_data):
        """
        Handle labels.
        """
        label_data = validated_data.pop('label')
        dated_task = super(DatedTaskSerializer, self).create(validated_data)
        for label in label_data:
            dated_task.label.add(label['id'])
        return dated_task

    def update(self, instance, validated_data):
        """
        Handle labels update.
        """
        label_data = validated_data.pop('label')
        dated_task = super(DatedTaskSerializer, self).update(instance, validated_data)
        dated_task.label.clear()
        for label in label_data:
            dated_task.label.add(label['id'])
        return dated_task


class WeekTaskSerializer(serializers.ModelSerializer):
    label = LabelTaskSerializer(many=True)

    class Meta:
        model = WeekTask
        fields = ['name', 'week_number', 'year', 'done', 'id', 'label']

    def create(self, validated_data):
        """
        Handle labels.
        """
        label_data = validated_data.pop('label')
        week_task = super(WeekTaskSerializer, self).create(validated_data)
        for label in label_data:
            week_task.label.add(label['id'])
        return week_task

    def update(self, instance, validated_data):
        """
        Handle labels update.
        """
        label_data = validated_data.pop('label')
        week_task = super(WeekTaskSerializer, self).update(instance, validated_data)
        week_task.label.clear()
        for label in label_data:
            week_task.label.add(label['id'])
        return week_task


class MultiOccurencesTaskSerializer(serializers.ModelSerializer):
    label = LabelTaskSerializer(many=True)

    class Meta:
        model = MultiOccurencesTask
        fields = [
            'name', 'done', 'id', 'start_date', 'end_date', 'every_week', 'every_month', 'label',
            'every_year', 'every_last_day_of_month', 'number_a_day', 'number_a_week', 'task_name',
            'related_tasks_count', 'done_tasks_count'
        ]

    def to_internal_value(self, data):
        # Handle the case of empty string posted for number_a_day and number_a_week
        if data.get('number_a_day', None) == '':
            data['number_a_day'] = None
        if data.get('number_a_week', None) == '':
            data['number_a_week'] = None
        return super(MultiOccurencesTaskSerializer, self).to_internal_value(data)

    def create(self, validated_data):
        """
        Handle labels.
        """
        label_data = validated_data.pop('label')
        mot = super(MultiOccurencesTaskSerializer, self).create(validated_data)
        for label in label_data:
            mot.label.add(label['id'])
        return mot

    def update(self, instance, validated_data):
        """
        Handle labels.
        """
        label_data = validated_data.pop('label', 'not informed')
        labels_id = []
        for label in label_data:
            labels_id.append(label['id'])
        for field in self.get_fields().keys():
            try:
                setattr(instance, field, validated_data[field])
            except KeyError: # partial updated allowed
                pass
        instance.save()
        if label_data != 'not_informed':
            instance.label.set(labels_id)
        return instance
