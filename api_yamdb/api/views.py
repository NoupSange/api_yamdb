from django.contrib.auth import get_user_model
from django.db import models
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Comment, Category, Genre, Review, Title

from .filters import TitleFilter
from .mixins import CategoryGenreViewsetMixin
from .permissions import (
    AllowAny,
    AuthorModeratorAdminOrReadOnly,
    IsAdminOrOwner,
    IsAdminOrReadOnly,
    IsMethodPutAllowed,
)
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleSerializer,
    SignUpSerializer,
    TokenSerializer,
    UserSerializer,
)
from .utils import (check_fields_availability, check_user_objects,
                    send_confirmation_code)
User = get_user_model()


class SignupView(APIView):
    """
    Регистрирует пользователя в БД.
    Отправляет код подтверждения на почту.
    """
    permission_classes = [AllowAny]

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
    permission_classes = [AllowAny]

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
    permission_classes = [IsAdminOrOwner, IsMethodPutAllowed]
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

    def perform_update(self, serializer):
        is_me = self.kwargs.get('pk') == 'me'
        is_admin = self.request.user.is_authenticated and (
            self.request.user.role == 'admin' or self.request.user.is_superuser
        )

        if is_me and not is_admin and 'role' in serializer.validated_data:
            del serializer.validated_data['role']
        serializer.save()


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
    permission_classes = [IsAdminOrReadOnly, IsMethodPutAllowed]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter
    pagination_class = PageNumberPagination


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для отзывов."""

    serializer_class = ReviewSerializer
    permission_classes = [AuthorModeratorAdminOrReadOnly, IsMethodPutAllowed]

    def get_title(self) -> Title:
        """Получение произведения по ID."""
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self) -> models.QuerySet[Review]:
        """Возвращает все отзывы произведения."""
        return self.get_title().reviews.all()

    def perform_create(self, serializer) -> None:
        """Переопределение метода добавления отзыва."""
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для комментариев."""

    serializer_class = CommentSerializer
    permission_classes = [AuthorModeratorAdminOrReadOnly, IsMethodPutAllowed]

    def get_review(self) -> Review:
        """Получение отзыва по ID."""
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def get_queryset(self) -> models.QuerySet[Comment]:
        """Возвращает все комментарии для отзыва."""
        return self.get_review().comments.all().order_by('-pub_date')

    def perform_create(self, serializer) -> None:
        """Переопределение метода добавления комментария."""
        serializer.save(author=self.request.user, review=self.get_review())
