from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters,status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Genre, Review, Title

from .mixins import CategoryGenreViewsetMixin
from .permissions import (AuthorModeratorAdminOrReadOnly, IsAdminOrOwner,
                          IsAdminSuperUserOrReadOnly,
                          IsAuthenticatedOrReadOnly, IsMethodPutAllowed)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer, SignUpSerializer,
                          TitleSerializer, TokenSerializer, UserSerializer)
import api.permissions as p
from .utils import (check_fields_availability, check_user_objects,
                    send_confirmation_code)

User = get_user_model()


class SignupView(APIView):
    """
    Регистрирует пользователя в БД.
    Отправляет код подтверждения на почту.
    """
    permission_classes = [p.AllowAny]

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            username = serializer.validated_data['username']
            confirmation_code = get_random_string(length=40)

            (both_exists, username_exists, email_exists
             ) = check_user_objects(User, email, username)

            response, fields_occupied = check_fields_availability(
                both_exists, username_exists, email_exists,
                email, username
            )
            if fields_occupied:
                return response

            user, created = User.objects.update_or_create(
                    email=email, username=username,
                    defaults={'confirmation_code': confirmation_code},
            )
            send_confirmation_code(user, confirmation_code, email, username)
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenView(APIView):
    """
    Сверяет код подтверждения пользователя.
    Выдает/обновляет токен для пользователя.
    """
    permission_classes = [p.AllowAny]

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            user = User.objects.get(username=username)

            user.is_active = True
            user.save()

            refresh = RefreshToken.for_user(user)
            token = str(refresh.access_token)
            return Response({'token': token}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsersViewSet(viewsets.ModelViewSet):
    """Viewset для пользователей."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [p.IsAdmin]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username']
    pagination_class = PageNumberPagination

    def get_object(self):
        username = self.kwargs.get('pk')
        user = get_object_or_404(
            User,
            username=(
                self.request.user.username
                if username == 'me'
                else username
            )
        )
        self.check_object_permissions(self.request, user)
        return user

    def get_permissions(self):
        if self.action in ('partial_update', 'retrieve'):
            if self.kwargs.get('pk') == "me":
                return [p.OwnerOrReadOnly()]
        return [p.IsAdmin()]


class GenreViewSet(CategoryGenreViewsetMixin):
    """ViewSet для жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [p.AdminOrReadOnly]

    def get_object(self):
        return get_object_or_404(Genre, slug=self.kwargs.get('pk'))


class CategoryViewSet(CategoryGenreViewsetMixin):
    """ViewSet для категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [p.AdminOrReadOnly]

    def get_object(self):
        return get_object_or_404(Category, slug=self.kwargs.get('pk'))


class TitleViewSet(viewsets.ModelViewSet):
    """Viewset для произведений."""

    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_clases = [p.AdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category__slug', 'genre__slug', 'name', 'year']
    pagination_class = PageNumberPagination


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для отзывов."""

    serializer_class = ReviewSerializer
    permission_classes = [p.OwnerOrReadOnly]

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
    permission_classes = [p.OwnerOrReadOnly]

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
