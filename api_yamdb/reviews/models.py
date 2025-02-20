from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from .constants import TEXT_LENGTH

User = get_user_model()


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
