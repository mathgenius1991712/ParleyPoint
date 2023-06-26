from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from .models import Profile, ChatMessage

class UserUpdateForm(UserChangeForm):
    password = None

    class Meta:
        model = User
        fields = ['username']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image', 'bio']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].widget.attrs.update({'class': 'form-control'})
        self.fields['bio'].widget.attrs.update({'class': 'form-control'})
        
        
class ChatMessageForm(forms.ModelForm):
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 2, 'cols': 50}))

    class Meta:
        model = ChatMessage
        fields = ['message']
