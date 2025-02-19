from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from reviews.models import Category, Genre, Title

from .mixins import CategoryGenreViewsetMixin
from .permissions import IsAdminSuperUserOrReadOnly, IsMethodPutAllowed
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
)


class GenreViewSet(CategoryGenreViewsetMixin):
    """ViewSet для жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer

    def get_object(self):
        return get_object_or_404(Genre, slug=self.kwargs.get('pk'))


class CategoryViewSet(CategoryGenreViewsetMixin):
    """ViewSet для категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_object(self):
        return get_object_or_404(Category, slug=self.kwargs.get('pk'))


class TitleViewSet(viewsets.ModelViewSet):
    """Viewset для произведений."""

    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = [IsAdminSuperUserOrReadOnly, IsMethodPutAllowed]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category__slug', 'genre__slug', 'name', 'year']
    pagination_class = PageNumberPagination
