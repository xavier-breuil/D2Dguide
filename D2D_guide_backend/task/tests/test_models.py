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
                name='week_53_task',
                week_number=53,
                year=2024
            )
        # 2020 has 53 weeks, so it should not raise
        w = WeekTask.objects.create(
                name='week_53_task',
                week_number=53,
                year=2020
            )
        self.assertEqual(w.week_number, 53)
