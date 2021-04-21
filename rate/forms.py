from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.forms import ModelForm

from .models import *


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class ContactForm(forms.Form):
    email = forms.EmailField(max_length=50)
    subject = forms.CharField(max_length=150)
    message = forms.CharField(widget=forms.Textarea, max_length=2000)


class ReviewerForm(ModelForm):
    class Meta:
        model = Reviewer
        fields = ['name', 'email', 'phone']

class SongForm(ModelForm):
    class Meta:
        model = Song
        fields = ['name', 'author', 'url']
