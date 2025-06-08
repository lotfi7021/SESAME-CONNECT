from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import User, Announcement, Message, Category
from .forms import UserRegisterForm, AnnouncementForm, MessageForm
from django.contrib.auth.forms import PasswordChangeForm
from collections import defaultdict
from django.contrib import messages as django_messages
from django.db.models import Q
from django.db import models
from django.urls import reverse
from django.http import JsonResponse
import json
import subprocess




@login_required(login_url='login')
def home(request):
    category_id = request.GET.get('category')
    
    # Use the correct related_name 'announcement' (singular) instead of 'announcements'
    categories = Category.objects.annotate(
        announcement_count=models.Count('announcement',  # Changed from 'announcements'
                                      filter=models.Q(announcement__is_active=True)))
    
    if category_id:
        announcements = Announcement.objects.filter(
            is_active=True,
            category__id=category_id
        ).select_related('author', 'category').order_by('-created_at')
        selected_category = int(category_id)
    else:
        announcements = Announcement.objects.filter(
            is_active=True
        ).select_related('author', 'category').order_by('-created_at')
        selected_category = None

    context = {
        'announcements': announcements,
        'categories': categories,
        'selected_category': selected_category,
        'total_count': announcements.count() if not category_id else None,
    }
    return render(request, 'announcements/home.html', context)


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'compte/register.html', {'form': form})

@login_required(login_url='login')
def chatbot_view(request):
    if request.method == "POST":
        user_input = json.loads(request.body).get("message", "")

    
        result = subprocess.run(
    ["ollama", "run", "phi3", user_input],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    encoding='utf-8'  
)
        return JsonResponse({"response": result.stdout})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in successfully!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'compte/login.html')

@login_required(login_url='login')
def logout_view(request):
    logout(request)
    messages.info(request, 'Logged out successfully!')
    return redirect('login')

@login_required(login_url='login')
def profile(request, username):
    user = get_object_or_404(User, username=username)
    announcements = Announcement.objects.filter(author=user, is_active=True)
    context = {
        'profile_user': user,  # This is correct
        'announcements': announcements,
    }
    return render(request, 'profile/profile.html', context)

@login_required(login_url='login')
def create_announcement(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.author = request.user
            announcement.save()
            messages.success(request, 'Announcement created successfully!')
            return redirect('announcement-detail', pk=announcement.pk)
    else:
        form = AnnouncementForm()
    return render(request, 'announcements/announcement_form.html', {'form': form})

@login_required(login_url='login')
def announcement_detail(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    if request.method == 'POST' and request.user.is_authenticated:
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = announcement.author
            message.announcement = announcement
            message.save()
            messages.success(request, 'Message sent successfully!')
            return redirect('announcement-detail', pk=pk)
    else:
        form = MessageForm()
    context = {
        'announcement': announcement,
        'form': form,
    }
    return render(request, 'announcements/announcement_detail.html', context)

@login_required(login_url='login')
def update_announcement(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    if request.user != announcement.author:
        messages.error(request, 'You are not authorized to edit this announcement.')
        return redirect('announcement-detail', pk=pk)
    
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES, instance=announcement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Announcement updated successfully!')
            return redirect('announcement-detail', pk=pk)
    else:
        form = AnnouncementForm(instance=announcement)
    return render(request, 'announcements/announcement_form.html', {'form': form})

@login_required(login_url='login')
def delete_announcement(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    if request.user != announcement.author:
        messages.error(request, 'You are not authorized to delete this announcement.')
        return redirect('announcement-detail', pk=pk)
    
    if request.method == 'POST':
        announcement.is_active = False
        announcement.save()
        messages.success(request, 'Announcement deleted successfully!')
        return redirect('home')
    return render(request, 'announcements/announcement_confirm_delete.html', {'announcement': announcement})

from collections import defaultdict


@login_required(login_url='login')
def messages_list(request):
    # Get all messages involving current user
    all_messages = Message.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).select_related('sender', 'receiver', 'announcement').order_by('-created_at')

    # Organize conversations
    conversations = []
    seen_user_ids = set()

    for msg in all_messages:
        # Determine the other user in conversation
        other_user = msg.receiver if msg.sender == request.user else msg.sender
        
        if other_user and other_user.pk not in seen_user_ids:
            seen_user_ids.add(other_user.pk)
            conversations.append({
                'other_user': other_user,
                'last_message': msg,
                'unread': (msg.receiver == request.user and not msg.is_read)
            })

    # Handle message submission
    recipient_id = request.GET.get('recipient')
    form = None
    recipient = None
    
    if recipient_id:
        try:
            recipient = User.objects.get(pk=recipient_id)
            if request.method == 'POST':
                form = MessageForm(request.POST)
                if form.is_valid():
                    # Create new message
                    new_message = Message.objects.create(
                        sender=request.user,
                        receiver=recipient,
                        content=form.cleaned_data['content'],
                        announcement=form.cleaned_data.get('announcement')
                    )
                    messages.success(request, 'Message sent successfully!')
                    
                    # Mark previous messages as read
                    Message.objects.filter(
                        sender=recipient,
                        receiver=request.user,
                        is_read=False
                    ).update(is_read=True)
                    
                    return redirect('{}?recipient={}'.format(reverse('messages'), recipient_id))
        except (User.DoesNotExist, ValueError):
            messages.error(request, 'Recipient not found')
            recipient = None
    else:
        form = MessageForm()

    context = {
        'conversations': conversations,
        'active_recipient': recipient,
        'form': form,
        'user': request.user,
        'conversation': Message.objects.filter(
            Q(sender=request.user, receiver=recipient) |
            Q(sender=recipient, receiver=request.user)
        ).order_by('created_at') if recipient else None
    }
    return render(request, 'messages/messages_list.html', context)


from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Message, User
from .forms import MessageForm

@login_required(login_url='login')
def create_message(request, user_id):
    receiver = get_object_or_404(User, id=user_id)
    announcement = None

    # Get the full conversation between users
    conversation = Message.objects.filter(
        Q(sender=request.user, receiver=receiver) | 
        Q(sender=receiver, receiver=request.user)
    ).order_by('created_at')

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = receiver
            
            announcement_id = request.POST.get('announcement_id')
            if announcement_id:
                announcement = get_object_or_404(Announcement, id=announcement_id)
                message.announcement = announcement
            
            message.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': {
                        'content': message.content,
                        'created_at': message.created_at.strftime("%b %d, %I:%M %p"),
                        'sender': {
                            'username': message.sender.username,
                            'profile_picture': message.sender.profile_picture.url
                        }
                    }
                })
            
            return redirect('create-message', user_id=user_id)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors.get_json_data()
            })
    else:
        form = MessageForm()
        announcement_id = request.GET.get('announcement_id')
        if announcement_id:
            announcement = get_object_or_404(Announcement, id=announcement_id)
            initial = {'content': f"Hi, I'm interested in your announcement: {announcement.title}\n\n"}
            form = MessageForm(initial=initial)

    context = {
        'form': form,
        'receiver': receiver,
        'conversation': conversation,
        'announcement': announcement,
        'user': request.user  # Make sure user is in context
    }
    return render(request, 'messages/message_form.html', context)

@login_required(login_url='login')
def edit_profile(request):
    if request.method == 'POST':
        # Update user information
        user = request.user
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.bio = request.POST.get('bio')
        
        # Handle profile picture
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']
        
        try:
            user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile', username=user.username)
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
    
    return render(request, 'profile/edit_profile.html')

@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile', username=request.user.username)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'compte/change_password.html', {'form': form})



