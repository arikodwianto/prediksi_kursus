from django import forms
from .models import DataLatih, DataUji
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")
        if password and confirm and password != confirm:
            raise forms.ValidationError("Password dan konfirmasi tidak sama.")
        return cleaned_data


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Username')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')


class DataLatihForm(forms.ModelForm):
    class Meta:
        model = DataLatih
        fields = ['nama', 'hari', 'waktu', 'durasi', 'paket', 'status']
        widgets = {
            'nama': forms.TextInput(attrs={'class': 'form-control'}),
            'hari': forms.Select(attrs={'class': 'form-control'}),
            'waktu': forms.Select(attrs={'class': 'form-control'}),
            'durasi': forms.NumberInput(attrs={'class': 'form-control'}),
            'paket': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

class DataUjiForm(forms.ModelForm):
    class Meta:
        model = DataUji
        fields = ['nama', 'hari', 'waktu', 'durasi', 'paket']
        widgets = {
            'nama': forms.TextInput(attrs={'class': 'form-control'}),
            'hari': forms.Select(attrs={'class': 'form-control'}),
            'waktu': forms.Select(attrs={'class': 'form-control'}),
            'durasi': forms.NumberInput(attrs={'class': 'form-control'}),
            'paket': forms.Select(attrs={'class': 'form-control'}),
        }
