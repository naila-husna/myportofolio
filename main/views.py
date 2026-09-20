from django.shortcuts import render, redirect
from main.models import Experience, Education, Message
from main.forms import MessageForm


def show_main(request):
    if request.method == "POST":
        form = MessageForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("main:show_main")
    else:
        form = MessageForm()
        
    context = {
        "name": "Naila Husna",
        "npm": "2506620444",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "I’m a first-year Information Systems student at Universitas Indonesia with an interest in technology, data, and consulting. I enjoy solving problems, learning new skills, and working collaboratively on meaningful projects."
        ),
        "form": form,
        "message_list": Message.objects.all().order_by("-created_at"),
    }
    return render(request, "index.html", context)


def show_experience(request):
    title_query = request.GET.get("title", "").strip()
    Ex
    experiences = perience.objects.all()
    
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