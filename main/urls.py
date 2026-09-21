from django.urls import path

from main.views import show_main, show_experience, show_education, get_messages_json, update_message, delete_message

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("education/", show_education, name="show_education"),
    path("api/messages/", get_messages_json, name="get_messages_json"),
    path("messages/<int:message_id>/edit/", update_message, name="update_message"),
    path("messages/<int:message_id>/delete/", delete_message, name="delete_message"),
]