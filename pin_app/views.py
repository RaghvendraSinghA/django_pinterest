
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
import logging


logger = logging.getLogger(__name__)


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

            logger.info(
                "User %s is creating a Pin",
                request.user.id
            )

            try:
                pin.save()
            except Exception:
                logger.exception(
                    "Failed to create Pin for user %s",
                    request.user.id
                )
                raise

            transaction.on_commit(
                lambda: index_pin.delay(pin.id),
                robust=True
            )

            try:
                upload_pin_image.delay(pin.id)
            except Exception:
                logger.exception(
                    "Failed to queue image upload for Pin %s",
                    pin.id
                )
                raise

            logger.info(
                "Pin %s created successfully for user %s",
                pin.id,
                request.user.id
            )

            return redirect("home")

        logger.warning(
            "User %s submitted an invalid Pin form",
            request.user.id
        )

    else:
        form = PinForm()

    return render(request, "pin/create_pin.html", {"form": form})


def pin_detail(request, pin_id):

    pin = get_object_or_404(Pin, id=pin_id)

    logger.debug(
        "User %s accessed Pin %s",
        getattr(request.user, "id", None),
        pin.id
    )

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
            "boards": boards,
        },
    )


@login_required
def delete_pin(request, pin_id):

    pin = get_object_or_404(Pin, id=pin_id)

    if request.user != pin.user:
        logger.warning(
            "User %s attempted to delete Pin %s without permission",
            request.user.id,
            pin.id
        )
        return redirect("pin_detail", pin_id=pin.id)

    if request.method == "POST":

        image_name = pin.image.name if pin.image else None
        deleted_pin_id = pin.id

        logger.info(
            "User %s is deleting Pin %s",
            request.user.id,
            deleted_pin_id
        )

        try:
            pin.delete()
        except Exception:
            logger.exception(
                "Failed to delete Pin %s",
                deleted_pin_id
            )
            raise

        logger.info(
            "Pin %s deleted successfully",
            deleted_pin_id
        )

        # Delete the Elasticsearch document after DB commit
        transaction.on_commit(
            lambda: delete_pin_from_elasticsearch.delay(deleted_pin_id)
        )

        if image_name:
            try:
                delete_pin_image.delay(image_name)
            except Exception:
                logger.exception(
                    "Failed to queue image deletion for Pin %s",
                    deleted_pin_id
                )
                raise

        return redirect("home")

    return redirect("pin_detail", pin_id=pin.id)


@login_required
@require_POST
def like_pin(request, pin_id):

    pin = get_object_or_404(Pin, id=pin_id)

    try:
        like, created = Like.objects.get_or_create(
            user=request.user,
            pin=pin,
        )

        if not created:
            like.delete()
            liked = False

            logger.info(
                "User %s unliked Pin %s",
                request.user.id,
                pin.id
            )

        else:
            liked = True

            logger.info(
                "User %s liked Pin %s",
                request.user.id,
                pin.id
            )

        like_count = pin.likes.count()

    except Exception:
        logger.exception(
            "Failed to toggle like for Pin %s by user %s",
            pin.id,
            request.user.id
        )
        raise

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

        try:
            comment.save()
        except Exception:
            logger.exception(
                "Failed to add comment to Pin %s by user %s",
                pin.id,
                request.user.id
            )
            raise

        logger.info(
            "User %s added Comment %s to Pin %s",
            request.user.id,
            comment.id,
            pin.id
        )

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

    logger.warning(
        "User %s submitted an invalid comment for Pin %s",
        request.user.id,
        pin.id
    )

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

        try:
            reply.save()
        except Exception:
            logger.exception(
                "Failed to add reply to Comment %s on Pin %s",
                parent_comment.id,
                pin.id
            )
            raise

        logger.info(
            "User %s added Reply %s to Comment %s",
            request.user.id,
            reply.id,
            parent_comment.id
        )

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

    logger.warning(
        "User %s submitted an invalid reply for Comment %s",
        request.user.id,
        parent_comment.id
    )

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

    try:
        comment.delete()
    except Exception:
        logger.exception(
            "Failed to delete Comment %s by user %s",
            comment_id,
            request.user.id
        )
        raise

    logger.info(
        "User %s deleted Comment %s",
        request.user.id,
        comment_id
    )

    return JsonResponse({
        "success": True,
        "comment_id": comment_id
    })


