from django.shortcuts import render

from rest_framework import viewsets

from task.models import DatedTask
from task.serializers import DatedTaskSerializer

class DatedTaskViewSet(viewsets.ModelViewSet):
    """
    View that returns dated task data.
    """
    queryset = DatedTask.objects.all().order_by('date')
    serializer_class = DatedTaskSerializer
