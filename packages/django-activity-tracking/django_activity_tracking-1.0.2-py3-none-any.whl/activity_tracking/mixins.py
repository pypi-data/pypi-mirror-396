from django.contrib.contenttypes.models import ContentType

from .models import UserActivity
from .utils import get_client_ip


class ActivityTrackingMixin:
    """Mixin to add activity tracking to views"""

    def log_activity(self, action, instance=None, changes=None):
        if not self.request.user.is_authenticated:
            return

        UserActivity.objects.create(
            actor=self.request.user,
            action=action,
            content_type=(
                ContentType.objects.get_for_model(instance) if instance else None
            ),
            object_id=str(instance.pk) if instance else None,
            object_repr=str(instance)[:255] if instance else "",
            changes=changes,
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get("HTTP_USER_AGENT", "")[:500],
        )
