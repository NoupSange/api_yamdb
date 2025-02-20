from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination

from reviews.models import Category, Genre, Review, Title

from .mixins import CategoryGenreViewsetMixin
from .permissions import (
    AuthorModeratorAdminOrReadOnly,
    IsAdminSuperUserOrReadOnly,
    IsAuthenticatedOrReadOnly,
    IsMethodPutAllowed,
)
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
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


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для отзывов."""

    serializer_class = ReviewSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        AuthorModeratorAdminOrReadOnly
    ]

    def get_queryset(self):
        """Возвращает список отзывов для конкретного произведения."""
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews

    def perform_create(self, serializer):
        """
        Создаёт отзыв, привязывая его к текущему
        пользователю и произведению.
        """
        title = get_object_or_404(Title, id=self.kwargs.get("title_id"))
        if Review.objects.filter(
                author=self.request.user, title=title
        ).exists():
            raise PermissionDenied(
                "Вы уже оставляли отзыв на это произведение."
            )
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для комментариев."""

    serializer_class = CommentSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        AuthorModeratorAdminOrReadOnly
    ]

    def get_queryset(self):
        """Возвращает список комментариев для конкретного отзыва."""
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review.comments

    def perform_create(self, serializer):
        """
        Создаёт комментарий, привязывая его
        к текущему пользователю и отзыву.
        """
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)
