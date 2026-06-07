# analytics/management/commands/setup_schedule.py
from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule
import json


class Command(BaseCommand):
    help = 'Setup Celery Beat periodic tasks'

    def handle(self, *args, **kwargs):
        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=30, period=IntervalSchedule.MINUTES,
        )
        PeriodicTask.objects.update_or_create(
            name='Fetch All Topics Every 30 Minutes',
            defaults={
                'interval': schedule,
                'task': 'analytics.tasks.fetch_all_topics',
                'args': json.dumps([]),
            }
        )
        self.stdout.write(self.style.SUCCESS('Periodic tasks configured!'))