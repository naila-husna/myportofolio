from django.forms import (ModelForm, TextInput, Textarea, URLInput, DateInput)
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags

from main.models import Experience, Message


class MessageForm(ModelForm):
    def clean_name(self):
        name = strip_tags(self.cleaned_data["name"]).strip()
        if not name:
            raise ValidationError("Nama tidak boleh hanya berisi tag HTML.")
        return name

    def clean_relationship(self):
        relationship = strip_tags(self.cleaned_data["relationship"]).strip()
        if not relationship:
            raise ValidationError("Relationship tidak boleh hanya berisi tag HTML.")
        return relationship

    def clean_message(self):
        message = strip_tags(self.cleaned_data["message"]).strip()
        if not message:
            raise ValidationError("Pesan tidak boleh hanya berisi tag HTML.")
        return message

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
