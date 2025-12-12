from rest_framework import serializers

from .models import UserActivity


class UserActivitySerializer(serializers.ModelSerializer):
    actor_email = serializers.CharField(source="actor.email", read_only=True)
    actor_name = serializers.CharField(source="actor.full_name", read_only=True)
    action_display = serializers.CharField(source="get_action_display", read_only=True)
    content_type_display = serializers.SerializerMethodField()

    class Meta:
        model = UserActivity
        fields = [
            "id",
            "actor",
            "actor_email",
            "actor_name",
            "action",
            "action_display",
            "content_type",
            "content_type_display",
            "object_id",
            "object_repr",
            "changes",
            "ip_address",
            "user_agent",
            "created_at",
        ]

    def get_content_type_display(self, obj):
        if obj.content_type:
            return f"{obj.content_type.app_label}.{obj.content_type.model}"
        return None
