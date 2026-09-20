from django.forms import (ModelForm, TextInput, Textarea, URLInput, DateInput)

from main.models import Experience, Message


class ExperienceForm(ModelForm):
    class Meta:
        model = Experience

        fields = [
            "title",
            "role",
            "description",
            "category",
            "thumbnail",
            "ended_at",
        ]

        labels = {
            "title": "Title",
            "role": "Role",
            "description": "Description",
            "category": "Category",
            "thumbnail": "Thumbnail URL",
            "ended_at": "End Date",
        }

        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Nama pengalaman",
                    "maxlength": 255,
                }
            ),
            "role": TextInput(
                attrs={
                    "placeholder": "Role atau posisi",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Ceritakan pengalamanmu",
                    "rows": 3,
                }
            ),
            "thumbnail": URLInput(
                attrs={
                    "placeholder": "https://...",
                }
            ),
            "ended_at": DateInput(
                attrs={
                    "type": "date",
                }
            ),
        }
        
class MessageForm(ModelForm):
    class Meta:
        model = Message

        fields = [
            "name",
            "message",
        ]

        labels = {
            "name": "Nama",
            "message": "Pesan",
        }

        widgets = {
            "name": TextInput(
                attrs={
                    "placeholder": "Nama kamu",
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