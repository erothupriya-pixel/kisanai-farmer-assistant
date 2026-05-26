from django.db import models
from django.contrib.auth.models import User


class FarmerProfile(models.Model):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('hi', 'Hindi'),
        ('te', 'Telugu'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farmer_profile')
    location = models.CharField(max_length=200, blank=True, help_text="City or village name")
    state = models.CharField(max_length=100, blank=True)
    primary_crops = models.CharField(max_length=500, blank=True, help_text="Comma-separated list of crops")
    land_area = models.FloatField(null=True, blank=True, help_text="Land area in acres")
    preferred_language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')
    phone = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_crops_list(self):
        if self.primary_crops:
            return [c.strip() for c in self.primary_crops.split(',')]
        return []


class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(max_length=200, blank=True)
    language = models.CharField(max_length=5, default='en')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Session {self.id} - {self.user.username}"


class ChatMessage(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]
    INPUT_TYPE_CHOICES = [
        ('text', 'Text'),
        ('voice', 'Voice'),
    ]

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    input_type = models.CharField(max_length=10, choices=INPUT_TYPE_CHOICES, default='text')
    language = models.CharField(max_length=5, default='en')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"


class DailyFarmingTip(models.Model):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('hi', 'Hindi'),
        ('te', 'Telugu'),
    ]
    SEASON_CHOICES = [
        ('kharif', 'Kharif (Jun-Sep)'),
        ('rabi', 'Rabi (Oct-Mar)'),
        ('zaid', 'Zaid (Mar-Jun)'),
        ('all', 'All Seasons'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')
    season = models.CharField(max_length=10, choices=SEASON_CHOICES, default='all')
    category = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class WeatherCache(models.Model):
    location = models.CharField(max_length=200)
    data = models.JSONField()
    fetched_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['location']

    def __str__(self):
        return f"Weather: {self.location}"
