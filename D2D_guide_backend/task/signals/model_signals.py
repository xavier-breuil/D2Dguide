from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError

from task.models import WeekTask, MultiOccurencesTask
from task.utils import number_of_weeks


@receiver(pre_save, sender=WeekTask)
def validate_week_number(sender, instance, **kwargs):
    if instance.week_number < 1 or instance.week_number > number_of_weeks(instance.year):
        raise ValidationError('Week_number must be within range [1,53]')

@receiver(pre_save, sender=MultiOccurencesTask)
def validate_multi_occurences_task(sender, instance, **kwargs):
    """
    Make sure data are clean before saving.
    """
    instance.clean()

@receiver(post_save, sender=MultiOccurencesTask)
def create_dated_tasks(sender, instance, created, **kwargs):
    """
    Once created, create appropriate tasks.
    Once modified, check for existing task and either modify them, delete them or create new ones.
    """
    if created:
        instance.create_related_tasks()
