from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.constants import (
    CONFIRMATION_CODE_LENGTH, EMAIL_LENGTH, OWNER_USERNAME_URL, USERNAME_LENGTH
)
from reviews.models import Category, Comment, Genre, Review
from .mixins import TitleSerializerMixin

User = get_user_model()


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=EMAIL_LENGTH)
    username = serializers.RegexField(
        r'^[\w.@+-]+\Z', max_length=USERNAME_LENGTH
    )

    def validate_username(self, value):
        if value == OWNER_USERNAME_URL:
            raise ValidationError(
                f'Username "{OWNER_USERNAME_URL}" is not allowed.'
            )
        return value


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=USERNAME_LENGTH)
    confirmation_code = serializers.CharField(
        max_length=CONFIRMATION_CODE_LENGTH
    )

    def validate(self, data):
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')

        user = get_object_or_404(User, username=username)

        if user.confirmation_code != confirmation_code:
            raise ValidationError({
                'confirmation_code': 'Invalid confirmation code.'
            })

        return data


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователей с ролями."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров."""

    class Meta:
        model = Genre
        exclude = ('id',)


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий."""

    class Meta:
        model = Category
        exclude = ('id',)


class TitleListSerializer(TitleSerializerMixin):
    """Сериализатор для получения списка/одного произведения."""

    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.IntegerField()


class TitleCreateSerializer(TitleSerializerMixin):
    """Сериализатор для создания/изменения/удаления произведения."""

    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
        allow_empty=False,
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
        allow_null=False,
    )


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
        fields = ('id', 'author', 'text', 'score', 'pub_date')


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'author', 'text', 'pub_date')
