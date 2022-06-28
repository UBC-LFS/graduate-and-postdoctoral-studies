from django import forms

from django.contrib.auth.models import User
from .models import AccessLevel, CustomField


class LocalLoginForm(forms.Form):
    username = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter'
        })
    )
    password = forms.CharField(
        max_length=200,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter'
        })
    )


class AccessLevelForm(forms.ModelForm):
    class Meta:
        model = AccessLevel
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={ 'class': 'form-control' })
        }
        help_texts = {
            'name': 'This field is unique. Maximum characters is 20.'
        }


class UserForm(forms.ModelForm):
    ''' Member model form '''
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'is_superuser', 'is_active']
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email',
            'username': 'CWL'
        }
        widgets = {
            'first_name': forms.TextInput(attrs={ 'required': True, 'class': 'form-control' }),
            'last_name': forms.TextInput(attrs={ 'required': True, 'class': 'form-control' }),
            'email': forms.EmailInput(attrs={ 'required': True, 'class': 'form-control' }),
            'username': forms.TextInput(attrs={ 'required': True, 'class': 'form-control' })
        }
        help_texts = {
            'first_name': 'Maximum length is 30 characters.',
            'last_name': 'Maximum length is 150 characters.',
            'email': 'Maximum length is 254 characters.',
            'username': 'Maximum length is 150 characters.',
            'is_superuser': "This field is necessary for Masquerade. If an user's access level is an administrator, please select this field."
        }


class CustomFieldForm(forms.ModelForm):
    accesslevels = forms.ModelMultipleChoiceField(
        required=True,
        queryset=AccessLevel.objects.all(),
        widget=forms.CheckboxSelectMultiple()
    )
    class Meta:
        model = CustomField
        fields = ['accesslevels']


class CustomFieldEditForm(forms.ModelForm):
    accesslevels = forms.ModelMultipleChoiceField(
        required=True,
        queryset=AccessLevel.objects.all(),
        widget=forms.CheckboxSelectMultiple()
    )
    class Meta:
        model = CustomField
        fields = ['user', 'accesslevels']
        widgets = {
            'user': forms.HiddenInput()
        }
