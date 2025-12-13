from django import forms
from django.contrib.auth import get_user_model
from .models import Post, Item

User = get_user_model()

class UserCreateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','email','age','photo','video','password']
        widgets = {'password': forms.PasswordInput()}

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content','image','video']

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description', 'price', 'image']