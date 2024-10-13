from datetime import date

from django.test import TestCase

from task.models import MultiOccurencesTask, DatedTask


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

    def mot_modifications_modifies_related_tasks_every_month(self):
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
