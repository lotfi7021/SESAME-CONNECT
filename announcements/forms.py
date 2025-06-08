from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Announcement, Message, Category

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=15, required=False)
    bio = forms.CharField(widget=forms.Textarea, required=False)
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'student_id', 'password1', 'password2', 
                 'first_name', 'last_name', 'phone_number', 'bio', 'profile_picture']

class AnnouncementForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="Select a category (optional)",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Announcement
        fields = ['title', 'content', 'category', 'announcement_type', 'price', 'image']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'announcement_type': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Type your message here...'}),
        } 
        labels = {
            'content': ''  # This removes the label
        }