from django.urls import path

from . import views

app_name = "game"

urlpatterns = [
    path("", views.index, name="index"),
    path("api/move/", views.api_move, name="api_move"),
    path("api/history/", views.api_history, name="api_history"),
    path("api/history/clear/", views.api_history_clear, name="api_history_clear"),
]
