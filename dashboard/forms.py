from django import forms
from .models import Franchise
from django.contrib.auth.models import User
from api.District.models import District

class FranchiseForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }
        district = forms.ModelMultipleChoiceField(queryset=District.objects.all(), required=True,
                                                  widget=forms.CheckboxSelectMultiple)


class FranchiseUserForm(forms.ModelForm):
    class Meta:
        model = Franchise
        fields = ['address', 'mobile_no_1', 'photo', 'district']
