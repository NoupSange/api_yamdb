from django.urls import path
from .views import SignupView, TokenView, UsersList, UserDetail

urlpatterns = [
    path('auth/signup/', SignupView.as_view()),
    path('auth/token/', TokenView.as_view()),
    path('users/', UsersList.as_view()),
    path('users/<int:pk>/', UserDetail.as_view()),
]
