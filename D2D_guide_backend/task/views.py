from django.shortcuts import render
from rest_framework import viewsets
from django_filters import rest_framework as filters

from task.models import DatedTask, WeekTask, MultiOccurencesTask
from task.serializers import (
    DatedTaskSerializer, WeekTaskSerializer, MultiOccurencesTaskSerializer)


class DatedTaskFilter(filters.FilterSet):
    week = filters.NumberFilter(field_name="date__week")
    year = filters.NumberFilter(field_name="date__year")

    class Meta:
        model = DatedTask
        fields = ['name', 'date', 'done', 'week', 'year']


class DatedTaskViewSet(viewsets.ModelViewSet):
    """
    View that returns dated task data.
    """
    queryset = DatedTask.objects.all().order_by('date')
    serializer_class = DatedTaskSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = DatedTaskFilter


class WeekTaskViewSet(viewsets.ModelViewSet):
    """
    View that returns week task data.
    """
    queryset = WeekTask.objects.all().order_by('week_number')
    serializer_class = WeekTaskSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('week_number', 'year')


class MultiOccurencesTaskViewSet(viewsets.ModelViewSet):
    """
    View that returns multi occurences task data.
    """
    queryset = MultiOccurencesTask.objects.all()
    serializer_class = MultiOccurencesTaskSerializer
