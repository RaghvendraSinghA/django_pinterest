from .models import Board
from django import forms


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