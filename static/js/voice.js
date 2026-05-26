/* ═══════════════════════════════════════════════════════
   KisanAI — voice.js
   Speech-to-Text (Web Speech API) + Text-to-Speech (SpeechSynthesis)
═══════════════════════════════════════════════════════ */

// ── State ─────────────────────────────────────────────
let currentLang      = window.USER_LANG || 'en';
let sessionId        = window.SESSION_ID || null;
let isListening      = false;
let isSpeaking       = false;
let recognition      = null;
let lastAiText       = '';
let voiceOutputOn    = true;
let speechSynth      = window.speechSynthesis;

// ── Language config ───────────────────────────────────
const LANG_CONFIG = {
  en: { code: 'en-IN', name: 'English',  welcome: '🌾 Hello! I am KisanAI. Ask me any farming question!', sub: 'Press the microphone or type your question below' },
  hi: { code: 'hi-IN', name: 'हिंदी',    welcome: '🌾 नमस्ते! मैं KisanAI हूँ। कोई भी खेती का सवाल पूछें!', sub: 'माइक्रोफोन दबाएं या नीचे टाइप करें' },
  te: { code: 'te-IN', name: 'తెలుగు',   welcome: '🌾 నమస్కారం! నేను KisanAI. మీ వ్యవసాయ సమస్యలు అడగండి.', sub: 'మైక్రోఫోన్ నొక్కండి లేదా క్రింద టైప్ చేయండి' },
};

const SAMPLE_Q = {
  en: ['Rice pest control?', 'Best fertilizer for cotton?', 'When to irrigate wheat?', 'Kharif crop suggestions'],
  hi: ['चावल में कीट नियंत्रण?', 'कपास के लिए खाद?', 'गेहूं में सिंचाई कब?', 'खरीफ फसल सुझाव'],
  te: ['వరిలో చీడ నియంత్రణ?', 'పత్తికి ఏ ఎరువు?', 'గోధుమకు నీరు ఎప్పుడు?', 'ఖరీఫ్ పంట సూచనలు'],
};

// ── DOM helpers ───────────────────────────────────────
const $  = id => document.getElementById(id);
const el = {
  get conversation()  { return $('voiceConversation'); },
  get messages()      { return $('messagesArea'); },
  get micBtn()        { return $('mainMicBtn'); },
  get micIcon()       { return $('micIcon'); },
  get micRings()      { return $('micRingsContainer'); },
  get statusDot()     { return $('statusDot'); },
  get statusText()    { return $('statusText'); },
  get voiceWave()     { return $('voiceWave'); },
  get textInput()     { return $('voiceTextInput'); },
  get welcomeText()   { return $('welcomeText'); },
  get welcomeSub()    { return $('welcomeSub'); },
  get sampleQ()       { return $('sampleQuestions'); },
  get micHint()       { return $('micHint'); },
};

// ── Init ──────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  setLanguage(currentLang, true);
  initSpeechRecognition();
  el.textInput?.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendTextMessage(); }
  });
  $('volumeSlider')?.addEventListener('input', e => { /* volume applied on speak */ });
});

// ── Language ──────────────────────────────────────────
function setLanguage(lang, silent = false) {
  currentLang = lang;
  document.querySelectorAll('.lang-pill').forEach(p => {
    p.classList.toggle('active', p.dataset.lang === lang);
  });
  const cfg = LANG_CONFIG[lang] || LANG_CONFIG.en;
  if (el.welcomeText) el.welcomeText.textContent = cfg.welcome;
  if (el.welcomeSub)  el.welcomeSub.textContent  = cfg.sub;
  if (el.sampleQ) {
    el.sampleQ.innerHTML = (SAMPLE_Q[lang] || SAMPLE_Q.en)
      .map(q => `<span onclick="askSample('${q.replace(/'/g,"\\'")}') ">${q}</span>`)
      .join('');
  }
  if (recognition) { recognition.lang = cfg.code; }
}

