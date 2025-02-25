import os
import csv
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime
from reviews.models import Category, Genre, Title, Review, Comment, User


class Command(BaseCommand):
    help = 'Импортирует данные из CSV файлов'

    def add_arguments(self, parser):
        parser.add_argument(
            'folder_path', type=str, help='Папка с CSV файлами'
        )

    def handle(self, *args, **kwargs):
        folder_path = kwargs['folder_path']
        if not os.path.isdir(folder_path):
            self.stdout.write(self.style.ERROR('Папка не существует'))
            return

        self.import_categories(os.path.join(folder_path, 'category.csv'))
        self.import_genres(os.path.join(folder_path, 'genre.csv'))
        self.import_users(os.path.join(folder_path, 'users.csv'))
        self.import_titles(os.path.join(folder_path, 'titles.csv'))
        self.import_genre_titles(os.path.join(folder_path, 'genre_title.csv'))
        self.import_reviews(os.path.join(folder_path, 'review.csv'))
        self.import_comments(os.path.join(folder_path, 'comments.csv'))

        self.stdout.write(self.style.SUCCESS(
            '✅ Все данные успешно импортированы!')
        )

    def import_categories(self, filepath):
        with open(filepath, encoding='utf-8') as file:
            for row in csv.DictReader(file):
                Category.objects.update_or_create(
                    id=row['id'],
                    defaults={'name': row['name'], 'slug': row['slug']}
                )

    def import_genres(self, filepath):
        with open(filepath, encoding='utf-8') as file:
            for row in csv.DictReader(file):
                Genre.objects.update_or_create(
                    id=row['id'],
                    defaults={'name': row['name'], 'slug': row['slug']}
                )

    def import_users(self, filepath):
        with open(filepath, encoding='utf-8') as file:
            for row in csv.DictReader(file):
                User.objects.update_or_create(
                    id=row['id'],
                    defaults={
                        'username': row['username'],
                        'email': row['email'],
                        'role': row['role'],
                        'bio': row.get('bio', ''),
                        'first_name': row.get('first_name', ''),
                        'last_name': row.get('last_name', ''),
                    }
                )

    def import_titles(self, filepath):
        with open(filepath, encoding='utf-8') as file:
            for row in csv.DictReader(file):
                category = Category.objects.filter(id=row['category']).first()
                Title.objects.update_or_create(
                    id=row['id'],
                    defaults={
                        'name': row['name'],
                        'year': row['year'],
                        'category': category
                    }
                )

    def import_genre_titles(self, filepath):
        with open(filepath, encoding='utf-8') as file:
            for row in csv.DictReader(file):
                title = Title.objects.get(id=row['title_id'])
                genre = Genre.objects.get(id=row['genre_id'])
                title.genre.add(genre)

    def import_reviews(self, filepath):
        with open(filepath, encoding='utf-8') as file:
            for row in csv.DictReader(file):
                title = Title.objects.get(id=row['title_id'])
                author = User.objects.get(id=row['author'])
                Review.objects.update_or_create(
                    id=row['id'],
                    defaults={
                        'title': title,
                        'text': row['text'],
                        'author': author,
                        'score': row['score'],
                        'pub_date': parse_datetime(row['pub_date'])
                    }
                )

    def import_comments(self, filepath):
        with open(filepath, encoding='utf-8') as file:
            for row in csv.DictReader(file):
                review = Review.objects.get(id=row['review_id'])
                author = User.objects.get(id=row['author'])
                Comment.objects.update_or_create(
                    id=row['id'],
                    defaults={
                        'review': review,
                        'text': row['text'],
                        'author': author,
                        'pub_date': parse_datetime(row['pub_date'])
                    }
                )
