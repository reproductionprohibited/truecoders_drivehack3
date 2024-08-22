from typing import Any, Mapping
from django import forms
from django.forms.renderers import BaseRenderer
from django.forms.utils import ErrorList


class UploadFileForm(forms.Form):
    file = forms.FileField()

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
