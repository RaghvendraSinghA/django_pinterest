from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Board(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="boards",
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    pins = models.ManyToManyField(
        "pin_app.Pin",
        related_name="saved_in_boards",
        blank=True,
    )

    def __str__(self):
        return self.name