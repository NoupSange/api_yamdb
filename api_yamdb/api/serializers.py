import secrets
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from rest_framework import serializers

from reviews.constants import (
    CONFIRMATION_CODE_LENGTH,
    EMAIL_LENGTH,
    MAX_SCORE_VALUE,
    MIN_SCORE_VALUE,
    OWNER_USERNAME_URL,
    USERNAME_LENGTH,
)
from reviews.models import Category, Comment, Genre, Review
from reviews.validators import username_validator
from .mixins import TitleSerializerMixin

User = get_user_model()


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, max_length=EMAIL_LENGTH)
    username = serializers.CharField(
        required=True,
        max_length=USERNAME_LENGTH,
        validators=[username_validator]
    )

    def validate_username(self, value):
        if value.lower() == OWNER_USERNAME_URL:
            raise ValidationError(
                f'Имя пользователя "{value}" недопустимо.'
            )
        return value

    def validate(self, data):
        email = data.get('email')
        username = data.get('username')

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            if user.username != username:
                raise serializers.ValidationError({
                    "email": "Такой email уже существует.",
                    "username": (
                        "Имя пользователя не совпадает с зарегистрированным."
                    )
                })
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            if user.email != email:
                raise serializers.ValidationError({
                    "email": "Email не совпадает с зарегистрированным.",
                    "username": "Такое имя пользователя уже существует."
                })

        return data

    def create(self, validated_data):
        email = validated_data.get('email')
        username = validated_data.get('username')
        confirmation_code = secrets.token_hex(16)

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': username,
                'confirmation_code': confirmation_code,
            }
        )
        send_mail(
            "Код подтверждения",
            f"Ваш код подтверждения: {confirmation_code}",
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        return user


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, max_length=USERNAME_LENGTH)
    confirmation_code = serializers.CharField(
        required=True, max_length=CONFIRMATION_CODE_LENGTH
    )

    def validate(self, data):
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')

        user = get_object_or_404(User, username=username)

        if user.confirmation_code != confirmation_code:
            raise serializers.ValidationError({
                "confirmation_code": "Неверный код подтверждения."
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
        min_value=MIN_SCORE_VALUE, max_value=MAX_SCORE_VALUE,
        error_messages={
            "min_value": f"Оценка не может быть ниже {MIN_SCORE_VALUE}.",
            "max_value": f"Оценка не может быть выше {MAX_SCORE_VALUE}."
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
