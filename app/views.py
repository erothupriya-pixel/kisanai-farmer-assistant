import json
import logging
import requests
from datetime import datetime, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.utils import timezone

from .models import FarmerProfile, ChatSession, ChatMessage, DailyFarmingTip, WeatherCache
from .ai_service import get_ai_response, get_daily_tip
from .forms import FarmerRegistrationForm, FarmerProfileForm

logger = logging.getLogger(__name__)


# ─── Public Views ─────────────────────────────────────────────────────────────

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'app/home.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = FarmerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            FarmerProfile.objects.create(
                user=user,
                location=form.cleaned_data.get('location', ''),
                primary_crops=form.cleaned_data.get('primary_crops', ''),
                preferred_language=form.cleaned_data.get('preferred_language', 'en'),
            )
            login(request, user)
            messages.success(request, 'Welcome to KisanAI! Your account is ready.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = FarmerRegistrationForm()
    return render(request, 'app/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'app/login.html')


def logout_view(request):
    logout(request)
    return redirect('home')


# ─── Protected Views ───────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    profile, _ = FarmerProfile.objects.get_or_create(user=request.user)
    sessions = ChatSession.objects.filter(user=request.user)[:5]
    daily_tip = get_daily_tip(profile.preferred_language)

    # Recent messages count
    recent_messages = ChatMessage.objects.filter(
        session__user=request.user,
        created_at__gte=timezone.now() - timedelta(days=7)
    ).count()

    context = {
        'profile': profile,
        'sessions': sessions,
        'daily_tip': daily_tip,
        'recent_messages': recent_messages,
        'total_sessions': sessions.count(),
    }
    return render(request, 'app/dashboard.html', context)


@login_required
def voice_assistant(request):
    profile, _ = FarmerProfile.objects.get_or_create(user=request.user)
    session = ChatSession.objects.create(
        user=request.user,
        language=profile.preferred_language,
        title=f"Voice Session {datetime.now().strftime('%d %b %H:%M')}"
    )
    context = {
        'profile': profile,
        'session': session,
        'language': profile.preferred_language,
    }
    return render(request, 'app/voice_assistant.html', context)


@login_required
def chat_view(request, session_id=None):
    profile, _ = FarmerProfile.objects.get_or_create(user=request.user)

    if session_id:
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    else:
        session = ChatSession.objects.create(
            user=request.user,
            language=profile.preferred_language,
            title=f"Chat {datetime.now().strftime('%d %b %H:%M')}"
        )
        return redirect('chat_session', session_id=session.id)

    messages_qs = session.messages.all()
    all_sessions = ChatSession.objects.filter(user=request.user)[:10]

    context = {
        'profile': profile,
        'session': session,
        'chat_messages': messages_qs,
        'all_sessions': all_sessions,
    }
    return render(request, 'app/chat.html', context)


@login_required
def profile_view(request):
    profile, _ = FarmerProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = FarmerProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = FarmerProfileForm(instance=profile)
    return render(request, 'app/profile.html', {'form': form, 'profile': profile})


@login_required
def chat_history(request):
    sessions = ChatSession.objects.filter(user=request.user)
    return render(request, 'app/chat_history.html', {'sessions': sessions})


@login_required
def delete_session(request, session_id):
    session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    session.delete()
    messages.success(request, 'Conversation deleted.')
    return redirect('chat_history')


# ─── API Endpoints ─────────────────────────────────────────────────────────────

@login_required
@require_http_methods(["POST"])
def api_chat(request):
    """Main chat/voice API endpoint"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id')
        language = data.get('language', 'en')
        input_type = data.get('input_type', 'text')

        if not user_message:
            return JsonResponse({'error': 'Message is required'}, status=400)

        # Get or create session
        if session_id:
            try:
                session = ChatSession.objects.get(id=session_id, user=request.user)
            except ChatSession.DoesNotExist:
                session = ChatSession.objects.create(
                    user=request.user, language=language,
                    title=user_message[:50]
                )
        else:
            session = ChatSession.objects.create(
                user=request.user, language=language,
                title=user_message[:50]
            )

        # Save user message
        ChatMessage.objects.create(
            session=session, role='user',
            content=user_message, input_type=input_type, language=language
        )

        # Get farmer context
        profile = getattr(request.user, 'farmer_profile', None)
        location = profile.location if profile else ''
        crops = profile.primary_crops if profile else ''

        # Get AI response
        ai_response = get_ai_response(user_message, language, location, crops)

        # Save AI message
        ChatMessage.objects.create(
            session=session, role='assistant',
            content=ai_response, language=language
        )

        # Update session
        session.updated_at = timezone.now()
        if not session.title or session.title == 'New Chat':
            session.title = user_message[:50]
        session.save()

        return JsonResponse({
            'response': ai_response,
            'session_id': session.id,
            'language': language,
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Chat API error: {e}")
        return JsonResponse({'error': 'Server error. Please try again.'}, status=500)


@login_required
def api_weather(request):
    """Weather API endpoint"""
    location = request.GET.get('location', '')
    profile = getattr(request.user, 'farmer_profile', None)

    if not location and profile:
        location = profile.location

    if not location:
        return JsonResponse({'error': 'Location required'}, status=400)

    # Check cache (30 min)
    try:
        cache = WeatherCache.objects.get(location__iexact=location)
        age = timezone.now() - cache.fetched_at
        if age < timedelta(minutes=30):
            return JsonResponse({'weather': cache.data, 'cached': True})
    except WeatherCache.DoesNotExist:
        pass

    # Fetch fresh weather
    api_key = settings.WEATHER_API_KEY
    if not api_key:
        # Return mock data for demo
        mock = _get_mock_weather(location)
        return JsonResponse({'weather': mock, 'demo': True})

    try:
        url = f"{settings.WEATHER_API_URL}?q={location},IN&appid={api_key}&units=metric"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        raw = resp.json()

        weather_data = {
            'location': raw.get('name', location),
            'country': raw.get('sys', {}).get('country', 'IN'),
            'temperature': round(raw['main']['temp']),
            'feels_like': round(raw['main']['feels_like']),
            'humidity': raw['main']['humidity'],
            'description': raw['weather'][0]['description'].title(),
            'icon': raw['weather'][0]['icon'],
            'wind_speed': raw.get('wind', {}).get('speed', 0),
            'visibility': raw.get('visibility', 0) // 1000,
            'pressure': raw['main']['pressure'],
            'rain_1h': raw.get('rain', {}).get('1h', 0),
            'farming_advice': _get_weather_farming_advice(raw),
        }

        # Cache it
        WeatherCache.objects.update_or_create(
            location=location, defaults={'data': weather_data}
        )
        return JsonResponse({'weather': weather_data})

    except Exception as e:
        logger.error(f"Weather API error: {e}")
        mock = _get_mock_weather(location)
        return JsonResponse({'weather': mock, 'demo': True})


@login_required
def api_daily_tip(request):
    profile = getattr(request.user, 'farmer_profile', None)
    language = request.GET.get('language', profile.preferred_language if profile else 'en')
    tip = get_daily_tip(language)
    return JsonResponse({'tip': tip})


@login_required
def api_session_messages(request, session_id):
    session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    msgs = list(session.messages.values('role', 'content', 'input_type', 'created_at'))
    for m in msgs:
        m['created_at'] = m['created_at'].strftime('%I:%M %p')
    return JsonResponse({'messages': msgs, 'session_id': session_id})


# ─── Helpers ───────────────────────────────────────────────────────────────────

def _get_mock_weather(location):
    import random
    conditions = [
        ('Partly Cloudy', '02d'), ('Sunny', '01d'),
        ('Light Rain', '10d'), ('Overcast', '04d'),
    ]
    cond, icon = random.choice(conditions)
    return {
        'location': location.title(),
        'country': 'IN',
        'temperature': random.randint(24, 38),
        'feels_like': random.randint(26, 42),
        'humidity': random.randint(45, 85),
        'description': cond,
        'icon': icon,
        'wind_speed': round(random.uniform(2, 15), 1),
        'visibility': random.randint(5, 10),
        'pressure': random.randint(1005, 1020),
        'rain_1h': 0,
        'farming_advice': 'Good conditions for field work today. Monitor soil moisture levels.',
    }


def _get_weather_farming_advice(raw):
    temp = raw['main']['temp']
    humidity = raw['main']['humidity']
    rain = raw.get('rain', {}).get('1h', 0)
    wind = raw.get('wind', {}).get('speed', 0)

    if rain > 5:
        return "Heavy rain expected. Avoid spraying pesticides/fertilizers. Ensure proper field drainage."
    elif temp > 40:
        return "Extreme heat! Irrigate early morning. Avoid field work between 11am-4pm."
    elif humidity > 85:
        return "High humidity may trigger fungal diseases. Monitor crops closely."
    elif wind > 20:
        return "Strong winds. Avoid spraying. Support tall crops if needed."
    else:
        return "Favorable conditions for farming activities today."
