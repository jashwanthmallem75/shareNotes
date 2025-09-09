from django import forms
from .models import Note


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ["studying_year", "department", "section", "subject", "unit_number"]

