import threading

_thread_locals = threading.local()


def get_current_request():
    return getattr(_thread_locals, "request", None)


def set_current_request(request):
    _thread_locals.request = request


def clear_current_request():
    if hasattr(_thread_locals, "request"):
        del _thread_locals.request


def get_model_changes(old_instance, new_instance, sensitive_fields):
    changes = {}
    for field in new_instance._meta.fields:
        field_name = field.name
        if field_name in sensitive_fields:
            continue
        old_value = getattr(old_instance, field_name, None)
        new_value = getattr(new_instance, field_name, None)
        if old_value != new_value:
            changes[field_name] = {"from": str(old_value), "to": str(new_value)}
    return changes if changes else None


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip
