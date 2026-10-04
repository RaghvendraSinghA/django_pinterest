from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from .forms import SignupForm, LoginForm


def signup_view(request):

    if request.method == "POST":

        form = SignupForm(request.POST)

        if form.is_valid():

            user = form.save()

            login(request, user)

            return redirect("home")

    else:

        form = SignupForm()
        # create and return an empty form.

    return render(
        request,
        "account/signup.html",
        {
            "form": form
        }
    )


def login_view(request):

    if request.method == "POST":

        form = LoginForm(
            request,
            data=request.POST
        )

        # request is passed because, AuthenticationForm uses the request during authentication.

        if form.is_valid():

            user = form.get_user()

            login(request, user)

            return redirect("home")

    else:

        form = LoginForm()

    return render(
        request,
        "account/login.html",
        {
            "form": form
        }
    )


def logout_view(request):

    logout(request)

    return redirect("home")