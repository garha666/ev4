from django.urls import path
from .views import MeView, SessionTokenView, UserCreateView

urlpatterns = [
    path('users/', UserCreateView.as_view(), name='user-create'),
    path('users/me/', MeView.as_view(), name='user-me'),
    path('token/session/', SessionTokenView.as_view(), name='token-session'),
]
