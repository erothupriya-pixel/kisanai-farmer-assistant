#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────
#  KisanAI — Render Build Script
#  Runs automatically during Render deployment
# ─────────────────────────────────────────────────────────
set -o errexit   # exit on error

echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "📁 Collecting static files..."
python manage.py collectstatic --no-input

echo "🗄️  Running database migrations..."
python manage.py migrate

echo "✅ Build complete!"
