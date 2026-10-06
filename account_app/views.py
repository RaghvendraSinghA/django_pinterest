from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from .forms import SignupForm, LoginForm


def signup_view(request):

    if request.method == "POST":

        form = SignupForm(request.POST)

        if form.is_valid():

            user = form.save()

            login(request, user)
            # It creates login session for user.

            return redirect("home")

        # on successful signup redirect

    else:

        form = SignupForm()
        # create an empty form and then return will execute.
        # also,  The request is POST but the form is invalid → show the form
        # again with the submitted values and validation errors using bound form technique.

    return render(
        # this will also execute when there is no post method but, it is initial get method to get form fillup page,
        # In django we even return the frontend from backend.
        request,
        "account/signup.html",
        {"form": form},
    )


def login_view(request):

    if request.method == "POST":

        form = LoginForm(request, data=request.POST)

        # request is passed because, AuthenticationForm uses the request during authentication.

        if form.is_valid():

            user = form.get_user()

            login(request, user)

            return redirect("home")

    else:

        form = LoginForm()

    return render(request, "account/login.html", {"form": form})


def logout_view(request):

    logout(request)

    return redirect("home")
