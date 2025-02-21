from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from reviews.models import Comment, Review
from reviews.constants import CONFIRMATION_CODE_LENGTH, USERNAME_LENGTH
User = get_user_model()


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=USERNAME_LENGTH)

    def validate_username(self, value):
        if value == 'me':
            raise ValidationError('Username "me" is not allowed.')
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
                'confirmation_code': 'Invalid confirmation code.'})

        return data


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователей с ролями."""

    class Meta:
        model = User
        fields = (
            "id", "username", "email", "first_name", "last_name", "bio", "role"
        )


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field="username"
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
        request = self.context.get("request")
        if request and request.method == "POST":
            user = request.user
            title_id = self.context["view"].kwargs.get("title_id")
            if Review.objects.filter(author=user, title_id=title_id).exists():
                raise ValidationError(
                    "Вы уже оставляли отзыв на это произведение."
                )
        return data

    class Meta:
        model = Review
        fields = ("id", "author", "title", "text", "score", "pub_date")


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field="username"
    )

    class Meta:
        model = Comment
        fields = ("id", "author", "review", "text", "pub_date")
