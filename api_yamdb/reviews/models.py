import datetime
from enum import Enum

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .constants import (
    CONFIRMATION_CODE_LENGTH, EMAIL_LENGTH, ROLE_LENGTH, TEXT_LENGTH
)
from .mixins import CategoryGenreMixin


class User(AbstractUser):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"

    ROLE_CHOICES = (
        (USER, "Пользователь"),
        (MODERATOR, "Модератор"),
        (ADMIN, "Админ")
    )

    email = models.EmailField(
        unique=True,
        blank=False,
        null=False,
        verbose_name='Почта',
        max_length=EMAIL_LENGTH,
    )
    bio = models.TextField(null=True, blank=True, verbose_name='Биография')
    role = models.CharField(
        max_length=ROLE_LENGTH,
        choices=ROLE_CHOICES,
        default=USER,
        verbose_name='Роль',
    )
    confirmation_code = models.CharField(
        max_length=CONFIRMATION_CODE_LENGTH, null=True,
        verbose_name='Код подтверждения',
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return self.username


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
        verbose_name='Название'
    )
    year = models.PositiveIntegerField(
        validators=[MaxValueValidator(datetime.date.today().year)],
        verbose_name='Год выпуска'
    )
    description = models.TextField(
        max_length=TEXT_LENGTH,
        null=True,
        blank=True,
        verbose_name='Описание'
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанры',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
    )

    class Meta:
        default_related_name = 'titles'
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('id',)

    def __str__(self):
        return f'{self.name}, {self.year}'


class Review(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение',
    )
    text = models.TextField(verbose_name='Текст отзыва')
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
        db_index=True
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )

    class Meta:
        default_related_name = 'reviews'
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author'), name='unique_review'
            )
        ]

    def __str__(self):
        return f'Отзыв от {self.author.username} на {self.title.name}'


class Comment(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв',
    )
    text = models.TextField(
        max_length=TEXT_LENGTH,
        verbose_name='Текст комментария'
    )
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        default_related_name = 'comments'
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('pub_date',)

    def __str__(self):
        return (
            f'Комментарий от {self.author.username}'
            f'к отзыву {self.review.id}'
        )
