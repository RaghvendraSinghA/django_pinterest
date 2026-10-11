from django import forms
from .models import Pin, Comment, Board


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



class BoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ["name", "description"]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Give your board a name",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "placeholder": "Describe your board...",
                    "rows": 3,
                }
            ),
        }