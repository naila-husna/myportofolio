from django.shortcuts import render
from main.models import Experience, Education


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
    title_query = request.GET.get("title", "").strip()
    
    experiences = Experience.objects.all()
    
    if title_query:
        experiences = experiences.filter(
            title__icontains=title_query
        )
    
    context = {
        "name": "Naila Husna",
        "experience_list": experiences,
        "name": "Naila Husna",
    }
    return render(request, "experience.html", context)

def show_education(request):
    context = {
        "name": "Naila Husna",
        "education_list": Education.objects.all(),
    }
    return render(request, "education.html", context)