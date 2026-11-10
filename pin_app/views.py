from django.shortcuts import render, get_object_or_404, redirect
from .forms import PinForm, CommentForm
from django.contrib.auth.decorators import login_required
from .models import Pin, Like, Comment, Follow
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.models import User
from board_app.models import Board
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string




@login_required
def create_pin(request):

    if request.method == "POST":
        form = PinForm(request.POST, request.FILES)

        if form.is_valid():
            pin = form.save(commit=False)
            pin.user = request.user
            pin.save()

            return redirect("home")

    else:
        form = PinForm()

    return render(request, "pin/create_pin.html", {"form": form})


def pin_detail(request, pin_id):

    pin = get_object_or_404(Pin, id=pin_id)

    other_pins = Pin.objects.exclude(id=pin_id)

    user_liked = False

    if request.user.is_authenticated:
        user_liked = Like.objects.filter(user=request.user, pin=pin).exists()

    like_count = Like.objects.filter(pin=pin).count()

    comments = Comment.objects.filter(pin=pin, parent=None)

    comment_form = CommentForm()

    boards = (
        Board.objects.filter(user=request.user)
        if request.user.is_authenticated
        else Board.objects.none()
    )

    followed = False

    if request.user.is_authenticated:
        followed = Follow.objects.filter(
            follower=request.user, following=pin.user
        ).exists()

    return render(
        request,
        "pin/pin_detail.html",
        {
            "pin": pin,
            "other_pins": other_pins,
            "user_liked": user_liked,
            "like_count": like_count,
            "comments": comments,
            "comment_form": comment_form,
            "followed": followed,
            "boards":boards,
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
@require_POST
def like_pin(request, pin_id):

    pin = get_object_or_404(Pin, id=pin_id)

    like, created = Like.objects.get_or_create(
        user=request.user,
        pin=pin,
    )

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    like_count = pin.likes.count()

    return JsonResponse({
        "liked": liked,
        "like_count": like_count,
    })


# @login_required
# def add_comment(request, pin_id):

#     pin = get_object_or_404(Pin, id=pin_id)

#     if request.method == "POST":

#         form = CommentForm(request.POST)

#         if form.is_valid():

#             comment = form.save(commit=False)

#             comment.user = request.user
#             comment.pin = pin
#             comment.save()

#     return redirect("pin_detail", pin_id=pin.id)


@login_required
@require_POST
def add_comment(request, pin_id):

    pin = get_object_or_404(Pin, id=pin_id)
    form = CommentForm(request.POST)

    if form.is_valid():

        comment = form.save(commit=False)
        comment.user = request.user
        comment.pin = pin
        comment.save()

        html = render_to_string(
            "pin/components/comment.html",
            {
                "comment": comment,
                "level": 0,
                "pin": pin,
                "request": request,
            },
            request=request,
        )

        return JsonResponse({
            "success": True,
            "html": html,
        })

    return JsonResponse({
        "success": False,
        "errors": form.errors,
    }, status=400)


# @login_required
# def add_reply(request, pin_id, comment_id):

#     pin = get_object_or_404(Pin, id=pin_id)

#     parent_comment = get_object_or_404(Comment, id=comment_id, pin=pin)

#     if request.method == "POST":

#         form = CommentForm(request.POST)

#         if form.is_valid():

#             reply = form.save(commit=False)

#             reply.user = request.user
#             reply.pin = pin
#             reply.parent = parent_comment

#             reply.save()

#     return redirect("pin_detail", pin_id=pin.id)

@login_required
@require_POST
def add_reply(request, pin_id, comment_id):

    pin = get_object_or_404(Pin, id=pin_id)

    parent_comment = get_object_or_404(
        Comment,
        id=comment_id,
        pin=pin,
    )

    form = CommentForm(request.POST)

    if form.is_valid():

        reply = form.save(commit=False)

        reply.user = request.user
        reply.pin = pin
        reply.parent = parent_comment

        reply.save()

        html = render_to_string(
            "pin/components/comment.html",
            {
                "comment": reply,
                "level": 1,
                "pin": pin,
                "request": request,
            },
            request=request,
        )

        return JsonResponse({
            "success": True,
            "html": html,
        })

    return JsonResponse({
        "success": False,
        "errors": form.errors,
    }, status=400)


# @login_required
# def delete_comment(request, comment_id):

#     comment = get_object_or_404(Comment, id=comment_id)

#     if request.user != comment.user:
#         return redirect("pin_detail", pin_id=comment.pin.id)

#     if request.method == "POST":
#         comment.delete()

#     return redirect("pin_detail", pin_id=comment.pin.id)



@login_required
@require_POST
def delete_comment(request, comment_id):

    comment = get_object_or_404(
        Comment,
        id=comment_id,
        user=request.user
    )

    comment.delete()

    return JsonResponse({
        "success": True,
        "comment_id": comment_id
    })


@login_required
@require_POST
def follow_user(request, user_id):

    following_user = get_object_or_404(User, id=user_id)

    if request.user == following_user:
        return JsonResponse(
            {"error": "You cannot follow yourself"},
            status=400
        )

    follow, created = Follow.objects.get_or_create(
        follower=request.user,
        following=following_user,
    )

    if not created:
        follow.delete()
        followed = False
    else:
        followed = True

    followers_count = following_user.followers.count()

    return JsonResponse({
        "followed": followed,
        "followers_count": followers_count,
    })


def search_pins(request):
    query = request.GET.get("q", "").strip()

    pins = Pin.objects.filter(
        Q(title__icontains=query) |
        Q(description__icontains=query)
    )[:10] if query else []

    results = [
        {
            "title": pin.title,
            "image": pin.image.url,
            "url": f"/pin/{pin.id}/",
        }
        for pin in pins
    ]

    return JsonResponse({"results": results})


@login_required
@require_POST
def edit_comment(request, comment_id):

    comment = get_object_or_404(
        Comment,
        id=comment_id,
        user=request.user
    )

    form = CommentForm(request.POST, instance=comment)

    if form.is_valid():
        form.save()
        return JsonResponse({"text": comment.text})

    return JsonResponse({"error": "Invalid comment"}, status=400)



@login_required
@require_POST
def edit_pin_title(request, pin_id):

    pin = get_object_or_404(
        Pin,
        id=pin_id,
        user=request.user
    )

    title = request.POST.get("title", "").strip()

    if not title:
        return JsonResponse({"error": "Title cannot be empty"}, status=400)

    pin.title = title
    pin.save(update_fields=["title"])

    return JsonResponse({
        "success": True,
        "title": pin.title
    })


@login_required
def edit_pin(request, pin_id):
    pin = get_object_or_404(
        Pin,
        id=pin_id,
        user=request.user
    )

    if request.method == "POST":
        pin.title = request.POST.get("title", "").strip()
        pin.description = request.POST.get("description", "").strip()

        if request.FILES.get("image"):
            pin.image = request.FILES["image"]

        pin.save()

        return redirect("pin_detail", pin_id=pin.id)

    return render(request, "pin/edit_pin.html", {
        "pin": pin
    })