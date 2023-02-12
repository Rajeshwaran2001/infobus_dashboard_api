from django import forms
from .models import Franchise
from django.contrib.auth.models import User


class FranchiseForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }


class FranchiseUserForm(forms.ModelForm):
    class Meta:
        model = Franchise
        fields = ['address', 'mobile_no_1', 'photo', 'district']
