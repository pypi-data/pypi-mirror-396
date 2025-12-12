from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .models import UserActivity
from .registry import registry
from .utils import get_client_ip, get_current_request, get_model_changes


@receiver(pre_save)
def capture_pre_save_state(sender, instance, **kwargs):
    if not registry.is_registered(sender) or sender == UserActivity:
        return
    if instance.pk:
        try:
            instance._pre_save_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            instance._pre_save_instance = None


@receiver(post_save)
def log_create_update(sender, instance, created, **kwargs):
    if not registry.is_registered(sender) or sender == UserActivity:
        return

    request = get_current_request()
    if not request or not hasattr(request, "user") or not request.user.is_authenticated:
        return

    action = (
        UserActivity.ActionChoices.CREATE
        if created
        else UserActivity.ActionChoices.UPDATE
    )
    changes = None

    if not created and hasattr(instance, "_pre_save_instance"):
        changes = get_model_changes(
            instance._pre_save_instance, instance, registry.get_sensitive_fields()
        )
        if not changes:
            return

    UserActivity.objects.create(
        actor=request.user,
        action=action,
        content_type=ContentType.objects.get_for_model(sender),
        object_id=str(instance.pk),
        object_repr=str(instance)[:255],
        changes=changes,
        ip_address=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
    )


@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    if not registry.is_registered(sender) or sender == UserActivity:
        return

    request = get_current_request()
    if not request or not hasattr(request, "user") or not request.user.is_authenticated:
        return

    UserActivity.objects.create(
        actor=request.user,
        action=UserActivity.ActionChoices.DELETE,
        content_type=ContentType.objects.get_for_model(sender),
        object_id=str(instance.pk),
        object_repr=str(instance)[:255],
        ip_address=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
    )
