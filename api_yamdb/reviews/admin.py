from django.contrib import admin

from .mixins import AdminMixin, CategoryGenreAdminMixin
from .models import Category, Comment, Genre, Review, Title


@admin.register(Category)
class CategoryAdmin(CategoryGenreAdminMixin):
    pass


@admin.register(Genre)
class GenreAdmin(CategoryGenreAdminMixin):
    pass


@admin.register(Title)
class TitleAdmin(AdminMixin):
    list_display = ('pk', 'name', 'year', 'category',)
    search_fields = ('name', 'year',)
    list_filter = ('genre', 'category',)


@admin.register(Review)
class ReviewAdmin(AdminMixin):
    list_display = ('pk', 'author', 'title', 'pub_date', 'score',)
    search_fields = ('author', 'title', 'text',)
    list_filter = ('pub_date', 'score',)


@admin.register(Comment)
class CommentAdmin(AdminMixin):
    list_display = ('pub_date', 'author', 'review', 'text',)
    search_fields = ('author', 'text',)
    list_filter = ('pub_date',)
