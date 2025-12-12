from django.contrib.contenttypes.models import ContentType

from .models import UserActivity
from .utils import get_client_ip


def log_activity(user, action, instance=None, changes=None, request=None):
    """Helper function to manually log activity"""
    UserActivity.objects.create(
        actor=user,
        action=action,
        content_type=ContentType.objects.get_for_model(instance) if instance else None,
        object_id=str(instance.pk) if instance else None,
        object_repr=str(instance)[:255] if instance else "",
        changes=changes,
        ip_address=get_client_ip(request) if request else None,
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:500] if request else "",
    )


def log_login(user, request=None):
    """Helper to log login activity"""
    log_activity(user=user, action=UserActivity.ActionChoices.LOGIN, request=request)


def log_logout(user, request=None):
    """Helper to log logout activity"""
    log_activity(user=user, action=UserActivity.ActionChoices.LOGOUT, request=request)