@login_required
@require_POST
def follow_user(request, user_id):

    following_user = get_object_or_404(User, id=user_id)

    if request.user == following_user:

        logger.warning(
            "User %s attempted to follow themselves",
            request.user.id
        )

        return JsonResponse(
            {"error": "You cannot follow yourself"},
            status=400
        )

    try:
        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            following=following_user,
        )

        if not created:
            follow.delete()
            followed = False

            logger.info(
                "User %s unfollowed User %s",
                request.user.id,
                following_user.id
            )

        else:
            followed = True

            logger.info(
                "User %s followed User %s",
                request.user.id,
                following_user.id
            )

        followers_count = following_user.followers.count()

    except Exception:
        logger.exception(
            "Failed to toggle follow from User %s to User %s",
            request.user.id,
            following_user.id
        )
        raise

    return JsonResponse({
        "followed": followed,
        "followers_count": followers_count,
    })


def search_pins(request):

    query = request.GET.get("q", "").strip()

    if not query:
        logger.warning(
            "User %s submitted an empty search query",
            getattr(request.user, "id", None)
        )
        return JsonResponse({"results": []})

    logger.info(
        "User %s searched Pins with query: %s",
        getattr(request.user, "id", None),
        query
    )

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

    logger.info(
        "Search completed for query '%s'. Found %s Pins",
        query,
        len(results)
    )

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

        try:
            form.save()
        except Exception:
            logger.exception(
                "Failed to edit Comment %s by user %s",
                comment.id,
                request.user.id
            )
            raise

        logger.info(
            "User %s edited Comment %s",
            request.user.id,
            comment.id
        )

        return JsonResponse({"text": comment.text})

    logger.warning(
        "User %s submitted invalid data while editing Comment %s",
        request.user.id,
        comment.id
    )

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
        logger.warning(
            "User %s attempted to set an empty title for Pin %s",
            request.user.id,
            pin.id
        )

        return JsonResponse({"error": "Title cannot be empty"}, status=400)

    old_title = pin.title

    try:
        pin.title = title
        pin.save(update_fields=["title"])
    except Exception:
        logger.exception(
            "Failed to update title for Pin %s",
            pin.id
        )
        raise

    logger.info(
        "User %s changed Pin %s title from '%s' to '%s'",
        request.user.id,
        pin.id,
        old_title,
        title
    )

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

        old_title = pin.title

        pin.title = request.POST.get("title", "").strip()
        pin.description = request.POST.get("description", "").strip()

        if request.FILES.get("image"):

            old_image_name = pin.image.name
            pin.image = request.FILES["image"]

            if old_image_name and old_image_name != pin.image.name:

                try:
                    pin.save()
                except Exception:
                    logger.exception(
                        "Failed to update Pin %s",
                        pin.id
                    )
                    raise

                try:
                    pin.image.storage.delete(old_image_name)
                except Exception:
                    logger.exception(
                        "Failed to delete old image %s for Pin %s",
                        old_image_name,
                        pin.id
                    )
                    raise

                logger.info(
                    "User %s updated Pin %s and replaced its image",
                    request.user.id,
                    pin.id
                )

                transaction.on_commit(
                    lambda: index_pin.delay(pin.id)
                )

                return redirect("pin_detail", pin_id=pin.id)

        try:
            pin.save()
        except Exception:
            logger.exception(
                "Failed to update Pin %s by user %s",
                pin.id,
                request.user.id
            )
            raise

        logger.info(
            "User %s updated Pin %s. Title changed from '%s' to '%s'",
            request.user.id,
            pin.id,
            old_title,
            pin.title
        )

        transaction.on_commit(
            lambda: index_pin.delay(pin.id)
        )

        return redirect("pin_detail", pin_id=pin.id)

    return render(request, "pin/edit_pin.html", {
        "pin": pin
    })
