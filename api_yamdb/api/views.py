from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.constants import OWNER_USERNAME_URL
from reviews.models import Category, Genre, Review, Title

from .filters import TitleFilter
from .mixins import CategoryGenreViewsetMixin
from .permissions import (
    AuthorModeratorAdminOrReadOnly,
    IsAdmin,
    IsAdminOrReadOnly,
    IsMethodPutAllowed,
)
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleCreateSerializer,
    TitleListSerializer,
    SignUpSerializer,
    TokenSerializer,
    UserSerializer,
)
from .utils import (
    check_fields_availability, check_user_objects, send_confirmation_code
)

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

            (
                both_exists, username_exists, email_exists
            ) = check_user_objects(User, email, username)

            response, fields_occupied = check_fields_availability(
                both_exists,
                username_exists,
                email_exists,
                email,
                username,
            )
            if fields_occupied:
                return Response(response[0], response[1])

            user, created = User.objects.update_or_create(
                email=email,
                username=username,
                defaults={'confirmation_code': confirmation_code},
            )
            send_confirmation_code(user, confirmation_code, email, username)
            return Response(response[0], response[1])
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
    permission_classes = [IsAdmin]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username']
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'delete', 'patch']
    lookup_field = 'username'

    @action(
        detail=False,
        methods=['get', 'patch'],
        url_path=OWNER_USERNAME_URL,
        permission_classes=[IsAuthenticated]
    )
    def personal_info(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)

        if request.method == 'PATCH':
            data = request.data.copy()
            if 'role' in data:
                del data['role']
            serializer = self.get_serializer(
                request.user, data=data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )


class GenreViewSet(CategoryGenreViewsetMixin):
    """ViewSet для жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(CategoryGenreViewsetMixin):
    """ViewSet для категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TitleViewSet(viewsets.ModelViewSet):
    """Viewset для произведений."""

    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).order_by('id')
    permission_classes = [IsAdminOrReadOnly, IsMethodPutAllowed]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleListSerializer
        return TitleCreateSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для отзывов."""

    serializer_class = ReviewSerializer
    permission_classes = [AuthorModeratorAdminOrReadOnly, IsMethodPutAllowed]

    def get_title(self):
        """Получение произведения по ID."""
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для комментариев."""

    serializer_class = CommentSerializer
    permission_classes = [AuthorModeratorAdminOrReadOnly, IsMethodPutAllowed]

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.all().order_by('-pub_date')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
