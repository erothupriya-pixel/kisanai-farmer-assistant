from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import FarmerProfile


class FarmerRegistrationForm(UserCreationForm):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('hi', 'हिंदी (Hindi)'),
        ('te', 'తెలుగు (Telugu)'),
    ]

    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'placeholder': 'your@email.com'}))
    location = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'placeholder': 'e.g. Warangal, Telangana'}))
    primary_crops = forms.CharField(max_length=500, required=False, widget=forms.TextInput(attrs={'placeholder': 'e.g. Rice, Cotton, Maize'}))
    preferred_language = forms.ChoiceField(choices=LANGUAGE_CHOICES, initial='en')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Choose a username'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-input')
        self.fields['password1'].widget.attrs['placeholder'] = 'Create password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm password'


class FarmerProfileForm(forms.ModelForm):
    class Meta:
        model = FarmerProfile
        fields = ['location', 'state', 'primary_crops', 'land_area', 'preferred_language', 'phone']
        widgets = {
            'location': forms.TextInput(attrs={'placeholder': 'Your city/village'}),
            'state': forms.TextInput(attrs={'placeholder': 'Your state'}),
            'primary_crops': forms.TextInput(attrs={'placeholder': 'Rice, Wheat, Cotton...'}),
            'land_area': forms.NumberInput(attrs={'placeholder': 'Area in acres', 'step': '0.5'}),
            'phone': forms.TextInput(attrs={'placeholder': '+91 XXXXXXXXXX'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-input')
