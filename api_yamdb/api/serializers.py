from rest_framework import serializers
from django.core.exceptions import ValidationError
from reviews.models import Review, Comment, Title
from users.models import User  # Замените 'users' на имя вашего приложения


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователей с ролями."""

    class Meta:
        model = User
        fields = ("id", "username", "email", "role")


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
                raise ValidationError("Вы уже оставляли отзыв на это произведение.")
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
