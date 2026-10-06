from django.shortcuts import render, get_object_or_404, redirect
from pin_app.models import Pin, Like, Comment
from pin_app.forms import CommentForm
from django.contrib.auth.decorators import login_required
from pin_app.models import Follow
from django.contrib.auth.models import User


# @login_required
def home(request):
    pins = Pin.objects.all()

    return render(request, "home.html", {"pins": pins})


def pin_detail(request, pin_id):

    pin = get_object_or_404(Pin, id=pin_id)

    other_pins = Pin.objects.exclude(id=pin_id)

    user_liked = False

    if request.user.is_authenticated:
        user_liked = Like.objects.filter(user=request.user, pin=pin).exists()

    like_count = Like.objects.filter(pin=pin).count()

    comments = Comment.objects.filter(pin=pin, parent=None)

    comment_form = CommentForm()

    followed = False

    if request.user.is_authenticated:
        followed = Follow.objects.filter(
            follower=request.user, following=pin.user
        ).exists()

    return render(
        request,
        "home/pin_detail.html",
        {
            "pin": pin,
            "other_pins": other_pins,
            "user_liked": user_liked,
            "like_count": like_count,
            "comments": comments,
            "comment_form": comment_form,
            "followed": followed,
        },
    )


@login_required
def delete_pin(request, pin_id):

    pin = get_object_or_404(Pin, id=pin_id)

    print("pin to be delete", pin)

    # Find the Pin whose id is equal to pin_id. If it doesn't exist, return a 404 page using redirect internal http response.

    if request.user != pin.user:
        return redirect("pin_detail", pin_id=pin.id)

    if request.method == "POST":
        pin.delete()
        return redirect("home")

    return redirect("pin_detail", pin_id=pin.id)


@login_required
def like_pin(request, pin_id):

    pin = get_object_or_404(Pin, id=pin_id)

    if request.method == "POST":

        like, created = Like.objects.get_or_create(user=request.user, pin=pin)

        if not created:
            like.delete()

        # If new like not created means like with userid,pinid exist then delete like.

    return redirect("pin_detail", pin_id=pin.id)


@login_required
def add_comment(request, pin_id):

    pin = get_object_or_404(Pin, id=pin_id)

    if request.method == "POST":

        form = CommentForm(request.POST)

        if form.is_valid():

            comment = form.save(commit=False)

            comment.user = request.user
            comment.pin = pin
            comment.save()

    return redirect("pin_detail", pin_id=pin.id)


@login_required
def add_reply(request, pin_id, comment_id):

    pin = get_object_or_404(Pin, id=pin_id)

    parent_comment = get_object_or_404(Comment, id=comment_id, pin=pin)

    if request.method == "POST":

        form = CommentForm(request.POST)

        if form.is_valid():

            reply = form.save(commit=False)

            reply.user = request.user
            reply.pin = pin
            reply.parent = parent_comment

            reply.save()

    return redirect("pin_detail", pin_id=pin.id)


@login_required
def delete_comment(request, comment_id):

    comment = get_object_or_404(Comment, id=comment_id)

    if request.user != comment.user:
        return redirect("pin_detail", pin_id=comment.pin.id)

    if request.method == "POST":
        comment.delete()

    return redirect("pin_detail", pin_id=comment.pin.id)


@login_required
def follow_user(request, user_id):

    user_to_follow = get_object_or_404(User, id=user_id)

    pin_id = request.POST.get("pin_id")

    if request.user == user_to_follow:
        return redirect("pin_detail", pin_id=pin_id)

    if request.method == "POST":

        follow, created = Follow.objects.get_or_create(
            follower=request.user, following=user_to_follow
        )

        if not created:
            follow.delete()

    return redirect("pin_detail", pin_id=pin_id)
