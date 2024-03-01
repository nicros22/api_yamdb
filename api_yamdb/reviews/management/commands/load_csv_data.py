import csv

from django.conf import settings
from django.core.management import BaseCommand

from reviews.models import (Category, Comment, Genre, GenreTitle, Review,
                            Title, User)

DATA_NAMES = {
    Category: 'category.csv',
    Comment: 'comments.csv',
    Genre: 'genre.csv',
    GenreTitle: 'genre_title.csv',
    Review: 'review.csv',
    Title: 'titles.csv',
    User: 'users.csv'
}


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for model, csv_filename in DATA_NAMES.items():
            with open(f'{settings.BASE_DIR}/static/data/{csv_filename}',
                      'r',
                      encoding='utf-8') as csv_file:
                reader = csv.DictReader(csv_file)
                model.objects.bulk_create(
                    model(**data) for data in reader)
                print('Данные из csv-файла были успешно загружены')
