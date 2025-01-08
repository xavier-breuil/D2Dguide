from datetime import date

from django.test import TestCase

from task.models import MultiOccurencesTask, DatedTask, WeekTask


class MultiOccurencesTaskTestCase(TestCase):

    def test_mot_delete(self):
        """
        Make sure that deleting a mot delete related tasks.
        This is test only on mot with every_week (and not every_month,...) since this mechanism
        is not related to objects field.
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
        self.assertEqual(DatedTask.objects.count(), dated_count + len(days))
        mot.delete()
        self.assertEqual(DatedTask.objects.count(), dated_count)

    def test_mot_modifications_modifies_related_tasks_every_month(self):
        """
        Make sure that modifying a mot modifies related tasks.
        """
        dated_count = DatedTask.objects.count()
        start = date(2024, 7, 1)
        end = date(2024, 7, 31)
        mot = MultiOccurencesTask.objects.create(
            name='mot',
            task_name='task',
            start_date=start,
            end_date=end,
            every_month=[2, 5]
        )
        related_tasks = DatedTask.objects.filter(related_mot=mot)
        self.assertEqual(len(related_tasks), 2)
        task_1 = related_tasks[0]
        task_2 = related_tasks[1]
        # modifying name doessn't change
        mot.name = 'rename'
        mot.save()
        # make sure thas dated tasks name haven't change
        related_tasks = DatedTask.objects.filter(related_mot=mot)
        self.assertEqual(len(related_tasks), 2)
        self.assertTrue(task_1.id in related_tasks.values_list('id', flat=True))
        self.assertTrue(task_2.id in related_tasks.values_list('id', flat=True))
        task_1_bis = DatedTask.objects.get(id=task_1.id)
        task_2_bis = DatedTask.objects.get(id=task_2.id)
        self.assertEqual(task_1.name, task_1_bis.name)
        self.assertEqual(task_2.name, task_2_bis.name)
        # increasing start date should delete appropriate tasks
        mot.start_date = date(2024, 7, 3)
        mot.save()
        related_tasks = DatedTask.objects.filter(related_mot=mot)
        self.assertEqual(len(related_tasks), 1)
        self.assertTrue(task_2.id in related_tasks.values_list('id', flat=True))
        # decreasing end date should delete appropriate tasks
        mot.end_date = date(2024, 7, 4)
        mot.save()
        self.assertFalse(DatedTask.objects.filter(related_mot=mot).exists())
        # decreasing start_date shoul create new tasks
        mot.start_date = date(2024, 6, 1)
        mot.save()
        related_tasks = DatedTask.objects.filter(related_mot=mot)
        self.assertEqual(len(related_tasks), 3)
        dates = related_tasks.values_list('date', flat=True)
        self.assertTrue(date(2024, 6, 2) in dates)
        self.assertTrue(date(2024, 6, 5) in dates)
        self.assertTrue(date(2024, 7, 2) in dates)
        # increasing end_date should create new tasks
        mot.end_date = date(2024, 7, 31)
        mot.save()
        related_tasks = DatedTask.objects.filter(related_mot=mot)
        self.assertEqual(len(related_tasks), 4)
        dates = related_tasks.values_list('date', flat=True)
        self.assertTrue(date(2024, 6, 2) in dates)
        self.assertTrue(date(2024, 6, 5) in dates)
        self.assertTrue(date(2024, 7, 2) in dates)
        self.assertTrue(date(2024, 7, 5) in dates)
        # Changing reccurences should delete and create new tasks.
        mot.every_month = [12, 15]
        mot.save()
        # make sure previous task have been deleted
        for task in related_tasks:
            self.assertFalse(DatedTask.objects.filter(id=task.id))
        # make sure new task have been created.
        related_tasks = DatedTask.objects.filter(related_mot=mot)
        self.assertEqual(len(related_tasks), 4)
        dates = related_tasks.values_list('date', flat=True)
        self.assertTrue(date(2024, 6, 12) in dates)
        self.assertTrue(date(2024, 6, 15) in dates)
        self.assertTrue(date(2024, 7, 12) in dates)
        self.assertTrue(date(2024, 7, 15) in dates)

    def test_mot_modifications_modifies_related_tasks_every_week(self):
        """
        Make sure that modifying a mot modifies related tasks.
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
        # increasing start date should delete appropriate tasks
        mot.start_date = date(2024, 7, 6)
        mot.save()
        days = [9, 12, 16, 19, 23, 26, 30]
        dates = [date(year=2024, month=7, day=day_num) for day_num in days]
        for day in dates:
            self.assertEqual(
                DatedTask.objects.filter(
                    related_mot=mot,
                    date=day,
                    name='task'
                ).count(), 1
            )
        self.assertEqual(DatedTask.objects.count(), dated_count + len(days))
        # decreasing end date should delete appropriate tasks
        mot.end_date = date(2024, 7, 20)
        mot.save()
        days = [9, 12, 16, 19]
        dates = [date(year=2024, month=7, day=day_num) for day_num in days]
        for day in dates:
            self.assertEqual(
                DatedTask.objects.filter(
                    related_mot=mot,
                    date=day,
                    name='task'
                ).count(), 1
            )
        self.assertEqual(DatedTask.objects.count(), dated_count + len(days))
        # decreasing start_date shoul create new tasks
        mot.start_date = date(2024, 7, 1)
        mot.save()
        days = [2, 5, 9, 12, 16, 19]
        dates = [date(year=2024, month=7, day=day_num) for day_num in days]
        for day in dates:
            self.assertEqual(
                DatedTask.objects.filter(
                    related_mot=mot,
                    date=day,
                    name='task'
                ).count(), 1
            )
        self.assertEqual(DatedTask.objects.count(), dated_count + len(days))
        # increasing end_date should create new tasks
        mot.end_date = date(2024, 7, 31)
        mot.save()
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
        self.assertEqual(DatedTask.objects.count(), dated_count + len(days))
        # Evaluate queryset to store the ids of the objects that must be deleted
        related_tasks = list(DatedTask.objects.filter(related_mot=mot))
        # Changing reccurences should delete and create new tasks.
        mot.every_week = [3]
        mot.save()
        # make sure previous task have been deleted
        for task in related_tasks:
            self.assertFalse(DatedTask.objects.filter(id=task.id).exists())
        # make sure new task have been created.
        days = [3, 10, 17, 24, 31]
        dates = [date(year=2024, month=7, day=day_num) for day_num in days]
        for day in dates:
            self.assertEqual(
                DatedTask.objects.filter(
                    related_mot=mot,
                    date=day,
                    name='task'
                ).count(), 1
            )
        self.assertEqual(DatedTask.objects.count(), dated_count + len(days))

    def test_mot_modifications_modifies_related_tasks_every_last_day_of_month(self):
        """
        Make sure that modifying a mot modifies related tasks.
        """
        dated_count = DatedTask.objects.count()
        start = date(2024, 5, 1)
        end = date(2024, 7, 31)
        mot = MultiOccurencesTask.objects.create(
            name='mot',
            task_name='task',
            start_date=start,
            end_date=end,
            every_last_day_of_month=True
        )
        related_tasks = DatedTask.objects.filter(related_mot=mot)
        self.assertEqual(len(related_tasks), 3)
        task_1 = DatedTask.objects.get(related_mot=mot, date=date(2024, 5, 31))
        task_2 = DatedTask.objects.get(related_mot=mot, date=date(2024, 6, 30))
        task_3 = DatedTask.objects.get(related_mot=mot, date=date(2024, 7, 31))
        # increasing start date should delete appropriate tasks
        mot.start_date = date(2024, 6, 1)
        mot.save()
        related_tasks = DatedTask.objects.filter(related_mot=mot)
        self.assertEqual(len(related_tasks), 2)
        self.assertTrue(task_2.id in related_tasks.values_list('id', flat=True))
        self.assertTrue(task_3.id in related_tasks.values_list('id', flat=True))
        # decreasing end date should delete appropriate tasks
        mot.end_date = date(2024, 7, 4)
        mot.save()
        related_tasks = DatedTask.objects.filter(related_mot=mot)
        self.assertEqual(len(related_tasks), 1)
        self.assertTrue(task_2.id in related_tasks.values_list('id', flat=True))
        # decreasing start_date shoul create new tasks
        mot.start_date = date(2024, 5, 1)
        mot.save()
        related_tasks = DatedTask.objects.filter(related_mot=mot)
        self.assertEqual(len(related_tasks), 2)
        # would raise if doesn't exist
        task_1_bis = DatedTask.objects.get(related_mot=mot, date=date(2024, 5, 31))
        self.assertTrue(task_2.id in related_tasks.values_list('id', flat=True))
        # increasing end_date should create new tasks
        mot.end_date = date(2024, 7, 31)
        mot.save()
        related_tasks = DatedTask.objects.filter(related_mot=mot)
        self.assertEqual(len(related_tasks), 3)
        task_3_bis = DatedTask.objects.get(related_mot=mot, date=date(2024, 7, 31))
        self.assertTrue(task_1_bis.id in related_tasks.values_list('id', flat=True))
        self.assertTrue(task_2.id in related_tasks.values_list('id', flat=True))
        # Changing reccurences should delete and create new tasks.
        mot.every_month = [28]
        mot.every_last_day_of_month = False
        mot.save()
        # make sure previous task have been deleted
        for task in related_tasks:
            self.assertFalse(DatedTask.objects.filter(id=task.id))
        # make sure new task have been created.
        related_tasks = DatedTask.objects.filter(related_mot=mot)
        self.assertEqual(len(related_tasks), 3)
        dates = related_tasks.values_list('date', flat=True)
        self.assertTrue(date(2024, 5, 28) in dates)
        self.assertTrue(date(2024, 6, 28) in dates)
        self.assertTrue(date(2024, 7, 28) in dates)

    def test_mot_modifications_modifies_related_tasks_every_year(self):
        """
        Make sure that modifying a mot modifies related tasks.
        """
        dated_count = DatedTask.objects.count()
        start = date(2024, 1, 1)
        end = date(2027, 7, 31)
        mot = MultiOccurencesTask.objects.create(
            name='mot',
            task_name='task',
            start_date=start,
            end_date=end,
            every_year=[{'month': 8, 'day': 22}]
        )
        date_1 = date(2024, 8, 22)
        date_2 = date(2025, 8, 22)
        date_3 = date(2026, 8, 22)
        related_tasks = DatedTask.objects.filter(related_mot=mot)
        self.assertEqual(len(related_tasks), 3)
        self.assertTrue(
            date_1 in DatedTask.objects.filter(related_mot=mot).values_list('date', flat=True))
        self.assertTrue(
            date_2 in DatedTask.objects.filter(related_mot=mot).values_list('date', flat=True))
        self.assertTrue(
            date_3 in DatedTask.objects.filter(related_mot=mot).values_list('date', flat=True))
        task_1 = DatedTask.objects.get(related_mot=mot, date=date_1)
        task_2 = DatedTask.objects.get(related_mot=mot, date=date_2)
        task_3 = DatedTask.objects.get(related_mot=mot, date=date_3)
        # increasing start date should delete appropriate tasks
        mot.start_date = date(2025, 1, 1)
        mot.save()
        self.assertEqual(DatedTask.objects.filter(related_mot=mot).count(), 2)
        self.assertTrue(
            task_2.id in DatedTask.objects.filter(related_mot=mot).values_list('id', flat=True))
        self.assertTrue(
            task_3.id in DatedTask.objects.filter(related_mot=mot).values_list('id', flat=True))
        # decreasing end date should delete appropriate tasks
        mot.end_date = date(2026, 7, 4)
        mot.save()
        self.assertEqual(DatedTask.objects.filter(related_mot=mot).count(), 1)
        self.assertTrue(
            task_2.id in DatedTask.objects.filter(related_mot=mot).values_list('id', flat=True))
        # decreasing start_date shoul create new tasks
        mot.start_date = date(2024, 6, 1)
        mot.save()
        self.assertEqual(DatedTask.objects.filter(related_mot=mot).count(), 2)
        self.assertTrue(
            task_2.id in DatedTask.objects.filter(related_mot=mot).values_list('id', flat=True))
        task_1_bis = DatedTask.objects.get(related_mot=mot, date=date_1)
        # increasing end_date should create new tasks
        mot.end_date = date(2027, 7, 31)
        mot.save()
        self.assertEqual(DatedTask.objects.filter(related_mot=mot).count(), 3)
        self.assertTrue(
            task_1_bis.id in DatedTask.objects.filter(related_mot=mot).values_list(
                'id', flat=True))
        self.assertTrue(
            task_2.id in DatedTask.objects.filter(related_mot=mot).values_list('id', flat=True))
        task_3_bis = DatedTask.objects.get(related_mot=mot, date=date_3)
        # Changing reccurences should delete and create new tasks.
        mot.every_year = [{'month': 5, 'day': 21}]
        mot.save()
        # make sure previous task have been deleted
        for task in [task_1_bis, task_2, task_3_bis]:
            self.assertFalse(DatedTask.objects.filter(id=task.id))
        # make sure new task have been created.
        related_tasks = DatedTask.objects.filter(related_mot=mot)
        self.assertEqual(len(related_tasks), 3)
        dates = related_tasks.values_list('date', flat=True)
        self.assertTrue(date(2025, 5, 21) in dates)
        self.assertTrue(date(2026, 5, 21) in dates)
        self.assertTrue(date(2027, 5, 21) in dates)

    def test_mot_modifications_modifies_related_tasks_name(self):
        """
        Make sure that modifying a mot modifies related tasks name.
        """
        dated_count = DatedTask.objects.count()
        start = date(2024, 1, 1)
        end = date(2027, 7, 31)
        mot = MultiOccurencesTask.objects.create(
            name='mot',
            task_name='task',
            start_date=start,
            end_date=end,
            every_year=[{'month': 8, 'day': 22}]
        )
        date_1 = date(2024, 8, 22)
        date_2 = date(2025, 8, 22)
        date_3 = date(2026, 8, 22)
        related_tasks = DatedTask.objects.filter(related_mot=mot)
        self.assertEqual(len(related_tasks), 3)
        self.assertTrue(
            date_1 in DatedTask.objects.filter(related_mot=mot).values_list('date', flat=True))
        self.assertTrue(
            date_2 in DatedTask.objects.filter(related_mot=mot).values_list('date', flat=True))
        self.assertTrue(
            date_3 in DatedTask.objects.filter(related_mot=mot).values_list('date', flat=True))
        task_1 = DatedTask.objects.get(related_mot=mot, date=date_1)
        task_2 = DatedTask.objects.get(related_mot=mot, date=date_2)
        task_3 = DatedTask.objects.get(related_mot=mot, date=date_3)
        # changing task_name chould change tasks names
        mot.task_name = 'new_name'
        mot.save()
        task_1.refresh_from_db()
        self.assertEqual(task_1.name, 'new_name')
        task_2.refresh_from_db()
        self.assertEqual(task_2.name, 'new_name')
        task_3.refresh_from_db()
        self.assertEqual(task_3.name, 'new_name')

    def test_mot_modifications_modifies_related_tasks_number_a_day(self):
        """
        Make sure that modifying a mot modifies related tasks.
        """
        dated_count = DatedTask.objects.count()
        start = date(2025, 1, 1)
        end = date(2025, 1, 3)
        mot = MultiOccurencesTask.objects.create(
            name='mot',
            task_name='nad',
            start_date=start,
            end_date=end,
            number_a_day=2
        )
        related_tasks = DatedTask.objects.filter(related_mot=mot)
        self.assertEqual(len(related_tasks), 6)
        task_1 = related_tasks[0]
        task_2 = related_tasks[1]
        task_3 = related_tasks[2]
        task_4 = related_tasks[3]
        task_5 = related_tasks[4]
        task_6 = related_tasks[5]
        # modifying name doesn't change
        mot.name = 'rename'
        mot.save()
        # make sure thas dated tasks name haven't change
        related_tasks = DatedTask.objects.filter(related_mot=mot)
        self.assertEqual(len(related_tasks), 6)
        self.assertTrue(task_1.id in related_tasks.values_list('id', flat=True))
        self.assertTrue(task_2.id in related_tasks.values_list('id', flat=True))
        self.assertTrue(task_3.id in related_tasks.values_list('id', flat=True))
        self.assertTrue(task_4.id in related_tasks.values_list('id', flat=True))
        self.assertTrue(task_5.id in related_tasks.values_list('id', flat=True))
        self.assertTrue(task_6.id in related_tasks.values_list('id', flat=True))
        task_1_bis = DatedTask.objects.get(id=task_1.id)
        task_2_bis = DatedTask.objects.get(id=task_2.id)
        task_3_bis = DatedTask.objects.get(id=task_3.id)
        task_4_bis = DatedTask.objects.get(id=task_4.id)
        task_5_bis = DatedTask.objects.get(id=task_5.id)
        task_6_bis = DatedTask.objects.get(id=task_6.id)
        self.assertEqual(task_1.name, task_1_bis.name)
        self.assertEqual(task_2.name, task_2_bis.name)
        self.assertEqual(task_3.name, task_3_bis.name)
        self.assertEqual(task_4.name, task_4_bis.name)
        self.assertEqual(task_5.name, task_5_bis.name)
        self.assertEqual(task_6.name, task_6_bis.name)
        # increasing start date should delete appropriate tasks
        mot.start_date = date(2025, 1, 2)
        mot.save()
        related_tasks = DatedTask.objects.filter(related_mot=mot)
        self.assertEqual(len(related_tasks), 4)
        self.assertTrue(task_3.id in related_tasks.values_list('id', flat=True))
        self.assertTrue(task_4.id in related_tasks.values_list('id', flat=True))
        self.assertTrue(task_5.id in related_tasks.values_list('id', flat=True))
        self.assertTrue(task_6.id in related_tasks.values_list('id', flat=True))
        # increasing end_date should create new tasks
        mot.end_date = date(2025, 1, 4)
        mot.save()
        related_tasks = DatedTask.objects.filter(related_mot=mot)
        self.assertEqual(len(related_tasks), 6)
        dates = related_tasks.values_list('date', flat=True)
        self.assertTrue(date(2025, 1, 2) in dates)
        self.assertTrue(date(2025, 1, 3) in dates)
        self.assertTrue(date(2025, 1, 4) in dates)
        # decreasing end date should delete appropriate tasks
        mot.end_date = date(2025, 1, 3)
        mot.save()
        self.assertEqual(DatedTask.objects.filter(related_mot=mot).count(), 4)
        dates = related_tasks.values_list('date', flat=True)
        self.assertTrue(date(2025, 1, 2) in dates)
        self.assertTrue(date(2025, 1, 3) in dates)
        # decreasing start_date should create new tasks
        mot.start_date = date(2025, 1, 1)
        mot.save()
        related_tasks = DatedTask.objects.filter(related_mot=mot)
        self.assertEqual(len(related_tasks), 6)
        dates = related_tasks.values_list('date', flat=True)
        self.assertTrue(date(2025, 1, 1) in dates)
        self.assertTrue(date(2025, 1, 2) in dates)
        self.assertTrue(date(2025, 1, 3) in dates)
        # Changing reccurences should delete and create new tasks.
        mot.number_a_day = 3
        mot.save()
        # make sure previous task have been deleted
        for task in related_tasks:
            self.assertFalse(DatedTask.objects.filter(id=task.id))
        # make sure new task have been created.
        related_tasks = DatedTask.objects.filter(related_mot=mot)
        self.assertEqual(len(related_tasks), 9)
        dates = related_tasks.values_list('date', flat=True)
        self.assertTrue(date(2025, 1, 1) in dates)
        self.assertTrue(date(2025, 1, 2) in dates)
        self.assertTrue(date(2025, 1, 3) in dates)

    def test_mot_modifications_modifies_related_tasks_number_a_week(self):
        """
        Make sure that modifying a mot modifies related tasks.
        """
        week_count = WeekTask.objects.count()
        start = date(2025, 1, 1)
        end = date(2025, 1, 17)
        mot = MultiOccurencesTask.objects.create(
            name='mot',
            task_name='task',
            start_date=start,
            end_date=end,
            number_a_week=2
        )
        weeks = [1, 2, 3]
        for week in weeks:
            self.assertEqual(
                WeekTask.objects.filter(
                    related_mot=mot,
                    week_number=week,
                    year=2025,
                    name='task'
                ).count(), 2
            )
        # Make sur no other dated tasks have been created or deleted.
        self.assertEqual(WeekTask.objects.count(), week_count + len(weeks) * 2)
        # increasing start date should delete appropriate tasks
        mot.start_date = date(2025, 1, 8)
        mot.save()
        weeks = [2,3]
        for week in weeks:
            self.assertEqual(
                WeekTask.objects.filter(
                    related_mot=mot,
                    week_number=week,
                    year=2025,
                    name='task'
                ).count(), 2
            )
        self.assertEqual(WeekTask.objects.count(), week_count + len(weeks) * 2)
        # decreasing end date should delete appropriate tasks
        mot.end_date = date(2025, 1, 12)
        mot.save()
        weeks = [2]
        for week in weeks:
            self.assertEqual(
                WeekTask.objects.filter(
                    related_mot=mot,
                    week_number=week,
                    year=2025,
                    name='task'
                ).count(), 2
            )
        self.assertEqual(WeekTask.objects.count(), week_count + len(weeks) * 2)
        # decreasing start_date but still in the same week should not create new tasks
        mot.start_date = date(2025, 1, 6)
        mot.save()
        weeks = [2]
        for week in weeks:
            self.assertEqual(
                WeekTask.objects.filter(
                    related_mot=mot,
                    week_number=week,
                    year=2025,
                    name='task'
                ).count(), 2
            )
        self.assertEqual(WeekTask.objects.count(), week_count + len(weeks) * 2)
        # decreasing start_date to another week should create new tasks
        mot.start_date = date(2025, 1, 4)
        mot.save()
        weeks = [1, 2]
        for week in weeks:
            self.assertEqual(
                WeekTask.objects.filter(
                    related_mot=mot,
                    week_number=week,
                    year=2025,
                    name='task'
                ).count(), 2
            )
        self.assertEqual(WeekTask.objects.count(), week_count + len(weeks) * 2)
        # increasing end_date to another week should create new tasks
        mot.end_date = date(2025, 1, 15)
        mot.save()
        weeks = [1, 2, 3]
        for week in weeks:
            self.assertEqual(
                WeekTask.objects.filter(
                    related_mot=mot,
                    week_number=week,
                    year=2025,
                    name='task'
                ).count(), 2
            )
        self.assertEqual(WeekTask.objects.count(), week_count + len(weeks) * 2)
        # increasing end_date to the same week should not create new tasks
        mot.end_date = date(2025, 1, 16)
        mot.save()
        weeks = [1, 2, 3]
        for week in weeks:
            self.assertEqual(
                WeekTask.objects.filter(
                    related_mot=mot,
                    week_number=week,
                    year=2025,
                    name='task'
                ).count(), 2
            )
        self.assertEqual(WeekTask.objects.count(), week_count + len(weeks) * 2)
        # Evaluate queryset to store the ids of the objects that must be deleted
        related_tasks = list(WeekTask.objects.filter(related_mot=mot))
        # Changing reccurences should delete and create new tasks.
        mot.number_a_week = 1
        mot.save()
        # make sure previous task have been deleted
        for task in related_tasks:
            self.assertFalse(WeekTask.objects.filter(id=task.id).exists())
        # make sure new task have been created.
        weeks = [1, 2, 3]
        for week in weeks:
            self.assertEqual(
                WeekTask.objects.filter(
                    related_mot=mot,
                    week_number=week,
                    year=2025,
                    name='task'
                ).count(), 1
            )
        self.assertEqual(WeekTask.objects.count(), week_count + len(weeks))
