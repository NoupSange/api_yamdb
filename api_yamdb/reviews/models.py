from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .constants import (
    CONFIRMATION_CODE_LENGTH,
    EMAIL_LENGTH,
    MAX_SCORE_VALUE,
    MIN_SCORE_VALUE,
    SLUG_LENGTH,
    TEXT_LENGTH,
)
from .validators import validate_year


class User(AbstractUser):

    class Role(models.TextChoices):
        USER = 'user', 'Пользователь'
        MODERATOR = 'moderator', 'Модератор'
        ADMIN = 'admin', 'Администратор'

    ROLE_MAX_LENGTH = max(len(role) for role in Role.values)

    email = models.EmailField(
        unique=True,
        max_length=EMAIL_LENGTH,
        verbose_name='Email',
    )
    bio = models.TextField(blank=True, null=True, verbose_name='Биография')
    role = models.CharField(
        max_length=ROLE_MAX_LENGTH,
        choices=Role.choices,
        default=Role.USER,
        blank=True,
        verbose_name='Роль',
    )
    confirmation_code = models.CharField(
        blank=True,
        null=True,
        max_length=CONFIRMATION_CODE_LENGTH,
        verbose_name='Код подтверждения',
    )

    @property
    def is_moderator(self):
        return self.role == self.Role.MODERATOR

    @property
    def is_admin(self):
        return (
            self.role == self.Role.ADMIN
            or self.is_staff
            or self.is_superuser
        )

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class CategoryGenreBase(models.Model):
    name = models.CharField(
        unique=True,
        max_length=TEXT_LENGTH,
        verbose_name='Наименование',
    )
    slug = models.SlugField(
        unique=True, max_length=SLUG_LENGTH, verbose_name='Слаг'
    )

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name


class Category(CategoryGenreBase):

    class Meta(CategoryGenreBase.Meta):
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Genre(CategoryGenreBase):

    class Meta(CategoryGenreBase.Meta):
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.CharField(
        max_length=TEXT_LENGTH,
        verbose_name='Название'
    )
    year = models.IntegerField(
        validators=[validate_year],
        verbose_name='Год выпуска',
        db_index=True,
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
        blank=True,
        null=True,
        verbose_name='Категория',
    )

    class Meta:
        default_related_name = 'titles'
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}, {self.year}'


class ReviewCommentBase(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    text = models.TextField(
        max_length=TEXT_LENGTH,
        verbose_name='Текст'
    )
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        abstract = True
        ordering = ('-pub_date',)


class Review(ReviewCommentBase):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение',
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        validators=[
            MinValueValidator(MIN_SCORE_VALUE),
            MaxValueValidator(MAX_SCORE_VALUE),
        ]
    )

    class Meta(ReviewCommentBase.Meta):
        default_related_name = 'reviews'
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author'), name='unique_review'
            )
        ]

    def __str__(self):
        return f'Отзыв от {self.author.username} на {self.title.name}'


class Comment(ReviewCommentBase):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв',
    )

    class Meta(ReviewCommentBase.Meta):
        default_related_name = 'comments'
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return (
            f'Комментарий от {self.author.username}'
            f'к отзыву {self.review.id}'
        )
