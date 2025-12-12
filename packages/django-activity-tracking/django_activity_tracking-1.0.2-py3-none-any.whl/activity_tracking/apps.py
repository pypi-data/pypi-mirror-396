from django.apps import AppConfig, apps


class ActivityConfig(AppConfig):
    name = "activity_tracking"

    def ready(self):
        from .registry import registry
        from .settings import AUTO_REGISTER_MODELS, SENSITIVE_FIELDS

        # Register sensitive fields
        for field in SENSITIVE_FIELDS:
            registry.add_sensitive_field(field)

        # Auto-register models from settings
        for model_path in AUTO_REGISTER_MODELS:
            try:
                model = apps.get_model(model_path)
                registry.register(model)
            except (LookupError, ValueError):
                pass