// ── Speech Recognition ────────────────────────────────
function initSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    setStatus('Voice not supported in this browser. Please use Chrome.', 'error');
    if (el.micBtn) { el.micBtn.disabled = true; el.micBtn.style.opacity = '0.4'; }
    return;
  }
  recognition = new SpeechRecognition();
  recognition.continuous    = false;
  recognition.interimResults= true;
  recognition.maxAlternatives = 1;
  recognition.lang = (LANG_CONFIG[currentLang] || LANG_CONFIG.en).code;

  recognition.onstart = () => {
    isListening = true;
    setStatus('Listening…', 'listening');
    el.micBtn?.classList.add('listening-btn');
    el.micRings?.classList.add('listening-active');
    el.voiceWave?.classList.add('active');
    if (el.micIcon) el.micIcon.className = 'fas fa-stop';
    if (el.micHint) el.micHint.textContent = 'Tap to stop';
    stopSpeaking();
  };

  recognition.onresult = e => {
    let interim = '', final = '';
    for (let i = e.resultIndex; i < e.results.length; i++) {
      const t = e.results[i][0].transcript;
      e.results[i].isFinal ? (final += t) : (interim += t);
    }
    // Show interim in input
    if (el.textInput) el.textInput.value = final || interim;
    if (final) { stopRecognition(); processVoiceInput(final.trim()); }
  };

  recognition.onerror = e => {
    console.error('Speech error', e.error);
    stopRecognition();
    const msgs = { 'no-speech': 'No speech detected. Try again.', 'not-allowed': 'Microphone access denied. Please allow mic permission.', 'network': 'Network error. Check connection.' };
    setStatus(msgs[e.error] || `Error: ${e.error}`, 'error');
  };

  recognition.onend = () => { if (isListening) stopRecognition(); };
}

function toggleListening() {
  if (isListening) { stopRecognition(); return; }
  if (!recognition) { initSpeechRecognition(); }
  recognition.lang = (LANG_CONFIG[currentLang] || LANG_CONFIG.en).code;
  try { recognition.start(); } catch(e) { console.warn(e); }
}

function stopRecognition() {
  isListening = false;
  try { recognition?.stop(); } catch(e) {}
  el.micBtn?.classList.remove('listening-btn');
  el.micRings?.classList.remove('listening-active');
  el.voiceWave?.classList.remove('active');
  if (el.micIcon) el.micIcon.className = 'fas fa-microphone';
  if (el.micHint) el.micHint.textContent = 'Tap to start speaking';
  setStatus('Ready — Press mic to speak', 'ready');
}

// ── Voice Input Flow ──────────────────────────────────
async function processVoiceInput(text) {
  if (!text) return;
  if (el.textInput) el.textInput.value = '';
  addMessage('user', text, 'voice');
  await sendToAI(text, 'voice');
}

function sendTextMessage() {
  const text = el.textInput?.value?.trim();
  if (!text) return;
  if (el.textInput) el.textInput.value = '';
  addMessage('user', text, 'text');
  sendToAI(text, 'text');
}

function askSample(q) { addMessage('user', q, 'text'); sendToAI(q, 'text'); }

// ── API Call ──────────────────────────────────────────
async function sendToAI(message, inputType = 'text') {
  setStatus('Thinking…', 'thinking');
  hideWelcome();

  try {
    const data = await window.KisanAI.postJSON('/api/chat/', {
      message, session_id: sessionId, language: currentLang, input_type: inputType,
    });
    sessionId = data.session_id;
    const reply = data.response || 'Sorry, I could not process that.';
    addMessage('assistant', reply, 'text');
    lastAiText = reply;
    if (voiceOutputOn) speakText(reply);
    setStatus('Ready — Press mic to speak', 'ready');
  } catch(err) {
    console.error(err);
    addMessage('assistant', '⚠️ Connection error. Please check your internet and try again.', 'text');
    setStatus('Error — Try again', 'error');
  }
}

