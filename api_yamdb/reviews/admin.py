from django.contrib import admin

from .mixins import CategoryGenreAdminMixin
from .models import Category, Comment, Genre, Review, Title


@admin.register(Category)
class CategoryAdmin(CategoryGenreAdminMixin):
    pass


@admin.register(Genre)
class GenreAdmin(CategoryGenreAdminMixin):
    pass


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'year', 'category')
    list_editable = ('year', 'category',)
    list_display_links = ('name',)
    search_fields = ('name', 'year',)
    list_filter = ('category',)
    filter_horizontal = ('genre',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'title', 'pub_date', 'score',)
    search_fields = ('author', 'title', 'text',)
    list_filter = ('pub_date', 'score',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'pub_date', 'author', 'review', 'text',)
    search_fields = ('author', 'text',)
    list_filter = ('pub_date',)


admin.site.empty_value_display = '-пусто-'
