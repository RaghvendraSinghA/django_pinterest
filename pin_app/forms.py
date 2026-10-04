from django import forms
from .models import Pin, Comment


class PinForm(forms.ModelForm):

    class Meta:
        model = Pin
        fields = [
            "title",
            "description",
            "image",
        ]




class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = [
            "text",
        ]

        widgets = {
            "text": forms.Textarea(
                attrs={
                    "placeholder": "Add a comment...",
                    "rows": 3,
                }
            )
        }