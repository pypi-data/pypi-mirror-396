"""
Unibot Auth API URL Configurations.
"""
from django.urls import path

from uni_bot_auth.api import views

urlpatterns = [
    path('jwt/generate/', views.GenerateJwtView.as_view(), name='generate-jwt'),
]
