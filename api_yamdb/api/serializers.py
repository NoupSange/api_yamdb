from rest_framework import serializers
from reviews.models import Category, Genre, Title


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров."""

    class Meta:
        model = Genre
        fields = ('name', 'slug',)


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий."""

    class Meta:
        model = Category
        fields = ('name', 'slug',)


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для произведений."""

    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
    )
    genre_detail = GenreSerializer(source='genre', read_only=True, many=True)
    category_detail = CategorySerializer(source='category', read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'category',
                  'genre', 'category_detail', 'genre_detail')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['category'] = representation.pop(
            'category_detail', None
        )
        representation['genre'] = representation.pop('genre_detail', None)
        return representation
