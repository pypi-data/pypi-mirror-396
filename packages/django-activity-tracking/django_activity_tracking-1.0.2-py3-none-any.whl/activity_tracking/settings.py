from django.conf import settings


def get_setting(name, default=None):
    """Get activity tracking setting"""
    return getattr(settings, f"ACTIVITY_TRACKING_{name}", default)


# Default sensitive fields
DEFAULT_SENSITIVE_FIELDS = ["password", "otp", "last_login", "token", "secret"]

# Get settings
SENSITIVE_FIELDS = get_setting("SENSITIVE_FIELDS", DEFAULT_SENSITIVE_FIELDS)
TRACK_LOGIN = get_setting("TRACK_LOGIN", True)
TRACK_LOGOUT = get_setting("TRACK_LOGOUT", True)
TRACK_IP = get_setting("TRACK_IP", True)
TRACK_USER_AGENT = get_setting("TRACK_USER_AGENT", True)
AUTO_REGISTER_MODELS = get_setting("AUTO_REGISTER_MODELS", [])
