from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import storages


class Pin(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pins")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # image = models.ImageField(upload_to="pins/")
    image = models.ImageField(
        upload_to="pins/",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    UPLOAD_STATUS = [
        ("pending", "Pending"),
        ("uploaded", "Uploaded"),
        ("failed", "Failed"),
    ]

    upload_status = models.CharField(
        max_length=20,
        choices=UPLOAD_STATUS,
        default="uploaded",
    )

    temp_image = models.FileField(
        upload_to="temp/pins/",
        storage=storages["temp"],
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.title

print("TEMP STORAGE:", Pin._meta.get_field("temp_image").storage.base_url)
# def __str__(self):    return self.title


# This is not a database field.
# It tells Python/Django:
# "When you need to represent a Pin as text, show its title in django admin page."

# For example, without __str__, Django admin might show something like:
# Pin object (1)
# Pin object (2)
# Pin object (3)


class Like(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    pin = models.ForeignKey(Pin, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "pin"], name="unique_user_pin_like")
        ]


class Comment(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pin = models.ForeignKey(Pin, on_delete=models.CASCADE, related_name="comments")
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text


class Follow(models.Model):

    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following"
    )

    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followers"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "following"], name="unique_follow"
            )
        ]


