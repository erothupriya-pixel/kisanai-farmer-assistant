from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Protected pages
    path('dashboard/', views.dashboard, name='dashboard'),
    path('voice/', views.voice_assistant, name='voice_assistant'),
    path('chat/', views.chat_view, name='chat'),
    path('chat/<int:session_id>/', views.chat_view, name='chat_session'),
    path('chat/history/', views.chat_history, name='chat_history'),
    path('chat/delete/<int:session_id>/', views.delete_session, name='delete_session'),
    path('profile/', views.profile_view, name='profile'),

    # API endpoints
    path('api/chat/', views.api_chat, name='api_chat'),
    path('api/weather/', views.api_weather, name='api_weather'),
    path('api/tip/', views.api_daily_tip, name='api_daily_tip'),
    path('api/session/<int:session_id>/messages/', views.api_session_messages, name='api_session_messages'),
]
