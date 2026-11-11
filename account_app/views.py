from django.contrib.auth import login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import SignupForm, LoginForm, UserUpdateForm, ProfileUpdateForm

from .models import Profile
from .tasks import upload_profile_pic
import logging


logger = logging.getLogger(__name__)


def signup_view(request):

    if request.method == "POST":

        form = SignupForm(request.POST)

        if form.is_valid():

            try:
                user = form.save()
            except Exception:
                logger.exception("Failed to create a new user account")
                raise

            login(request, user)

            return redirect("home")

    else:
        form = SignupForm()

    return render(
        request,
        "account/signup.html",
        {"form": form},
    )


def login_view(request):

    if request.method == "POST":

        form = LoginForm(request, data=request.POST)

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

    return render(
        request,
        "account/profile.html",
        {
            "profile_user": profile_user,
            "profile": profile,
            "boards": boards,
            "pins": pins,
        },
    )


@login_required
def edit_profile_view(request):

    profile, _ = Profile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":

        user_form = UserUpdateForm(
            request.POST,
            instance=request.user
        )

        profile_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if user_form.is_valid() and profile_form.is_valid():

            uploaded_image = request.FILES.get("profile_pic")

            try:
                user_form.save()

                updated_profile = profile_form.save(commit=False)

                if uploaded_image:
                    updated_profile.temp_profile_pic = uploaded_image
                    updated_profile.upload_status = "pending"

                updated_profile.save()

            except Exception:
                logger.exception(
                    "Failed to update profile for User %s",
                    request.user.id
                )
                raise

            if uploaded_image:

                try:
                    upload_profile_pic.delay(updated_profile.id)

                except Exception:
                    logger.exception(
                        "Failed to queue profile picture upload for User %s",
                        request.user.id
                    )
                    raise

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
