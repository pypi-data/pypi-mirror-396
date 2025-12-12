from django.contrib.contenttypes.models import ContentType
from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .models import UserActivity
from .serializers import UserActivitySerializer
from .utils import get_client_ip


class UserActivityListView(generics.ListAPIView):
    serializer_class = UserActivitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return UserActivity.objects.none()
        queryset = UserActivity.objects.filter(actor=self.request.user).select_related(
            "actor", "content_type"
        )
        action = self.request.query_params.get("action")
        content_type = self.request.query_params.get("content_type")

        if action:
            queryset = queryset.filter(action=action.upper())
        if content_type:
            try:
                app_label, model = content_type.split(".")
                ct = ContentType.objects.get(app_label=app_label, model=model)
                queryset = queryset.filter(content_type=ct)
            except (ValueError, ContentType.DoesNotExist):
                pass

        return queryset


class AllUserActivityListView(generics.ListAPIView):
    serializer_class = UserActivitySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        queryset = UserActivity.objects.all().select_related("actor", "content_type")
        actor_id = self.request.query_params.get("actor")
        action = self.request.query_params.get("action")

        if actor_id:
            queryset = queryset.filter(actor_id=actor_id)
        if action:
            queryset = queryset.filter(action=action.upper())

        return queryset


class LogViewActionView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        content_type_str = request.data.get("content_type")
        object_id = request.data.get("object_id")
        object_repr = request.data.get("object_repr", "")

        if not content_type_str or not object_id:
            return Response(
                {"error": "content_type and object_id are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            app_label, model = content_type_str.split(".")
            content_type = ContentType.objects.get(app_label=app_label, model=model)
        except (ValueError, ContentType.DoesNotExist):
            return Response(
                {"error": "Invalid content_type"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        UserActivity.objects.create(
            actor=request.user,
            action=UserActivity.ActionChoices.VIEW,
            content_type=content_type,
            object_id=str(object_id),
            object_repr=object_repr[:255],
            ip_address=get_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
        )

        return Response(
            {"message": "View action created successfully."},
            status=status.HTTP_201_CREATED,
        )
