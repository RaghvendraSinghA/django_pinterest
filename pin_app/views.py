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
from .tasks import upload_pin_image, delete_pin_image, index_pin, delete_pin_from_elasticsearch
from pinterest_config.search import fuzzy_search_pins
from django.db import transaction




@login_required
def create_pin(request):

    if request.method == "POST":
        form = PinForm(request.POST, request.FILES)

        if form.is_valid():
            pin = form.save(commit=False)
            pin.user = request.user
            pin.upload_status = "pending"

            uploaded_image = request.FILES["image"]
            pin.temp_image = uploaded_image
            pin.save()

            transaction.on_commit(
                lambda: index_pin.delay(pin.id)
            )

            upload_pin_image.delay(pin.id)

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

    if request.user != pin.user:
        return redirect("pin_detail", pin_id=pin.id)

    if request.method == "POST":

        image_name = pin.image.name if pin.image else None
        deleted_pin_id = pin.id
        pin.delete()

        # Delete the Elasticsearch document after DB commit
        transaction.on_commit(
            lambda: delete_pin_from_elasticsearch.delay(deleted_pin_id)
        )

        if image_name:
            delete_pin_image.delay(image_name)

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

    if not query:
        return JsonResponse({"results": []})

    # Search in Elasticsearch
    search_results = fuzzy_search_pins(query)

    # Extract PostgreSQL Pin IDs in Elasticsearch relevance order
    pin_ids = []

    for result in search_results:
        pin_id = result["_source"]["id"]
        pin_ids.append(pin_id)

    # Fetch actual Pin objects from PostgreSQL
    pins = Pin.objects.filter(id__in=pin_ids)

    # Create a dictionary to find a Pin quickly using its ID
    pins_by_id = {}

    for pin in pins:
        pins_by_id[pin.id] = pin

    # Build results in Elasticsearch's relevance order
    results = []

    for pin_id in pin_ids:
        if pin_id in pins_by_id:
            pin = pins_by_id[pin_id]

            result = {
                "title": pin.title,
                "image": pin.image.url if pin.image else None,
                "url": f"/pin/{pin.id}/",
            }

            results.append(result)

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

    transaction.on_commit(
        lambda: index_pin.delay(pin.id)
    )

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
            old_image_name = pin.image.name
            pin.image = request.FILES["image"]

            if old_image_name and old_image_name != pin.image.name:
                pin.save()
                pin.image.storage.delete(old_image_name)
                transaction.on_commit(
                    lambda: index_pin.delay(pin.id)
                )

                return redirect("pin_detail", pin_id=pin.id)

        pin.save()
        transaction.on_commit(
            lambda: index_pin.delay(pin.id)
        )

        return redirect("pin_detail", pin_id=pin.id)

    return render(request, "pin/edit_pin.html", {
        "pin": pin
    })

