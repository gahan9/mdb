from django import forms
from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):
    """Form to allow user to log in to system"""
    username = forms.CharField(label="UserName", max_length=30,
                               widget=forms.TextInput(
                                   attrs={'class': 'form-control', 'type': 'text',
                                          'aria-describedby': "emailHelp",
                                          'id': 'email', 'name': 'email',
                                          'placeholder': 'Enter UserName'}))
    password = forms.CharField(label="Password", max_length=30,
                               widget=forms.TextInput(
                                   attrs={'class': 'form-control',
                                          'name': 'password', 'id': 'password',
                                          'type': 'password', 'placeholder': 'Password'}))
