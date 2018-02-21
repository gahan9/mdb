from django import forms
from .models import DirData


class DirDataForm(forms.ModelForm):

    class Meta:
        model = DirData
        fields = ['filename','path','extension']
