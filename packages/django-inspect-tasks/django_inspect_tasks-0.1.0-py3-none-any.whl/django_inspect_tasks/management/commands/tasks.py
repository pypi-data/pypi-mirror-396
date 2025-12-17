import importlib

from crontask import scheduler
from django.apps import apps
from django.core.management import BaseCommand
from django.tasks import Task


class Command(BaseCommand):
    def handle(self, *args, **options):
        scheduled = {}
        tasks = {}
        for app in apps.get_app_configs():
            try:
                module = importlib.import_module(f"{app.name}.tasks")
            except ImportError:
                pass
            else:
                for key in dir(module):
                    obj = getattr(module, key)
                    if isinstance(obj, Task):
                        tasks[obj.module_path] = obj

        for job in scheduler.get_jobs():
            scheduled[job.func.__self__.module_path] = job.trigger
        for task in sorted(tasks):
            if task in scheduled:
                print(task, self.style.MIGRATE_HEADING(scheduled[task]))
            else:
                print(task)
