from django.shortcuts import render

from main.models import Experience


def show_main(request):
    context = {
        "name": "Naila",
        "npm": "2506620444",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "Whew"
        ),
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "name": "Naila Husna",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)