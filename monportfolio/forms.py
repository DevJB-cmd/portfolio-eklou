from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].max_length = 100
        self.fields["subject"].max_length = 200
        self.fields["message"].max_length = 2000

    def clean_name(self):
        name = (self.cleaned_data.get("name") or "").strip()
        if len(name) < 2:
            raise forms.ValidationError("Le nom est trop court.")
        return name

    def clean_subject(self):
        subject = (self.cleaned_data.get("subject") or "").strip()
        if len(subject) < 3:
            raise forms.ValidationError("Le sujet est trop court.")
        return subject

    def clean_message(self):
        message = (self.cleaned_data.get("message") or "").strip()
        if len(message) < 10:
            raise forms.ValidationError("Le message est trop court.")
        return message
