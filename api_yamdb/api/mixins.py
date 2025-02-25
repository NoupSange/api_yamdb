from rest_framework import filters, mixins, serializers, viewsets
from rest_framework.pagination import PageNumberPagination

from reviews.models import Title
from .permissions import (
    IsAdminOrReadOnly,
)


class CategoryGenreViewsetMixin(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    pagination_class = PageNumberPagination


class TitleSerializerMixin(serializers.ModelSerializer):
    """Миксин сериализаторов произведения."""

    class Meta:
        model = Title
        fields = '__all__'
