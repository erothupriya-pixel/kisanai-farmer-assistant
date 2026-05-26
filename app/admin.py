from django.contrib import admin
from .models import FarmerProfile, ChatSession, ChatMessage, DailyFarmingTip, WeatherCache


@admin.register(FarmerProfile)
class FarmerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'state', 'preferred_language', 'created_at']
    search_fields = ['user__username', 'location', 'state']
    list_filter = ['preferred_language', 'state']


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'language', 'created_at']
    list_filter = ['language']
    search_fields = ['user__username', 'title']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'role', 'input_type', 'language', 'created_at']
    list_filter = ['role', 'input_type', 'language']


@admin.register(DailyFarmingTip)
class DailyFarmingTipAdmin(admin.ModelAdmin):
    list_display = ['title', 'language', 'season', 'is_active', 'created_at']
    list_filter = ['language', 'season', 'is_active']


@admin.register(WeatherCache)
class WeatherCacheAdmin(admin.ModelAdmin):
    list_display = ['location', 'fetched_at']
