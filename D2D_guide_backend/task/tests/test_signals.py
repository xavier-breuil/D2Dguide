from datetime import date

from django.test import TestCase
from django.core.exceptions import ValidationError

from task.models import WeekTask, MultiOccurencesTask, DatedTask, Label

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
        day_1 = {'month': 8, 'day': 22}
        day_2 = {'month': 7, 'day': 22}
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
        error_message = 'every_year must be a list of {month:..., day:...}'
        with self.assertRaisesMessage(ValidationError, error_message):
            mot.every_year.append({'not_a_date': 42})
            mot.save()
        with self.assertRaisesMessage(ValidationError, error_message):
            mot.every_year = [{'month': 2, 'day': 30}]
            mot.save()
        # duplicate date should be removed.
        mot.every_year = [day_1, day_2, day_2]
        mot.save()
        self.assertIn(day_1, mot.every_year)
        self.assertIn(day_2, mot.every_year)
        self.assertEqual(len(mot.every_year), 2)

    def test_multi_occurences_task_single_time_field(self):
        """
        Make sure that exactly one field defined among every_week, every_month, every_year,
        every_last_day_of_month, number_a_day, number_a_week.
        """
        # Standard case should not raise
        start = date(2024, 1, 1)
        end = date(2024, 12, 31)
        day_1 = {'month': 8, 'day': 22}
        day_2 = {'month': 7, 'day': 22}
        every_year = [day_1, day_2]
        every_month = [13, 25]
        every_week = [2, 5]
        every_last_day_of_month = False
        number_a_day = 0
        number_a_week = 0
        # No field defined should raise.
        error_message = 'There must be exactly one field defined among every_week, '\
            'every_month, every_year, every_last_day_of_month, number_a_day, number_a_week'
        with self.assertRaisesMessage(ValidationError, error_message):
            MultiOccurencesTask.objects.create(
                name='mot',
                start_date=start,
                end_date=end,
            )
        # Single field define should not raise and at least two fields should raise.
        mot = MultiOccurencesTask.objects.create(
            name='mot',
            start_date=start,
            end_date=end,
            every_week=every_week
        )
        self.assertCountEqual(mot.every_week, every_week)
        mot.every_month = every_month
        with self.assertRaisesMessage(ValidationError, error_message):
            mot.save()
        mot.every_week = []
        mot.save()
        self.assertEqual(mot.every_week, [])
        self.assertCountEqual(mot.every_month, every_month)
        mot.every_year = every_year
        with self.assertRaisesMessage(ValidationError, error_message):
            mot.save()
        mot.every_month = []
        mot.save()
        self.assertEqual(mot.every_month, [])
        self.assertCountEqual(mot.every_year, every_year)
        mot.every_last_day_of_month = True
        with self.assertRaisesMessage(ValidationError, error_message):
            mot.save()
        mot.every_year = []
        mot.save()
        self.assertEqual(mot.every_year, [])
        self.assertTrue(mot.every_last_day_of_month)
        mot.number_a_day = 1
        with self.assertRaisesMessage(ValidationError, error_message):
            mot.save()
        mot.every_last_day_of_month = False
        mot.save()
        self.assertFalse(mot.every_last_day_of_month)
        self.assertEqual(mot.number_a_day, 1)
        mot.number_a_week = 5
        with self.assertRaisesMessage(ValidationError, error_message):
            mot.save()
        mot.number_a_day = None
        mot.save()
        self.assertEqual(mot.number_a_week, 5)

    def test_mot_creates_every_week_tasks(self):
        """
        Make sure that creating mot with every_week actually creates
        """
        dated_count = DatedTask.objects.count()
        start = date(2024, 7, 1)
        end = date(2024, 7, 31)
        mot = MultiOccurencesTask.objects.create(
            name='mot',
            task_name='task',
            start_date=start,
            end_date=end,
            every_week=[2, 5]
        )
        days = [2, 5, 9, 12, 16, 19, 23, 26, 30]
        dates = [date(year=2024, month=7, day=day_num) for day_num in days]
        for day in dates:
            self.assertEqual(
                DatedTask.objects.filter(
                    related_mot=mot,
                    date=day,
                    name='task'
                ).count(), 1
            )
        # Make sur no other dated tasks have been created or deleted.
        self.assertEqual(DatedTask.objects.count(), dated_count + len(days))

    def test_mot_creates_every_month_tasks(self):
        """
        Make sure that creating mot with every_month actually creates
        """
        dated_count = DatedTask.objects.count()
        start = date(2023, 10, 1)
        end = date(2024, 3, 10)
        mot = MultiOccurencesTask.objects.create(
            name='mot',
            task_name='task',
            start_date=start,
            end_date=end,
            every_month=[1, 15]
        )
        dates = [
            date(year=2023, month=10, day=1),
            date(year=2023, month=10, day=15),
            date(year=2023, month=11, day=1),
            date(year=2023, month=11, day=15),
            date(year=2023, month=12, day=1),
            date(year=2023, month=12, day=15),
            date(year=2024, month=1, day=1),
            date(year=2024, month=1, day=15),
            date(year=2024, month=2, day=1),
            date(year=2024, month=2, day=15),
            date(year=2024, month=3, day=1),
            ]
        for day in dates:
            self.assertEqual(
                DatedTask.objects.filter(
                    related_mot=mot,
                    date=day,
                    name='task'
                ).count(), 1
            )
        # Make sur no other dated tasks have been created or deleted.
        self.assertEqual(DatedTask.objects.count(), dated_count + len(dates))

    def test_mot_creates_every_last_day_of_month_tasks(self):
        """
        Make sure that creating mot with every_last_day_of_month actually creates
        """
        dated_count = DatedTask.objects.count()
        start = date(2023, 10, 1)
        end = date(2024, 3, 10)
        mot = MultiOccurencesTask.objects.create(
            name='mot',
            task_name='task',
            start_date=start,
            end_date=end,
            every_last_day_of_month=True
        )
        dates = [
            date(year=2023, month=10, day=31),
            date(year=2023, month=11, day=30),
            date(year=2023, month=12, day=31),
            date(year=2024, month=1, day=31),
            date(year=2024, month=2, day=29),
            ]
        for day in dates:
            self.assertEqual(
                DatedTask.objects.filter(
                    related_mot=mot,
                    date=day,
                    name='task'
                ).count(), 1
            )
        # Make sur no other dated tasks have been created or deleted.
        self.assertEqual(DatedTask.objects.count(), dated_count + len(dates))

    def test_mot_creates_every_year_tasks(self):
        """
        Make sure that creating mot with every_year actually creates
        """
        dated_count = DatedTask.objects.count()
        start = date(2023, 10, 1)
        end = date(2026, 6, 10)
        mot = MultiOccurencesTask.objects.create(
            name='mot',
            task_name='task',
            start_date=start,
            end_date=end,
            every_year=[{'month': 8, 'day': 22}, {'month': 5, 'day': 21}]
        )
        dates = [
            date(year=2024, month=5, day=21),
            date(year=2024, month=8, day=22),
            date(year=2025, month=5, day=21),
            date(year=2025, month=8, day=22),
            date(year=2026, month=5, day=21)
            ]
        for day in dates:
            self.assertEqual(
                DatedTask.objects.filter(
                    related_mot=mot,
                    date=day,
                    name='task'
                ).count(), 1
            )
        # Make sur no other dated tasks have been created or deleted.
        self.assertEqual(DatedTask.objects.count(), dated_count + len(dates))

    def test_mot_creates_number_a_day_tasks(self):
        """
        Make sure that creating mot with number_a_day actually creates tasks
        """
        dated_count = DatedTask.objects.count()
        start = date(2025, 1, 1)
        end = date(2025, 1, 4)
        mot = MultiOccurencesTask.objects.create(
            name='mot',
            task_name='n_a_d',
            start_date=start,
            end_date=end,
            number_a_day=2
        )
        dates = [
            date(year=2025, month=1, day=1),
            date(year=2025, month=1, day=2),
            date(year=2025, month=1, day=3),
            date(year=2025, month=1, day=4)
            ]
        for day in dates:
            self.assertEqual(
                DatedTask.objects.filter(
                    related_mot=mot,
                    date=day,
                    name='n_a_d'
                ).count(), 2
            )
        # Make sur no other dated tasks have been created or deleted.
        self.assertEqual(DatedTask.objects.count(), dated_count + len(dates) * 2)

    def test_mot_creates_number_a_week_tasks(self):
        """
        Make sure that creating mot with number_a_week actually creates tasks
        """
        week_count = WeekTask.objects.count()
        start = date(2025, 1, 1)
        end = date(2025, 1, 17)
        mot = MultiOccurencesTask.objects.create(
            name='mot',
            task_name='n_a_w',
            start_date=start,
            end_date=end,
            number_a_week=2
        )
        weeks = [
            {'week_number': 1, 'year': 2025},
            {'week_number': 2, 'year': 2025},
            {'week_number': 3, 'year': 2025}
            ]
        for week in weeks:
            self.assertEqual(
                WeekTask.objects.filter(
                    related_mot=mot,
                    week_number=week['week_number'],
                    year=week['year'],
                    name='n_a_w'
                ).count(), 2
            )
        # Make sur no other dated tasks have been created or deleted.
        self.assertEqual(WeekTask.objects.count(), week_count + len(weeks) * 2)

    def test_mot_modifications_modifies_related_tasks_label(self):
        """
        Make sure that modifying a mot modifies related tasks.
        """
        lab = Label.objects.create(name='lab')
        lab2 = Label.objects.create(name='lab2')
        dated_count = DatedTask.objects.count()
        start = date(2024, 5, 1)
        end = date(2024, 7, 24)
        mot = MultiOccurencesTask.objects.create(
            name='mot',
            task_name='task',
            start_date=start,
            end_date=end,
            every_last_day_of_month=True,
        )
        related_tasks = DatedTask.objects.filter(related_mot=mot)
        self.assertEqual(len(related_tasks), 2)
        task_1 = DatedTask.objects.get(related_mot=mot, date=date(2024, 5, 31))
        task_2 = DatedTask.objects.get(related_mot=mot, date=date(2024, 6, 30))
        self.assertEqual(task_1.label.count(), 0)
        self.assertEqual(task_2.label.count(), 0)
        # adding labels should add it to related tasks
        mot.label.add(lab)
        mot.save()
        task_1.refresh_from_db()
        self.assertEqual(task_1.label.count(), 1)
        self.assertEqual(task_1.label.first(), lab)
        task_2.refresh_from_db()
        self.assertEqual(task_2.label.count(), 1)
        self.assertEqual(task_2.label.first(), lab)
        # modifying labels should modify it on tasks
        mot.label.set([lab2])
        task_1.refresh_from_db()
        self.assertEqual(task_1.label.count(), 1)
        self.assertEqual(task_1.label.first(), lab2)
        task_2.refresh_from_db()
        self.assertEqual(task_2.label.count(), 1)
        self.assertEqual(task_2.label.first(), lab2)
        # removing label should remove it from tasks
        mot.label.remove(lab2)
        task_1.refresh_from_db()
        self.assertEqual(task_1.label.count(), 0)
        task_2.refresh_from_db()
        self.assertEqual(task_2.label.count(), 0)
