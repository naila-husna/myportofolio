import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.core import serializers
from django.http import HttpResponse, JsonResponse

from main.models import Experience, Education, Message
from main.forms import MessageForm
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.views import redirect_to_login

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST

def get_messages_json(request):
    message_query = request.GET.get("message", "").strip()
    messages = Message.objects.prefetch_related("starred_by").order_by("-created_at")

    if message_query:
        messages = messages.filter(message__icontains=message_query)

    data = []
    for message in messages:
        starred_users = message.starred_by.all()
        is_starred = request.user in starred_users if request.user.is_authenticated else False
        starred_by_names = ", ".join([u.username for u in starred_users])

        data.append({
            "pk": str(message.id),
            "fields": {
                "name": "Anonymous" if message.is_anonymous else message.name,
                "relationship": message.relationship,
                "message": message.message,
                "is_anonymous": message.is_anonymous,
                "star_count": starred_users.count(),
                "is_starred": is_starred,
                "starred_by_names": starred_by_names,
            }
        })

    return JsonResponse(data, safe=False)
    
def show_main(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), login_url="/login/")
        if not request.user.is_superuser:
            raise PermissionDenied

    last_login = request.COOKIES.get('last_login', 'Belum ada sesi login / Cookie tidak ditemukan')
    
    form = MessageForm(request.POST or None)
    
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("main:show_main")
    
    message_query = request.GET.get("message", "").strip()
    
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
        "is_editor": request.user.groups.filter(name="Editor").exists(),
        "message_query": message_query,
    }
    return render(request, "index.html", context)

@require_POST
def create_message_ajax(request):
    if not request.user.is_superuser:
        return JsonResponse(
            {"message": "Hanya pemilik portofolio yang dapat menambahkan pesan."},
            status=403,
        )

    form = MessageForm(request.POST)
    if form.is_valid():
        message = form.save()
        return JsonResponse(
            {"message": "Pesan berhasil ditambahkan.", "pk": str(message.id)},
            status=201,
        )
    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)


@login_required(login_url="/login/")
def update_message(request, message_id):
    if not (request.user.is_superuser or request.user.groups.filter(name="Editor").exists()):
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
