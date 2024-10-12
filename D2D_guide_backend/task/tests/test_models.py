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
