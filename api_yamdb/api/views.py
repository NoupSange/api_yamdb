from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from reviews.models import Review, Title
from .serializers import ReviewSerializer, CommentSerializer
from .permissions import (
    AuthorModeratorAdminOrReadOnly,
    IsAuthenticatedOrReadOnly
)


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
        review = get_object_or_404(Review, id=self.kwargs.get("review_id"))
        serializer.save(author=self.request.user, review=review)
