from django import forms
from django.contrib.auth.models import User
from .models import Office


class OfficeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }


class OfficeUserForm(forms.ModelForm):
    class Meta:
        model = Office
        fields = ['mobile_no_1']
