import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.core import serializers
from django.http import HttpResponse

from main.models import Experience, Education, Message
from main.forms import MessageForm
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

def get_messages_json(request):
    messages = Message.objects.all().order_by("-created_at")

    for message in messages:
        if message.is_anonymous:
            message.name = "Anonymous"

    messages_json = serializers.serialize("json", messages, use_natural_foreign_keys=True)

    return HttpResponse(
        messages_json,
        content_type="application/json"
    )
    
def show_main(request):
    last_login = request.COOKIES.get('last_login', 'Belum ada sesi login / Cookie tidak ditemukan')
    
    form = MessageForm(request.POST or None)
    
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("main:show_main")
    
    messages_list = Message.objects.all().order_by("-created_at")
    
    context = {
        "name": "Naila Husna",
        "npm": "2506620444",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "Mahasiswa Sistem Informasi Universitas Indonesia yang tertarik "
            "pada pengolahan data."
        ),
        "last_login": last_login,
        "form": form,
        "message_list": messages_list,
    }
    return render(request, "index.html", context)

@login_required(login_url="/login/")
def update_message(request, message_id):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    message = get_object_or_404(Message, pk=message_id)

    form = MessageForm(request.POST or None, instance=message)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("main:show_main")

    context = {
        "name": "Naila Husna",
        "form": form,
        "message": message,
    }

    return render(request, "message_form.html", context)

@login_required(login_url="/login/")
def delete_message(request, message_id):
    if not request.user.is_superuser:
            raise PermissionDenied
    
    message = get_object_or_404(Message, pk=message_id)

    if request.method == "POST":
        message.delete()

    return redirect("main:show_main")

def show_experience(request):
    title_query = request.GET.get("title", "").strip()
    experiences = Experience.objects.all()
    
    if title_query:
        experiences = experiences.filter(
            title__icontains=title_query
        )
    
    context = {
        "name": "Naila Husna",
        "experience_list": experiences,
    }
    return render(request, "experience.html", context)

def show_education(request):
    context = {
        "name": "Naila Husna",
        "education_list": Education.objects.all(),
    }
    return render(request, "education.html", context)

def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat. Silakan login.")
        return redirect("main:login")

    context = {
        "name": "Naila",
        "form": form,
    }
    return render(request, "register.html", context)

def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        response = redirect("main:show_main")
        response.set_cookie('last_login', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return response

    context = {
        "name": "Naila Husna",
        "form": form,
    }
    return render(request, "login.html", context)

def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie('last_login')
    return response

@login_required(login_url="/login/")
def toggle_star(request, message_id):
    message = get_object_or_404(Message, pk=message_id)

    if request.method == "POST":
        if request.user in message.starred_by.all():
            message.starred_by.remove(request.user)
        else:
            message.starred_by.add(request.user)

    return redirect("main:show_main")