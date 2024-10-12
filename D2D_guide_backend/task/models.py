from datetime import timedelta, date

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import ArrayField, HStoreField

from task.utils import (
    is_included, every_month_clean, remove_duplicate_from_list, check_dict_list_date_format,
    month_range)

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
    related_mot = models.ForeignKey(
        'task.MultiOccurencesTask', on_delete=models.CASCADE, null=True, blank=True)


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
    every_year = models.JSONField(default=list)
    # Task to repeat a certain number of time during the day no matter when
    number_a_day = models.SmallIntegerField(blank=True, null=True)
    # Task to repeat a certain number of time during the week no matter when
    number_a_week = models.SmallIntegerField(blank=True, null=True)

    def clean(self):
        """
        Make sure that multi occurences task fields are relevant with each other.
        Constraints are:
        - start_date must be before end_date
        - every_week integers must belong to [1,7]
        - every_month integers must belong to [1, number of days in month]
        - every_year data has the shape [{day:..., month:...},{day:..., month:...},...]
        - there can only be one of every_week, every_month, every_year, every_last_day_of_month,
        number_a_day, number_a_week that is not null or empty
        - there is at least one of every_week, every_month, every_year, every_last_day_of_month,
        number_a_day, number_a_week that is not null or empty
        """
        super().clean()
        if self.start_date >= self.end_date:
            raise ValidationError('start_date must be before end_date')
        if (self.every_week and
            not is_included(self.every_week, [*range(1,8)])):
            raise ValidationError('every_week must contain numbers in range 1,7')
        if (self.every_month and
            not every_month_clean(self.start_date, self.end_date, self.every_month)):
            raise ValidationError(
                'cannot create a date beacause of month range.'\
                'Please note that you also have the possibility to use '\
                'the every_last_day_of_month field.')
        self.every_week = remove_duplicate_from_list(self.every_week)
        self.every_month = remove_duplicate_from_list(self.every_month)
        if not check_dict_list_date_format(self.every_year):
            raise ValidationError('every_year must be a list of {year:..., month:..., day:...}')
        # Way to remove duplicate dict in list
        # https://stackoverflow.com/questions/9427163/remove-duplicate-dict-in-list-in-python
        self.every_year = [dict(t) for t in set(tuple(dic.items()) for dic in self.every_year)]
        # Check that there is exactly one of the following field that is defined:
        # every_week, every_month, every_year, every_last_day_of_month, number_a_day, number_a_week
        field_count = 0
        field_check = [
            'every_week', 'every_month', 'every_year', 'every_last_day_of_month', 'number_a_day',
            'number_a_week'
        ]
        for field_name in field_check:
            if self.__dict__[field_name]:
                field_count+=1
        if field_count != 1:
            raise ValidationError('There must be exactly one field defined among every_week, '\
                'every_month, every_year, every_last_day_of_month, number_a_day, number_a_week')

    def create_every_week_task(self):
        """
        Create task associated to this mot for every weeks between start and end dates.
        """
        running_date = self.start_date
        while running_date <= self.end_date:
            if (running_date.weekday() + 1) in self.every_week:
                DatedTask.objects.create(
                    name=self.name,
                    date= running_date,
                    related_mot=self
                )
            running_date = running_date + timedelta(days=1)

    def create_every_month_task(self):
        """
        Create task associated to this mot for every month between start and end dates.
        """
        running_date = date(year=self.start_date.year, month=self.start_date.month, day=1)
        while running_date <= self.end_date:
            for day in self.every_month:
                # Since object has been cleaned, date is supposed to exist.
                task_date = date(
                    year=running_date.year,
                    month=running_date.month,
                    day=day)
                # Handle case when every_month=[1,15] and end_date is 10th of month:
                # for this month task for the 1st must be created but not for the 15th
                if task_date <= self.end_date:
                    DatedTask.objects.create(
                        name=self.name,
                        date=task_date,
                        related_mot=self
                    )
            current_month_range = month_range(running_date.year, running_date.month)
            running_date = running_date + timedelta(days=current_month_range)
