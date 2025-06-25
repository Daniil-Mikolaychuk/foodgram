import csv

from django.core.management.base import BaseCommand

from recipes.constants import INGREDIENTS_PATH
from recipes.models import Ingredient


class Command(BaseCommand):
    """Заполнение базы ингридиентами"""

    help = 'Импорт данных из CSV-файлов в базу данных'
    count = 0

    def handle(self, *args, **options):
        with open(INGREDIENTS_PATH, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=',')
            for string in reader:
                name, measurement_unit = string
                if name:
                    Ingredient.objects.get_or_create(
                        name=name,
                        measurement_unit=measurement_unit
                    )
