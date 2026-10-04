from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class SignupForm(UserCreationForm):

    email = forms.EmailField(
        required=True
    )

    class Meta:
        model = User

        fields = [
            "username",
            "email",
            "password1",
            "password2",
        ]

    # It tells the form which Django model and which fields it should work with.
    #  class Meta:    Meta is a special inner class used to provide configuration/options for the form.

    # password1 and password2 are form fields created by Django's UserCreationForm.
    # They are not two password fields in the database.
    # password1 → password entered by the user
    # password2 → same password entered again for confirmation


class LoginForm(AuthenticationForm):

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username"
            }
        )
    )

    # a widget controls how a form field is represented in HTML.

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password"
            }
        )
    )