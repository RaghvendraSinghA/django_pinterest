from django.db import models
from django.contrib.auth.models import User


class Pin(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pins")

    title = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    image = models.ImageField(upload_to="pins/")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# def __str__(self):    return self.title


# This is not a database field.
# It tells Python/Django:
# "When you need to represent a Pin as text, show its title."

# For example, without __str__, Django admin might show something like:
# Pin object (1)
# Pin object (2)
# Pin object (3)


class Like(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    pin = models.ForeignKey(Pin, on_delete=models.CASCADE)

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
