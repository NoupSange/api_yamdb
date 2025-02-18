import datetime

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from .constants import TEXT_LENGTH
from .mixins import CategoryGenreMixin

User = get_user_model()


class Category(CategoryGenreMixin):

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Genre(CategoryGenreMixin):

    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.CharField(
        max_length=TEXT_LENGTH,
        verbose_name='Название произведения'
    )
    year = models.PositiveIntegerField(
        validators=[MaxValueValidator(datetime.date.today().year)],
        verbose_name='Год выпуска произведения'
    )
    description = models.TextField(
        max_length=TEXT_LENGTH,
        null=True,
        blank=True,
        verbose_name='Описание произведения'
    )
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        verbose_name='Жанры произведения',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория произведения',
    )

    class Meta:
        default_related_name = 'titles'
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return f'{self.name}, {self.year}'


class GenreTitle(models.Model):
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        verbose_name='Жанр произведения',
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=['genre', 'title'], name='unique_genre_title'
            ),
        )

    def __str__(self):
        return f'{self.genre} {self.title}'
