from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class SignupForm(UserCreationForm):

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={"placeholder": "Please enter you email address"}
        ),
    )

    # adding email field to SignupForm because, UserCreationForm doesn't have.

    username = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Please enter your username"}),
    )

    class Meta:
        model = User

        # It belongs to SignupFrom and tells django, configuration setting of SignupForm class.
        # "This form is connected to the User model."
        # When the form is saved, the data is used to create/update a User object.
        # so when submitting form we do user = form.save(), so form.save() will work bcoz it comes from User model.
        # so this means, that this form will have functionality of this model also.
        # The User model itself already has a uniqueness rule for username.

        fields = [
            "username",
            "email",
            "password1",
            "password2",
        ]

    # It means: "These are the model/form fields that Django should include when constructing the form."
    # when we're using:{{ form.as_p }}

    # In Django, class Meta is a special inner class used to give extra configuration/options to another Django class.

    # password1 and password2 are form fields created by Django's UserCreationForm.
    # They are not two password fields in the database.
    # password1 → password entered by the user
    # password2 → same password entered again for confirmation


class LoginForm(AuthenticationForm):

    username = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Username"})
    )

    # This time I am overriding/customizing the existing username form field.
    # a widget controls how a form field is represented in HTML, we can even pass class inside it,
    # We can even edit them like normal html element using css like <p>{color:green;}.

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Password"})
    )
