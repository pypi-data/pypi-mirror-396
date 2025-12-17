"""uni_bot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.urls import include, path, re_path

from lms.urls import urlpatterns as lms_patterns  # pylint: disable=import-error
from openedx.core.constants import COURSE_ID_PATTERN  # pylint: disable=import-error

from uni_bot.views.course_about import course_about
from uni_bot.views.tab_view import UniBotTabView

overridden_patterns = (
    re_path(fr'^courses/{settings.COURSE_ID_PATTERN}/$', course_about, name='course_root'),
    re_path(fr'^courses/{settings.COURSE_ID_PATTERN}/about$', course_about, name='about_course'),
)

for overridden_pattern in overridden_patterns:
    lms_patterns.insert(0, overridden_pattern)


urlpatterns = [
    re_path(fr'courses/{COURSE_ID_PATTERN}/unibot', UniBotTabView.as_view(), name='unibot_tab'),
    path('uni_bot/api/', include('uni_bot.api.urls')),
]