// ── Message Rendering ─────────────────────────────────
function addMessage(role, text, inputType = 'text') {
  const container = el.messages;
  if (!container) return;

  const wrap = document.createElement('div');
  wrap.className = 'voice-msg-pair';

  const time = new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
  const isUser = role === 'user';

  wrap.innerHTML = `
    <div class="${isUser ? 'voice-user-msg' : 'voice-ai-msg'}">
      <div class="msg-ava ${isUser ? 'user-ava' : 'ai-ava'}">
        ${isUser ? '<i class="fas fa-user"></i>' : '🌾'}
      </div>
      <div>
        <div class="voice-bubble ${isUser ? 'voice-user-bubble' : 'voice-ai-bubble'}">
          ${window.KisanAI.renderMarkdown(escapeHtml(text))}
        </div>
        <div class="voice-msg-meta">
          ${inputType === 'voice' ? '<i class="fas fa-microphone-alt" style="color:var(--green-400)"></i>' : ''}
          <span>${time}</span>
          ${!isUser ? `<button class="speak-this" onclick="speakText(${JSON.stringify(text)})"><i class="fas fa-volume-up"></i> Listen</button>` : ''}
        </div>
      </div>
    </div>`;

  container.appendChild(wrap);
  window.KisanAI.scrollToBottom(el.conversation);
}

function hideWelcome() {
  const w = document.querySelector('.voice-welcome');
  if (w) { w.style.display = 'none'; }
}

// ── Text-to-Speech ────────────────────────────────────
function speakText(text) {
  if (!speechSynth) return;
  stopSpeaking();

  // Clean text for speech (remove markdown symbols)
  const clean = text.replace(/[*_#`]/g, '').replace(/\n/g, '. ').substring(0, 500);

  const utt = new SpeechSynthesisUtterance(clean);
  utt.lang  = (LANG_CONFIG[currentLang] || LANG_CONFIG.en).code;
  utt.rate  = parseFloat($('speedSlider')?.value || '0.9');
  utt.pitch = 1.0;
  utt.volume= parseFloat($('volumeSlider')?.value || '1');

  // Pick best voice
  const voices = speechSynth.getVoices();
  const langCode = utt.lang.split('-')[0];
  const match = voices.find(v => v.lang.startsWith(utt.lang))
             || voices.find(v => v.lang.startsWith(langCode))
             || voices.find(v => v.lang.startsWith('en'));
  if (match) utt.voice = match;

  utt.onstart = () => { isSpeaking = true; setStatus('Speaking…', 'speaking'); };
  utt.onend   = () => { isSpeaking = false; setStatus('Ready — Press mic to speak', 'ready'); };
  utt.onerror = () => { isSpeaking = false; };

  speechSynth.speak(utt);
}

function stopSpeaking()  { speechSynth?.cancel(); isSpeaking = false; }
function replaySpeech()  { if (lastAiText) speakText(lastAiText); }

// ── Status ────────────────────────────────────────────
function setStatus(msg, state = 'ready') {
  if (el.statusText) el.statusText.textContent = msg;
  const dot = el.statusDot;
  if (dot) { dot.className = 'status-dot'; if (state !== 'ready') dot.classList.add(state); }
}

// ── Utility ───────────────────────────────────────────
function escapeHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function clearConversation() {
  if (!confirm('Clear all messages?')) return;
  const m = el.messages;
  if (m) m.innerHTML = '';
  const w = document.querySelector('.voice-welcome');
  if (w) w.style.display = '';
  stopSpeaking();
  setStatus('Ready — Press mic to speak', 'ready');
}

// Expose globals
window.setLanguage        = setLanguage;
window.toggleListening    = toggleListening;
window.sendTextMessage    = sendTextMessage;
window.askSample          = askSample;
window.speakText          = speakText;
window.stopSpeaking       = stopSpeaking;
window.replaySpeech       = replaySpeech;
window.clearConversation  = clearConversation;
