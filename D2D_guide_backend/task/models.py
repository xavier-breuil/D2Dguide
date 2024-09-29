from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.postgres.fields import ArrayField, HStoreField

class Task(models.Model):
    """
    Abstract task model.
    """
    name = models.CharField(max_length=100)
    done = models.BooleanField(default=False)

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
    year = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(2024)])
    week_number = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(53), MinValueValidator(1)])


class MultiOccurencesTask(Task):
    """
    Tasks that are meant to be repeated over weeks, monthes or years.
    """
    # start and end dates are necessayr for every_... field.
    start_date = models.DateField()
    end_date = models.DateField()
    # 1 is for monday, 7 for sunday.
    # A task to repeat every tuesday and friday would have this field equal to [2, 5]
    every_week = ArrayField(
        models.SmallIntegerField(),
        default=list
    )
    # A task to repeat on the 1st and 15th of each month would have this field equal to [1, 15]
    # If a task is to be perform on the 31st and a month has only 30 days,
    # it won't be added to this field.
    every_month = ArrayField(
        models.SmallIntegerField(),
        default=list
    )
    # True if teh task is to be performed on the last day of each month,
    # regardless the number of day in the month.
    every_last_day_of_month = models.BooleanField(default=False)
    # Task to operate on 4th of may and 11th of october only would be represented by
    # [{day: 4, month: 5}, {day: 11, month: 10}]
    every_year = HStoreField(null=True, blank=True)
    # Task to repeat a certain number of time during the day no matter when
    number_a_day = models.SmallIntegerField(blank=True, null=True)
    # Task to repeat a certain number of time during the week no matter when
    number_a_week = models.SmallIntegerField(blank=True, null=True)
