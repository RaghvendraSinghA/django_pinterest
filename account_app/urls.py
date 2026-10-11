from django.urls import path
from . import views


urlpatterns = [
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),


    path("profile/edit/", views.edit_profile_view, name="edit_profile"),

    path(
        "profile/<str:username>/",
        views.profile_view,
        name="profile",
    ),

    # path(
    #     "profile/edit/",
    #     views.edit_profile_view,
    #     name="edit_profile",
    # ),
]


# name gives a unique name to a URL pattern, so Django can refer to that URL without hardcoding the actual URL path.

# Suppose your URL changes later then still anywhere in your templates, you can use:
# <a href="{% url 'signup' %}">Sign Up</a> Django looks for:
# name="signup"
