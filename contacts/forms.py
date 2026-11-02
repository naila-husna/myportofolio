from django import forms

from .models import Contact


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ["name", "email", "phone"]
        labels = {"name": "Nama", "email": "Email", "phone": "Nomor telepon"}
        widgets = {"phone": forms.TextInput(attrs={"type": "tel"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["placeholder"] = field.label
