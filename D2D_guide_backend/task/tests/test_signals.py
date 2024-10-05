from datetime import date

from django.test import TestCase
from django.core.exceptions import ValidationError

from task.models import WeekTask, MultiOccurencesTask

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

class MultiOccurencesTaskTestCase(TestCase):
    
    def test_multi_occurences_task_cleaning_date(self):
        """
        Make sure that when saving a multi occurences task, start_date and end_date
        are relevant to create one.
        """
        start = date(2024, 1, 1)
        end = date(2024, 12, 31)
        mot = MultiOccurencesTask.objects.create(
            name='start_end',
            start_date=start,
            end_date=end,
            number_a_week=5
        )
        self.assertEqual(mot.start_date, start)
        self.assertEqual(mot.end_date, end)
        with self.assertRaises(ValidationError):
            MultiOccurencesTask.objects.create(
                name='start_start',
                start_date=start,
                end_date=start,
                number_a_week=5
            )
        with self.assertRaises(ValidationError):
            MultiOccurencesTask.objects.create(
                name='end_start',
                start_date=end,
                end_date=start,
                number_a_week=5
            )

    def test_multi_occurences_task_cleaning_every_week(self):
        """
        Make sure numbers correspond to week days.
        """
        start = date(2024, 1, 1)
        end = date(2024, 12, 31)
        mot = MultiOccurencesTask.objects.create(
            name='every_week',
            start_date=start,
            end_date=end,
            every_week=[2, 5]
        )
        self.assertIn(2, mot.every_week)
        self.assertIn(5, mot.every_week)
        self.assertEqual(len(mot.every_week), 2)
        with self.assertRaises(ValidationError):
            MultiOccurencesTask.objects.create(
                name='every_week',
                start_date=start,
                end_date=start,
                every_week=[5, 8]
            )
