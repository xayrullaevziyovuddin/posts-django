from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Comment



class SharePostForm(forms.Form):
    post_id = forms.IntegerField(widget=forms.HiddenInput)
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter recipient email',
        'required': True
    }))

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['email', 'text']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email *',
                'maxlength': '100',
                'required': True
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Comment',
                'maxlength': '400'
            }),
        }


class SignupForm(UserCreationForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "Password"})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "Confirm Password"})
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "First Name"}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Last Name"}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Username"}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': "Email"}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].help_text = None


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
