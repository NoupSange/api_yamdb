from rest_framework import serializers
from django.core.exceptions import ValidationError
from reviews.models import Category, Comment, Genre, Review, Title, User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователей с ролями."""

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role')


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
    rating = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'category',
                  'genre', 'category_detail', 'genre_detail', 'rating')

    def get_rating(self, obj):
        reviews = obj.reviews.all()

        count = len(reviews)
        if count == 0:
            return None

        total_score = 0
        for review in reviews:
            total_score += review.score
        return total_score / count

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['category'] = representation.pop(
            'category_detail', None
        )
        representation['genre'] = representation.pop('genre_detail', None)
        return representation


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )
    score = serializers.IntegerField(
        min_value=1, max_value=10,
        error_messages={
            "min_value": "Оценка не может быть ниже 1.",
            "max_value": "Оценка не может быть выше 10."
        }
    )

    def validate(self, data):
        """
        Проверяет, что пользователь оставляет
        только один отзыв на произведение.
        """
        request = self.context.get('request')
        if request and request.method == 'POST':
            user = request.user
            title_id = self.context['view'].kwargs.get('title_id')
            if Review.objects.filter(author=user, title_id=title_id).exists():
                raise ValidationError(
                    "Вы уже оставляли отзыв на это произведение."
                )
        return data

    class Meta:
        model = Review
        fields = ('id', 'author', 'title', 'text', 'score', 'pub_date')


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'author', 'review', 'text', 'pub_date')
