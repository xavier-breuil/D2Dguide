from datetime import date

from django.shortcuts import render
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django_filters import rest_framework as filters

from task.models import DatedTask, WeekTask, MultiOccurencesTask, Label
from task.serializers import (
    DatedTaskSerializer, WeekTaskSerializer, MultiOccurencesTaskSerializer, LabelSerializer)
from D2D_guide_backend.mixins.partial_update_mixin import PartialUpdateMixin


class LabelViewSet(viewsets.ModelViewSet):
    """
    View that returns labels.
    """
    queryset = Label.objects.all().order_by('name')
    serializer_class = LabelSerializer


class DatedTaskFilter(filters.FilterSet):
    week = filters.NumberFilter(field_name="date__week")
    year = filters.NumberFilter(field_name="date__year")

    class Meta:
        model = DatedTask
        fields = ['name', 'date', 'done', 'week', 'year', 'label']


class DatedTaskViewSet(viewsets.ModelViewSet):
    """
    View that returns dated task data.
    """
    queryset = DatedTask.objects.all().order_by('date', 'name')
    serializer_class = DatedTaskSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = DatedTaskFilter


class WeekTaskViewSet(viewsets.ModelViewSet):
    """
    View that returns week task data.
    """
    queryset = WeekTask.objects.all().order_by('week_number', 'name')
    serializer_class = WeekTaskSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('week_number', 'year', 'label')


class MultiOccurencesTaskViewSet(PartialUpdateMixin, viewsets.ModelViewSet):
    """
    View that returns multi occurences task data.
    """
    queryset = MultiOccurencesTask.objects.all()
    serializer_class = MultiOccurencesTaskSerializer

@api_view()
def get_late_tasks(request):
    """
    Return task before this week that have not been marked as done.
    """
    today = date.today()
    dated_tasks = DatedTask.objects.filter(date__lt=today, done=False)
    this_week = today.isocalendar()[1]
    this_year = today.isocalendar()[0]
    week_tasks = WeekTask.objects.filter(
        Q(week_number__lt=this_week, year=this_year, done=False) | Q(year__lt=this_year, done=False))
    late_tasks = []
    for task in dated_tasks:
        late_tasks.append({
            'name': task.name,
            'done': task.done,
            'id': task.id,
            'type': 'date',
            'date': task.date.strftime('%d/%m/%Y')})
    for task in week_tasks:
        late_tasks.append({
            'name': task.name,
            'done': task.done,
            'id': task.id,
            'type': 'week',
            'week': task.week_number,
            'year': task.year})
    return Response({'late_tasks': late_tasks})
