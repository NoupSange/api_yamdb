from django.contrib import admin
from django.db import models

from .constants import SLUG_LENGTH, TEXT_LENGTH


class CategoryGenreMixin(models.Model):
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

    def __str__(self):
        return self.name


class CategoryGenreAdminMixin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
