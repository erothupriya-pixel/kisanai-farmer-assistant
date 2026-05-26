# 🌾 KisanAI — AI Voice Based Farmer Assistant

A full-stack Django web application that provides AI-powered agricultural advice to farmers in **Telugu, Hindi, and English** using voice and text.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🎤 Voice Assistant | Speak in Telugu / Hindi / English, get spoken AI replies |
| 🤖 AI Chatbot | Expert crop, pest, fertilizer & irrigation advice |
| 🌦️ Weather Widget | Real-time weather + farming recommendations |
| 👤 Farmer Profile | Location, crops, land area, language preference |
| 💬 Chat History | All conversations saved & searchable |
| 📱 Mobile Responsive | Works on phones, tablets, desktops |
| 🌐 Multi-language | Telugu (తెలుగు), Hindi (हिंदी), English |

---

## 🗂️ Project Structure

```
farmer_ai_project/
├── manage.py
├── requirements.txt
├── Procfile                  ← Render/Heroku deployment
├── render.yaml               ← Render config
├── build.sh                  ← Render build script
├── runtime.txt               ← Python version
├── .env.example              ← Copy to .env and fill keys
├── .gitignore
│
├── backend/                  ← Django project config
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── app/                      ← Main Django app
│   ├── models.py             ← FarmerProfile, ChatSession, ChatMessage...
│   ├── views.py              ← All page + API views
│   ├── urls.py               ← URL routing
│   ├── forms.py              ← Registration & profile forms
│   ├── admin.py              ← Django admin config
│   ├── ai_service.py         ← Gemini AI integration + smart fallbacks
│   └── migrations/
│       └── 0001_initial.py
│
├── templates/app/
│   ├── base.html             ← Navbar, toasts, layout shell
│   ├── home.html             ← Landing page
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html        ← Main dashboard
│   ├── voice_assistant.html  ← Voice AI page
│   ├── chat.html             ← Text chatbot
│   ├── chat_history.html
│   └── profile.html
│
└── static/
    ├── css/
    │   └── main.css          ← Full responsive stylesheet
    └── js/
        ├── main.js           ← Global utilities
        ├── voice.js          ← Speech-to-text + TTS engine
        ├── chat.js           ← Chat + inline voice
        └── dashboard.js      ← Weather + quick chat + tips
```

---

## 🚀 Local Setup (Step-by-Step)

### 1. Prerequisites
- Python 3.10+ installed
- pip package manager
- Git (optional)

### 2. Clone / Download the project
```bash
git clone https://github.com/your-repo/kisanai.git
cd farmer_ai_project
```

### 3. Create virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Set up environment variables
```bash
cp .env.example .env
```
Open `.env` and fill in your API keys:
```
SECRET_KEY=any-random-long-string
DEBUG=True
GEMINI_API_KEY=your_key_here        ← Get free at makersuite.google.com
WEATHER_API_KEY=your_key_here       ← Get free at openweathermap.org
```

> **Note:** The app works WITHOUT API keys using smart built-in responses. Add keys for live AI + weather.

### 6. Run database migrations
```bash
python manage.py migrate
```

### 7. Create admin user (optional)
```bash
python manage.py createsuperuser
```

### 8. Start the server
```bash
python manage.py runserver
```

### 9. Open in browser
```
http://127.0.0.1:8000
```

---

## 🌐 Deploy on Render (Free)

### Step 1 — Push to GitHub
```bash
git init
git add .
git commit -m "Initial KisanAI commit"
git remote add origin https://github.com/YOUR_USERNAME/kisanai.git
git push -u origin main
```

### Step 2 — Create Render Web Service
1. Go to [render.com](https://render.com) → New → Web Service
2. Connect your GitHub repository
3. Render auto-detects `render.yaml` — click **Create Web Service**

### Step 3 — Add Environment Variables in Render Dashboard
| Key | Value |
|-----|-------|
| `SECRET_KEY` | any random 50-char string |
| `DEBUG` | `False` |
| `GEMINI_API_KEY` | your Gemini key |
| `WEATHER_API_KEY` | your OpenWeatherMap key |

### Step 4 — Deploy
Render runs `build.sh` automatically → your app is live!

---

## 🌐 Deploy on PythonAnywhere (Free)

1. Upload project files via **Files** tab
2. Open **Bash console**:
```bash
pip3.11 install --user -r requirements.txt
python manage.py migrate
python manage.py collectstatic --no-input
```
3. Go to **Web** tab → Add new web app → Manual config → Python 3.11
4. Set WSGI file path to: `/home/yourusername/farmer_ai_project/backend/wsgi.py`
5. Add environment variables in the **Web** tab → Environment variables section
6. Reload web app

---

## 🔑 API Keys — How to Get Them FREE

### Gemini AI (Google)
1. Go to https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy and paste into `.env`

### OpenWeatherMap (Weather)
1. Go to https://openweathermap.org/api
2. Sign up free
3. Go to API Keys tab
4. Copy your default key
5. Paste into `.env` as `WEATHER_API_KEY`

> ⚠️ New OpenWeatherMap keys take ~2 hours to activate.

---

## 🤖 AI Capabilities

The AI assistant (`ai_service.py`) can answer questions about:

- **Crop Selection** — best crops for your location and season
- **Pest Control** — identify pests, treatment methods, dosage
- **Fertilizers** — NPK recommendations, organic alternatives
- **Irrigation** — water scheduling, drip/sprinkler advice
- **Soil Health** — pH management, testing, improvement
- **Weather Advice** — what to do before/after rain
- **Government Schemes** — PM-KISAN, soil health cards, subsidies
- **Crop Calendar** — Kharif, Rabi, Zaid season guides

Works in **Telugu, Hindi, and English** — automatically detects the language.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 4.2 + Django REST Framework |
| Frontend | HTML5 + CSS3 + Vanilla JavaScript |
| Database | SQLite (dev) / PostgreSQL (prod) |
| AI | Google Gemini 1.5 Flash |
| Voice STT | Web Speech API (browser-native) |
| Voice TTS | SpeechSynthesis API (browser-native) |
| Weather | OpenWeatherMap API |
| Deployment | Render / PythonAnywhere / Heroku |
| Static Files | WhiteNoise |

---

## 🧑‍💻 Admin Panel

Access Django admin at: `http://127.0.0.1:8000/admin/`

Manage:
- Farmer profiles
- Chat sessions & messages
- Daily farming tips
- Weather cache

---

## 📱 Browser Compatibility for Voice

| Browser | Speech-to-Text | Text-to-Speech |
|---------|---------------|---------------|
| Chrome (recommended) | ✅ Full support | ✅ Full support |
| Edge | ✅ Full support | ✅ Full support |
| Firefox | ❌ Not supported | ✅ Supported |
| Safari (iOS 16+) | ✅ Supported | ✅ Supported |

> 💡 Recommend Chrome for best voice experience.

---

## 🐛 Troubleshooting

**Microphone not working?**
- Allow microphone permission when browser asks
- Make sure you're on HTTPS (required in production) or localhost
- Use Chrome browser

**AI not responding?**
- Check `GEMINI_API_KEY` in `.env`
- App works without key using built-in farming responses

**Static files not loading?**
```bash
python manage.py collectstatic --no-input
```

**Migration errors?**
```bash
python manage.py migrate --run-syncdb
```

---

## 📄 License

MIT License — Free for personal and commercial use.

---

## 🙏 Credits

Built with ❤️ for Indian Farmers  
Powered by Django · Google Gemini · Web Speech API
