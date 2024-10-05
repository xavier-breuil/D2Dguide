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
        error_message = 'start_date must be before end_date'
        with self.assertRaisesMessage(ValidationError, error_message):
            MultiOccurencesTask.objects.create(
                name='start_start',
                start_date=start,
                end_date=start,
                number_a_week=5
            )
        with self.assertRaisesMessage(ValidationError, error_message):
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
        error_message = 'every_week must contain numbers in range 1,7'
        with self.assertRaisesMessage(ValidationError, error_message):
            MultiOccurencesTask.objects.create(
                name='every_week',
                start_date=start,
                end_date=end,
                every_week=[5, 8]
            )
        # Adding a duplicate day in every_week should not modify the field.
        mot.every_week.append(2)
        mot.save()
        self.assertIn(2, mot.every_week)
        self.assertIn(5, mot.every_week)
        self.assertEqual(len(mot.every_week), 2)

    def test_multi_occurences_task_cleaning_every_month(self):
        """
        Make sure numbers correspond to month days.
        """
        # Standard case should not raise
        start = date(2024, 1, 1)
        end = date(2024, 12, 31)
        mot = MultiOccurencesTask.objects.create(
            name='every_month',
            start_date=start,
            end_date=end,
            every_month=[12, 21]
        )
        self.assertIn(12, mot.every_month)
        self.assertIn(21, mot.every_month)
        self.assertEqual(len(mot.every_month), 2)
        error_message = 'cannot create a date beacause of month range.'\
            'Please note that you also have the possibility to use '\
            'the every_last_day_of_month field.'
        # As february has only 29 days in 2024, this should raise
        with self.assertRaisesMessage(ValidationError, error_message):
            mot.every_month.append(30)
            mot.save()
        # if february is not included, this should be possible.
        mot.start_date = date(2024, 3, 1)
        mot.every_month.append(12)
        mot.save()
        self.assertIn(12, mot.every_month)
        self.assertIn(21, mot.every_month)
        self.assertIn(30, mot.every_month)
        self.assertEqual(len(mot.every_month), 3)

    def test_multi_occurences_task_cleaning_every_year(self):
        """
        Make sure every_year correspond to a date list.
        """
        # Standard case should not raise
        start = date(2024, 1, 1)
        end = date(2024, 12, 31)
        day_1 = {'year': 2024, 'month': 8, 'day': 22}
        day_2 = {'year': 2024, 'month': 7, 'day': 22}
        mot = MultiOccurencesTask.objects.create(
            name='every_month',
            start_date=start,
            end_date=end,
            every_year=[day_1, day_2]
        )
        self.assertIn(day_1, mot.every_year)
        self.assertIn(day_2, mot.every_year)
        self.assertEqual(len(mot.every_year), 2)
        # Error should be raised when uncorrect dict for date.
        error_message = 'every_year must be a list of {year:..., month:..., day:...}'
        with self.assertRaisesMessage(ValidationError, error_message):
            mot.every_year.append({'not_a_date': 42})
            mot.save()
        with self.assertRaisesMessage(ValidationError, error_message):
            mot.every_year = [{'year': 2024, 'month': 2, 'day': 30}]
            mot.save()
        # duplicate date should be removed.
        mot.every_year = [day_1, day_2, day_2]
        mot.save()
        self.assertIn(day_1, mot.every_year)
        self.assertIn(day_2, mot.every_year)
        self.assertEqual(len(mot.every_year), 2)
