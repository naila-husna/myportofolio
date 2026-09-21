from django.shortcuts import render, redirect, get_object_or_404
from django.core import serializers
from django.http import HttpResponse

from main.models import Experience, Education, Message
from main.forms import MessageForm

def get_messages_json(request):
    messages = Message.objects.all().order_by("-created_at")

    for message in messages:
        if message.is_anonymous:
            message.name = "Anonymous"

    messages_json = serializers.serialize("json", messages)

    return HttpResponse(
        messages_json,
        content_type="application/json"
    )
    
def show_main(request):
    if request.method == "POST":
        form = MessageForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("main:show_main")
    else:
        form = MessageForm()
    
    json_response = get_messages_json(request)

    messages = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8")
    )

    messages = [message.object for message in messages]
        
    context = {
        "name": "Naila Husna",
        "npm": "2506620444",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "I’m a first-year Information Systems student at Universitas Indonesia with an interest in technology, data, and consulting. I enjoy solving problems, learning new skills, and working collaboratively on meaningful projects."
        ),
        "form": form,
        "message_list": messages,
    }
    return render(request, "index.html", context)

def update_message(request, message_id):
    message = get_object_or_404(Message, pk=message_id)

    form = MessageForm(
        request.POST or None,
        instance=message
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("main:show_main")

    context = {
        "name": "Naila Husna",
        "form": form,
        "message": message,
    }

    return render(request, "message_form.html", context)

def delete_message(request, message_id):
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