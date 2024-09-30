from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError

from task.models import WeekTask, MultiOccurencesTask
from task.utils import number_of_weeks


@receiver(pre_save, sender=WeekTask)
def validate_week_number(sender, instance, **kwargs):
    if instance.week_number < 1 or instance.week_number > number_of_weeks(instance.year):
        raise ValidationError('Week_number must be within range [1,53]')

@receiver(pre_save, sender=MultiOccurencesTask)
def validate_week_number(sender, instance, **kwargs):
    """
    Make sure data are clean before saving.
    """
    instance.clean()
