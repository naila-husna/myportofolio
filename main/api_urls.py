from django.urls import path
from main import api_views

app_name = "api"

urlpatterns = [
    path("messages/", api_views.message_list, name="message-list"),
    path("messages/<int:message_id>/", api_views.message_detail, name="message-detail"),
    path("messages/<int:message_id>/star/", api_views.message_star, name="message-star"),
]
