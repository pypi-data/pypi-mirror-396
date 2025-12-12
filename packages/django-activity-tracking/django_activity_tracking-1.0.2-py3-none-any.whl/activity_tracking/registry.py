from django.apps import apps


class ActivityRegistry:
    def __init__(self):
        self._registry = set()
        self._sensitive_fields = set()

    def register(self, model, sensitive_fields=None):
        """Register a model for activity tracking"""
        if isinstance(model, str):
            model = apps.get_model(model)
        self._registry.add(model)
        if sensitive_fields:
            self._sensitive_fields.update(sensitive_fields)

    def unregister(self, model):
        """Unregister a model from activity tracking"""
        if isinstance(model, str):
            model = apps.get_model(model)
        self._registry.discard(model)

    def is_registered(self, model):
        """Check if a model is registered"""
        return model in self._registry

    def get_registered_models(self):
        """Get all registered models"""
        return self._registry

    def get_sensitive_fields(self):
        """Get all sensitive fields"""
        return self._sensitive_fields

    def add_sensitive_field(self, field_name):
        """Add a sensitive field"""
        self._sensitive_fields.add(field_name)


registry = ActivityRegistry()
