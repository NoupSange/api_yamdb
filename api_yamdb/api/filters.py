from django_filters import rest_framework as filters
from reviews.models import Category, Genre, Title


class TitleFilter(filters.FilterSet):
    genre = filters.ModelMultipleChoiceFilter(
        field_name='genre__slug',
        to_field_name='slug',
        queryset=Genre.objects.all(),
    )
    category = filters.ModelChoiceFilter(
        field_name='category',
        to_field_name='slug',
        queryset=Category.objects.all(),
    )

    class Meta:
        model = Title
        fields = ['genre', 'category', 'name', 'year']
