from django.urls import include, path
from rest_framework import routers

from .views import (
    CategoryViewSet,
    GenreViewSet,
    SignupView,
    TitleViewSet,
    TokenView,
    UserDetail,
    UsersList
)


router_v1 = routers.DefaultRouter()

router_v1.register('categories', CategoryViewSet)
router_v1.register('genres', GenreViewSet)
router_v1.register('titles', TitleViewSet)


urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('auth/signup/', SignupView.as_view()),
    path('auth/token/', TokenView.as_view()),
    path('users/', UsersList.as_view()),
    path('users/<int:pk>/', UserDetail.as_view()),
]
