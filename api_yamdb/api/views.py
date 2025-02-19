from rest_framework import filters, mixins, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination

from django.shortcuts import get_object_or_404
from reviews.models import Category
from .serializers import (
    CategorySerializer,
)
from .permissions import (
    IsAdminOrReadOnly,
)


class CategoryViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """ViewSet для категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    pagination_class = PageNumberPagination

    def get_object(self):
        return get_object_or_404(Category, slug=self.kwargs.get('pk'))
