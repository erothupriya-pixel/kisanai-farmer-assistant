/* ═══════════════════════════════════════════════════════
   KisanAI — dashboard.js
   Weather widget, Quick-chat, Daily tip refresh
═══════════════════════════════════════════════════════ */

const dashLang     = window.USER_LANG     || 'en';
const userLocation = window.USER_LOCATION || '';
let   quickSessionId = null;

// ── Init ──────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  loadWeather(userLocation || 'Hyderabad');

  const qi = document.getElementById('quickInput');
  if (qi) qi.addEventListener('keydown', e => {
    if (e.key === 'Enter') sendQuickChat();
  });
});

// ═══════════════════════════════════════════════════════
//  WEATHER
// ═══════════════════════════════════════════════════════
async function loadWeather(locationOverride) {
  const input = document.getElementById('weatherInput');
  const loc   = locationOverride || input?.value?.trim() || 'Hyderabad';

  const display = document.getElementById('weatherDisplay');
  if (display) display.innerHTML = '<div class="weather-loading"><i class="fas fa-spinner fa-spin"></i> Loading weather…</div>';

  try {
    const data = await window.KisanAI.getJSON(`/api/weather/?location=${encodeURIComponent(loc)}`);
    renderWeather(data.weather, data.demo);
  } catch(e) {
    if (display) display.innerHTML = '<div class="weather-loading" style="color:#ef4444"><i class="fas fa-exclamation-circle"></i> Could not load weather</div>';
  }
}

function renderWeather(w, isDemo) {
  const display = document.getElementById('weatherDisplay');
  const badge   = document.getElementById('weatherBadge');
  const tempSt  = document.getElementById('dashTemp');
  const descSt  = document.getElementById('dashWeatherDesc');

  if (badge) badge.querySelector('span').textContent = w.location;
  if (tempSt) tempSt.textContent = `${w.temperature}°C`;
  if (descSt) descSt.textContent = w.description;

  // Weather icon emoji mapping
  const iconMap = {
    '01': '☀️', '02': '⛅', '03': '☁️', '04': '☁️',
    '09': '🌧️', '10': '🌦️', '11': '⛈️', '13': '❄️', '50': '🌫️',
  };
  const iconKey = (w.icon || '01d').substring(0, 2);
  const emoji   = iconMap[iconKey] || '🌤️';

  if (display) display.innerHTML = `
    <div class="weather-main">
      <div style="font-size:2.5rem;margin-bottom:4px">${emoji}</div>
      <div class="weather-temp">${w.temperature}°C</div>
      <div class="weather-desc">${w.description} · Feels ${w.feels_like}°C</div>
      <div class="weather-details">
        <div class="weather-detail"><i class="fas fa-tint"></i> ${w.humidity}% Humidity</div>
        <div class="weather-detail"><i class="fas fa-wind"></i> ${w.wind_speed} m/s Wind</div>
        <div class="weather-detail"><i class="fas fa-eye"></i> ${w.visibility} km Vis.</div>
        <div class="weather-detail"><i class="fas fa-tachometer-alt"></i> ${w.pressure} hPa</div>
      </div>
      ${w.farming_advice ? `<div class="weather-advice"><i class="fas fa-leaf"></i> ${w.farming_advice}</div>` : ''}
      ${isDemo ? '<p style="font-size:0.7rem;color:var(--text-muted);margin-top:8px">Demo data · Add WEATHER_API_KEY for live data</p>' : ''}
    </div>`;
}

// ═══════════════════════════════════════════════════════
//  QUICK CHAT
// ═══════════════════════════════════════════════════════
async function sendQuickChat() {
  const input = document.getElementById('quickInput');
  const lang  = document.getElementById('quickLang')?.value || dashLang;
  const msg   = input?.value?.trim();
  if (!msg) return;
  if (input) input.value = '';

  appendQuickBubble('user', msg);

  // Loading bubble
  const loadId = 'qload-' + Date.now();
  appendQuickBubble('assistant', '<i class="fas fa-spinner fa-spin"></i>', loadId);

  try {
    const data = await window.KisanAI.postJSON('/api/chat/', {
      message: msg, session_id: quickSessionId,
      language: lang, input_type: 'text',
    });
    quickSessionId = data.session_id;
    const loadEl = document.getElementById(loadId);
    if (loadEl) loadEl.innerHTML = window.KisanAI.renderMarkdown(data.response || '—');
  } catch(e) {
    const loadEl = document.getElementById(loadId);
    if (loadEl) loadEl.innerHTML = '⚠️ Error. Please try again.';
  }

  window.KisanAI.scrollToBottom(document.getElementById('quickMessages'));
}

function appendQuickBubble(role, html, id) {
  const area = document.getElementById('quickMessages');
  if (!area) return;
  const div = document.createElement('div');
  div.className = `chat-bubble ${role === 'user' ? 'user-bubble' : 'assistant-bubble'}`;
  if (id) div.id = id;
  div.innerHTML = html;
  area.appendChild(div);
  window.KisanAI.scrollToBottom(area);
}

// ═══════════════════════════════════════════════════════
//  DAILY TIP
// ═══════════════════════════════════════════════════════
async function refreshTip() {
  const tipEl = document.getElementById('dailyTip');
  if (!tipEl) return;
  tipEl.innerHTML = '<p><i class="fas fa-spinner fa-spin"></i> Loading new tip…</p>';
  try {
    const data = await window.KisanAI.getJSON(`/api/tip/?language=${dashLang}`);
    tipEl.innerHTML = `<p>${data.tip}</p>`;
  } catch(e) {
    tipEl.innerHTML = '<p>Could not load tip. Try again.</p>';
  }
}

// Expose
window.loadWeather   = loadWeather;
window.sendQuickChat = sendQuickChat;
window.refreshTip    = refreshTip;
