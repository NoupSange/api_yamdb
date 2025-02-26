from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from .models import Category, Comment, Genre, Review, Title

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('role', 'bio', 'count_reviews', 'count_comments')}),
    )
    list_display = (
        'username',
        'email',
        'role',
        'is_staff',
        'count_reviews',
        'count_comments',
    )
    readonly_fields = ('count_reviews', 'count_comments')

    @admin.display(description='Кол-во отзывов')
    def count_reviews(self, obj):
        return len(obj.reviews.all())

    @admin.display(description='Кол-во комментариев')
    def count_comments(self, obj):
        return len(obj.comments.all())


class CategoryGenreAdminBase(admin.ModelAdmin):
    list_display = ('name', 'slug',)


@admin.register(Category)
class CategoryAdmin(CategoryGenreAdminBase):
    pass


@admin.register(Genre)
class GenreAdmin(CategoryGenreAdminBase):
    pass


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'year', 'category', 'genre_list')
    list_editable = ('year', 'category',)
    list_display_links = ('name',)
    search_fields = ('name', 'year',)
    list_filter = ('category',)
    filter_horizontal = ('genre',)

    @admin.display(description='Жанры')
    def genre_list(self, obj):
        return ', '.join([genre.name for genre in obj.genre.all()])


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
admin.site.unregister(Group)
