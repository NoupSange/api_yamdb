from rest_framework import serializers
from django.core.exceptions import ValidationError
from reviews.models import Category


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий."""

    class Meta:
        model = Category
        fields = '__all__'
