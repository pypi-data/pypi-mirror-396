import json
import os

from django.core.management.base import BaseCommand

from ...models import Row
from ...utils import subtitle, title


class Command(BaseCommand):
    """
    Coverts Row data from (raw) string to JSON.
    
    Initially in the development of this app, Row data was stores unprocessed.
    However, data is now directly loaded as JSON, and so this command should
    not be required. It is provided as it was already written.
    """
    help = "Covert Row data strings stored in database into JSON."

    # def add_arguments(self, parser):
    #     pass

    def handle(self, *args, **options):
        self.stdout.write(title(os.path.basename(__file__)))
        self.stdout.write(subtitle(self.help))

        counter = 0
        for row in Row.objects.all():
            if isinstance(row.data, str):
                row.data = json.loads(row.data)
                row.save()
                # print(row.id, type(row.data))
                # import sys
                # sys.exit()

            counter += 1
            if counter >= 500:
                print(".", end="")
                counter = 0
