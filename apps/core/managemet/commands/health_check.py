from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError

class Command(BaseCommand):
    help = 'Check application health'

    def handle(self, *args, **options):
        try:
            db_conn = connections['default']
            db_conn.cursor()
            self.stdout.write(self.style.SUCCESS('Database: OK'))
        except OperationalError:
            self.stdout.write(self.style.ERROR('Database: FAILED'))
            return

        self.stdout.write(self.style.SUCCESS('Application: HEALTHY'))