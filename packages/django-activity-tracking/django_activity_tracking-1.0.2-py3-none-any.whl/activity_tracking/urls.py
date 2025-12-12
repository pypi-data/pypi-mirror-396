from django.urls import path

from .views import AllUserActivityListView, LogViewActionView, UserActivityListView

urlpatterns = [
    path("my-activities/", UserActivityListView.as_view(), name="user-activities"),
    path("all-activities/", AllUserActivityListView.as_view(), name="all-activities"),
    path("log-view/", LogViewActionView.as_view(), name="log-view"),
]
