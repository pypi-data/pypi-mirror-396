from django.contrib import admin

from .models import UserActivity


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ["actor", "action", "object_repr", "created_at", "ip_address"]
    list_filter = ["action", "created_at", "content_type"]
    search_fields = ["actor__email", "object_repr", "ip_address"]
    readonly_fields = [
        "actor",
        "action",
        "content_type",
        "object_id",
        "object_repr",
        "changes",
        "ip_address",
        "user_agent",
        "created_at",
    ]
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
