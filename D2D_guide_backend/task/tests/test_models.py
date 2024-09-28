from django.test import TestCase
from django.core.exceptions import ValidationError

from task.models import WeekTask

class WeekTaskTestCase(TestCase):

    def test_week_validation(self):
        """
        Make sure a week task cannot be created with an unrelevant week number.
        """
        with self.assertRaises(ValidationError):
            WeekTask.objects.create(
                name='week_89_task',
                week_number=89,
                year=2024
            )
