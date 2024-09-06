from django.shortcuts import render
from rest_framework import viewsets
from django_filters import rest_framework as filters

from task.models import DatedTask, WeekTask
from task.serializers import DatedTaskSerializer, WeekTaskSerializer


class DatedTaskViewSet(viewsets.ModelViewSet):
    """
    View that returns dated task data.
    """
    queryset = DatedTask.objects.all().order_by('date')
    serializer_class = DatedTaskSerializer


class WeekTaskViewSet(viewsets.ModelViewSet):
    """
    View that returns week task data.
    """
    queryset = WeekTask.objects.all().order_by('week_number')
    serializer_class = WeekTaskSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('week_number',)
