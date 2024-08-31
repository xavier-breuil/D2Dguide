from django.db import models

# Create your models here.
class Task(models.Model):
    """
    Abstract task model.
    """
    name = models.CharField(max_length=100)

    class Meta:
        abstract = True

class DatedTask(Task):
    """
    Task that must be accomplished on a specific date.
    """
    date = models.DateField(null=False, blank=False)