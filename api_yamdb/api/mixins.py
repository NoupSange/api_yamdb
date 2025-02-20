from rest_framework import filters, mixins, viewsets
from rest_framework.pagination import PageNumberPagination

from .permissions import (
    IsAdminSuperUserOrReadOnly,
)


class CategoryGenreViewsetMixin(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAdminSuperUserOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    pagination_class = PageNumberPagination
