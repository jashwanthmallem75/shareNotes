from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SastraUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email or not email.endswith("@sastra.ac.in"):
            raise forms.ValidationError("Registration allowed only with @sastra.ac.in email address.")
        return email
