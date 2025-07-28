from django.core.management.base import BaseCommand
from api.tasks import ingest_data

class Command(BaseCommand):
    help = 'Ingests data from excel files into the database via Celery'

    def handle(self, *args, **options):
        ingest_data.delay()
        self.stdout.write(self.style.SUCCESS('Data ingestion task has been queued.'))