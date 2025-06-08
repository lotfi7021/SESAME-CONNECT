from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Announcement, Category, Message

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'student_id', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email', 'student_id', 'first_name', 'last_name')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'student_id', 'phone_number', 'bio', 'profile_picture')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'announcement_type', 'category', 'created_at', 'is_active')
    list_filter = ('announcement_type', 'category', 'is_active', 'created_at')
    search_fields = ('title', 'content', 'author__username')
    date_hierarchy = 'created_at'

class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'announcement', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('content', 'sender__username', 'receiver__username')

admin.site.register(User, CustomUserAdmin)
admin.site.register(Announcement, AnnouncementAdmin)
admin.site.register(Category)
admin.site.register(Message, MessageAdmin)
