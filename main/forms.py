from django.forms import (ModelForm, TextInput, Textarea, URLInput, DateInput)

from main.models import Experience, Message


class MessageForm(ModelForm):
    class Meta:
        model = Message

        fields = [
            "name",
            "relationship",
            "message",
            "is_anonymous",
        ]

        labels = {
            "name": "Nama",
            "relationship": "Relationship",
            "message": "Pesan",
            "is_anonymous": "Tampilkan sebagai anonim",
        }

        widgets = {
            "name": TextInput(
                attrs={
                    "placeholder": "Nama kamu",
                    "maxlength": 100,
                }
            ),
            "relationship": TextInput(
                attrs={
                    "placeholder": "Friend, teammate, classmate, etc.",
                    "maxlength": 100,
                }
            ),
            "message": Textarea(
                attrs={
                    "placeholder": "Tulis pesan atau kata-kata untuk Naila...",
                    "rows": 4,
                }
            ),
        }