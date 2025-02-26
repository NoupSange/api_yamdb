from django.urls import include, path
from rest_framework import routers

from .views import (
    AuthViewSet,
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    TitleViewSet,
    UsersViewSet,
)


router_v1 = routers.DefaultRouter()

router_v1.register('auth', AuthViewSet, basename='auth')
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register('users', UsersViewSet, basename='users')
router_v1.register(
    r'^titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='reviews'
)
router_v1.register(
    r'^titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)


urlpatterns = [
    path('v1/', include(router_v1.urls)),
]
