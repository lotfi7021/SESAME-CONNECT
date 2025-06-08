from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/<str:username>/', views.profile, name='profile'),
    
    path('announcement/new/', views.create_announcement, name='create-announcement'),
    path('announcement/<int:pk>/', views.announcement_detail, name='announcement-detail'),
    path('announcement/<int:pk>/update/', views.update_announcement, name='update-announcement'),
    path('announcement/<int:pk>/delete/', views.delete_announcement, name='delete-announcement'),
    
    path('messages/', views.messages_list, name='messages'),
    path('messages/new/<int:user_id>/', views.create_message, name='create-message'),
    path("ask/", views.chatbot_view, name="chatbot"),


    
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('change-password/', views.change_password, name='change_password'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 