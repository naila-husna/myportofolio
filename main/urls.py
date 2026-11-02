from django.urls import path
from main.views import (
    create_message_ajax,
    show_main,
    show_experience,
    show_education,
    get_messages_json,
    update_message,
    delete_message,
    register,
    login_user,
    logout_user,
    toggle_star,
)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("education/", show_education, name="show_education"),
    path("api/messages/", get_messages_json, name="get_messages_json"),
    path("messages/add-ajax/", create_message_ajax, name="create_message_ajax"),
    path("messages/<int:message_id>/edit/", update_message, name="update_message"),
    path("messages/<int:message_id>/delete/", delete_message, name="delete_message"),
    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
    path("messages/<int:message_id>/star/", toggle_star, name="toggle_star",),
]
