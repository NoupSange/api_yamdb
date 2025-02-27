from django_filters import rest_framework as filters
from reviews.models import Genre, Title


class TitleFilter(filters.FilterSet):
    genre = filters.ModelMultipleChoiceFilter(
        field_name='genre__slug',
        to_field_name='slug',
        queryset=Genre.objects.all(),
    )
    category = filters.CharFilter(
        field_name='category__slug',
    )
    name = filters.CharFilter(
        lookup_expr='icontains'
    )

    class Meta:
        model = Title
        fields = ['genre', 'category', 'name', 'year']
