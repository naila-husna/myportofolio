from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from django.core import serializers
from django.http import HttpResponse
from main.models import Experience, Education
from main.forms import ExperienceForm


def show_main(request):
    context = {
        "name": "Naila Husna",
        "npm": "2506620444",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "I’m a first-year Information Systems student at Universitas Indonesia with an interest in technology, data, and consulting. I enjoy solving problems, learning new skills, and working collaboratively on meaningful projects."
        ),
    }
    return render(request, "index.html", context)


def show_experience(request):
    json_response = get_experiences_json(request)

    experiences = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8")
    )

    experiences = [
        experience.object
        for experience in experiences
    ]

    title_query = request.GET.get("title", "").strip()

    context = {
        "name": "Naila Husna",
        "experience_list": experiences,
        "title_query": title_query,
    }

    return render(request, "experience.html", context)

def show_education(request):
    context = {
        "name": "Naila Husna",
        "education_list": Education.objects.all(),
    }
    return render(request, "education.html", context)

def create_experience(request):
    form = ExperienceForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Experience berhasil ditambahkan!")
        return redirect("main:show_experience")

    context = {
        "name": "Naila Husna",
        "form": form,
    }

    return render(request, "experience_form.html", context)

def get_experiences_json(request):
    title_query = request.GET.get("title", "").strip()
    experiences = Experience.objects.all()

    if title_query:
        experiences = experiences.filter(
            title__icontains=title_query
        )

    experiences_json = serializers.serialize(
        "json",
        experiences
    )

    return HttpResponse(
        experiences_json,
        content_type="application/json"
    )

def delete_experience(request, experience_id):
    experience = get_object_or_404(
        Experience,
        pk=experience_id
    )

    if request.method == "POST":
        experience.delete()
        messages.success(
            request,
            "Experience berhasil dihapus!"
        )

    return redirect("main:show_experience")