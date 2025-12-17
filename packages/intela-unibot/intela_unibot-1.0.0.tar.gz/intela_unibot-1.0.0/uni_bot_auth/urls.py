"""
uni_bot_auth URL Configurations.
"""
from django.urls import include, path


urlpatterns = [
    path('uni_bot_auth/api/', include('uni_bot_auth.api.urls')),
]
