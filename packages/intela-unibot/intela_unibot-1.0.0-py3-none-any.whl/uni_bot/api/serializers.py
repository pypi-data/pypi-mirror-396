"""
Unibot API endpoints data serializers.
"""
from django.contrib.auth import get_user_model
from django_countries.serializer_fields import CountryField
from rest_framework import serializers

from common.djangoapps.student.models import UserProfile  # pylint: disable=import-error


User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serialize a user profile.
    """

    country = CountryField()

    class Meta:  # pylint: disable=missing-class-docstring, too-few-public-methods
        model = UserProfile
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    """
    Serialize a user.
    """

    profile = UserProfileSerializer()
    course_role = serializers.CharField()

    class Meta:  # pylint: disable=missing-class-docstring, too-few-public-methods
        model = User
        exclude = ('password',)
