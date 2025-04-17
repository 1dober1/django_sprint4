from django import forms
from .models import User, Post


class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class AddPostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ['author', 'is_published']
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'})
        }

    def save(self, commit=True, author=None):
        instance = super().save(commit=False)
        if author:
            instance.author = author
        if commit:
            instance.save()
        return instance
