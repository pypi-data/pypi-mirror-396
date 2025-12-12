from functools import wraps

from django.contrib.contenttypes.models import ContentType

from .models import UserActivity
from .utils import get_client_ip


def track_view(content_type_str=None, get_object_id=None, get_object_repr=None):
    """
    Decorator to automatically track view actions

    Usage:
        @track_view('myapp.mymodel', lambda request, pk: pk, lambda request, pk: f'Object {pk}')
        def my_view(request, pk):
            ...
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)

            if request.user.is_authenticated and content_type_str:
                try:
                    app_label, model = content_type_str.split(".")
                    content_type = ContentType.objects.get(
                        app_label=app_label, model=model
                    )

                    object_id = (
                        get_object_id(request, *args, **kwargs)
                        if get_object_id
                        else None
                    )
                    object_repr = (
                        get_object_repr(request, *args, **kwargs)
                        if get_object_repr
                        else ""
                    )

                    UserActivity.objects.create(
                        actor=request.user,
                        action=UserActivity.ActionChoices.VIEW,
                        content_type=content_type,
                        object_id=str(object_id) if object_id else None,
                        object_repr=str(object_repr)[:255],
                        ip_address=get_client_ip(request),
                        user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
                    )
                except (ValueError, ContentType.DoesNotExist):
                    pass

            return response

        return wrapper

    return decorator
