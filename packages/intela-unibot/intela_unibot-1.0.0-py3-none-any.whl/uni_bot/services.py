"""
Defines models use cases.
"""
from django.contrib.auth import get_user_model
from django.db.models import OuterRef, QuerySet, Subquery
from django.db.models.functions import Coalesce

# pylint: disable=import-error
from common.djangoapps.student.models import CourseAccessRole
from openedx.core.djangoapps.django_comment_common.models import Role


User = get_user_model()


class UserService:
    """
    Perform user-related queries.
    """

    @staticmethod
    def get_course_enrollers(course_id: str) -> QuerySet[User]:
        """
        Provide users that are enrolled on the course.
        """
        return User.objects.filter(courseenrollment__course__id=course_id).distinct()

    def get_active_course_enrollers(self, course_id: str) -> QuerySet[User]:
        """
        Provide active users that are enrolled on the course.
        """
        return self.get_course_enrollers(course_id).filter(courseenrollment__is_active=True).distinct()

    def get_active_course_enrollers_with_roles(self, course_id: str) -> QuerySet[User]:
        """
        Provide active users that are enrolled on the course with role name.
        """
        return (
            self.get_active_course_enrollers(course_id)
            .annotate(
                course_role=Coalesce(
                    Subquery(
                        CourseAccessRole.objects.filter(
                            course_id=course_id,
                            user__id=OuterRef('pk'),
                        )
                        .values('role')
                        [:1]
                    ),
                    Subquery(
                        Role.objects.filter(
                            course_id=course_id,
                            users__id=OuterRef('pk'),
                        )
                        .values('name')
                        [:1]
                    )
                )
            )
        )
