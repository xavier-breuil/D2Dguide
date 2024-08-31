from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

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


class WeekTask(Task):
    """
    Task that must be accomplished on a specific week.
    """
    week_number = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(53), MinValueValidator(1)])
