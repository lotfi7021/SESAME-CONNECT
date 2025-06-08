from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    student_id = models.AutoField(primary_key=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', default='default.jpg')
    bio = models.TextField(max_length=500, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.username} ({self.student_id})"

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=30, default='tag', 
                          help_text="Bootstrap icon class name")
    
    @classmethod
    def create_default_categories(cls):
        default_categories = [
             ("Other", "Items that don't fit other categories", "question-circle"),
            ("Books", "Textbooks and reading materials", "book"),
            ("Electronics", "Devices and gadgets", "laptop"),
            ("Furniture", "Home and office furniture", "chair"),
            ("Clothing", "Apparel and accessories", "tshirt"),
            ("Services", "Offered services", "tools"),
            ("Events", "Campus events", "calendar-event"),
            ("Housing", "Accommodation listings", "house-door"),
            ("Jobs", "Employment opportunities", "briefcase")
        ]
        
        for name, desc, icon in default_categories:
            cls.objects.get_or_create(
                name=name, 
                defaults={
                    'description': desc,
                    'icon': icon
                }
            )

    def __str__(self):
        return self.name

class Announcement(models.Model):
    ANNOUNCEMENT_TYPES = [
        ('SELL', 'For Sale'),
        ('EXCHANGE', 'Exchange'),
        ('LOST', 'Lost and Found'),
        ('EVENT', 'Event'),
        ('OTHER', 'Other'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='announcements')
    category = models.ForeignKey(
            Category, 
            on_delete=models.SET_NULL, 
            null=True, 
            blank=True,
            related_name='announcement'  # This should match what you use in the view
    )   
    announcement_type = models.CharField(max_length=10, choices=ANNOUNCEMENT_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='announcement_images/', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver}"
