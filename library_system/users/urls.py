from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    path('register/', views.RegisterAPIView.as_view(), name='register'),
    path('login/', views.LoginAPIView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.LogoutAPIView.as_view(), name='logout'),
    path('password/rest/', views.PasswordRestAPIView.as_view(), name='password-rest'),
    path('password/confirm/', views.PasswordRestConfirmAPIView.as_view(), name='password-rest-confirm'),
]
