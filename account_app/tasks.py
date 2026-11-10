from celery import shared_task
from django.core.files import File
from .models import Profile


@shared_task
def upload_profile_pic(profile_id):

    profile = Profile.objects.get(id=profile_id)

    if not profile.temp_profile_pic:
        return "No temporary profile picture found"

    old_image_name = profile.profile_pic.name if profile.profile_pic else None

    try:
        with profile.temp_profile_pic.open("rb") as image_file:
            profile.profile_pic.save(
                profile.temp_profile_pic.name.split("/")[-1],
                File(image_file),
                save=False,
            )

        profile.upload_status = "uploaded"
        profile.save(update_fields=["profile_pic", "upload_status"])

        if old_image_name:
            profile.profile_pic.storage.delete(old_image_name)

        delete_temp_profile_pic.apply_async(
            args=[profile.id],
            countdown=300,
        )

        return "Profile picture uploaded successfully"

    except Exception:
        profile.upload_status = "failed"
        profile.save(update_fields=["upload_status"])
        raise


@shared_task
def delete_temp_profile_pic(profile_id):

    try:
        profile = Profile.objects.get(id=profile_id)

        if profile.temp_profile_pic:
            profile.temp_profile_pic.delete(save=False)
            profile.temp_profile_pic = None
            profile.save(update_fields=["temp_profile_pic"])

        return "Temporary profile picture deleted"

    except Profile.DoesNotExist:
        return "Profile not found"