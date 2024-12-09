from django import forms

from application.models import Recette


class RecetteForm(forms.ModelForm):
    class Meta:
        model = Recette
        exclude = ["quantites", "etapes"]