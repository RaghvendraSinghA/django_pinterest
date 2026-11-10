from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from .forms import SignupForm, LoginForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .forms import UserUpdateForm, ProfileUpdateForm
from .models import Profile
from .tasks import upload_profile_pic
import time


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





def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)

    profile, _ = Profile.objects.get_or_create(
        user=profile_user
    )

    pins = profile_user.pins.all()

    boards = profile_user.boards.all()

    # The _ is a normal Python variable name that programmers conventionally use when they don't need a returned value.
    # profile, created = Profile.objects.get_or_create(user=request.user). We ignored created .
    return render(
        request,
        "account/profile.html",
        {
            "profile_user": profile_user,
            "profile": profile,
            "boards": boards,
            "pins" : pins,
        },
    )



@login_required
def edit_profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if user_form.is_valid() and profile_form.is_valid():

            start = time.perf_counter()

            user_form.save()
            updated_profile = profile_form.save(commit=False)

            uploaded_image = request.FILES.get("profile_pic")

            if uploaded_image:
                updated_profile.temp_profile_pic = uploaded_image
                updated_profile.upload_status = "pending"

            updated_profile.save()

            print(
                "Django save time:",
                round(time.perf_counter() - start, 4),
                "seconds"
            )

            if uploaded_image:
                task_start = time.perf_counter()

                upload_profile_pic.delay(updated_profile.id)

                print(
                    "Celery queue time:",
                    round(time.perf_counter() - task_start, 4),
                    "seconds"
                )

            return redirect(
                "profile",
                username=request.user.username
            )

    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)

    return render(
        request,
        "account/edit_profile.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
        },
    )