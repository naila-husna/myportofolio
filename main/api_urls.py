from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from main import api_views

app_name = "api"

urlpatterns = [
    path("auth/token/", obtain_auth_token, name="api_token_auth"),
    path("auth/logout/", api_views.api_logout, name="api_logout"),
    path("projects/", api_views.project_list, name="project-list"),
    path("messages/", api_views.message_list, name="message-list"),
    path("messages/<int:message_id>/", api_views.message_detail, name="message-detail"),
    path("messages/<int:message_id>/star/", api_views.message_star, name="message-star"),
]
