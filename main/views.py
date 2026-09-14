from django.shortcuts import render

from main.models import Experience
from main.models import Education


def show_main(request):
    context = {
        "name": "Naila",
        "npm": "2506620444",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "I’m a first-year Information Systems student at Universitas Indonesia with an interest in technology, data, and consulting. I enjoy solving problems, learning new skills, and working collaboratively on meaningful projects."
        ),
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "name": "Naila Husna",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)

def show_education(request):
    context = {
        "name": "Naila Husna",
        "education_list": Education.objects.all(),
    }
    return render(request, "education.html", context)