from django.conf import settings
from django.core.management import BaseCommand, call_command

from varanus.server.models import Site


class Command(BaseCommand):
    help = "Migrates all Site schemas."

    def add_arguments(self, parser):
        parser.add_argument("sites", nargs="*")

    def handle(self, *args, **options):
        call_command("migrate", database=settings.VARANUS_DB_ALIAS)
        qs = Site.objects.all()
        if sites := options["sites"]:
            qs = qs.filter(slug__in=sites)
        for site in qs:
            print(f"*** Migrating {site.schema_name}")
            site.ensure_schema()
