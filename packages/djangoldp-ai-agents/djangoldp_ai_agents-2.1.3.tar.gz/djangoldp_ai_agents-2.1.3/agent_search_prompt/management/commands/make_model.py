from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Not implemented"

    def handle(self, *args, **options):

        self.stdout.write(
            self.style.SUCCESS("Not implemented")
        )
