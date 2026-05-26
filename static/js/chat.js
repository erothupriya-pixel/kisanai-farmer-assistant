/* ═══════════════════════════════════════════════════════
   KisanAI — chat.js
   Text chatbot with inline voice input and TTS toggle
═══════════════════════════════════════════════════════ */

let chatLang       = window.USER_LANG || 'en';
let chatSessionId  = window.SESSION_ID || null;
let ttsOn          = false;
let voiceRecording = false;
let chatRecognition= null;
const chatSynth    = window.speechSynthesis;

const LANG_CODES = { en: 'en-IN', hi: 'hi-IN', te: 'te-IN' };

// ── Init ──────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  scrollToBottom();

  const ta = document.getElementById('chatInput');
  if (ta) {
    ta.addEventListener('keydown', handleChatKey);
    ta.addEventListener('input', () => autoResize(ta));
  }

  // Init voice for chat
  initChatVoice();

  // Scroll to bottom of existing messages
  setTimeout(scrollToBottom, 100);
});

function scrollToBottom() {
  const area = document.getElementById('chatMessages');
  if (area) area.scrollTop = area.scrollHeight;
}

// ── Language ──────────────────────────────────────────
function updateLanguage(lang) {
  chatLang = lang;
  if (chatRecognition) chatRecognition.lang = LANG_CODES[lang] || 'en-IN';
}

// ── Keyboard handler ──────────────────────────────────
function handleChatKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendChatMessage(); }
}

function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 150) + 'px';
}

// ── Send message ──────────────────────────────────────
async function sendChatMessage() {
  const ta  = document.getElementById('chatInput');
  const msg = ta?.value?.trim();
  if (!msg) return;

  ta.value = '';
  autoResize(ta);

  appendMessage('user', msg, 'text');
  showTyping(true);

  try {
    const data = await window.KisanAI.postJSON('/api/chat/', {
      message: msg, session_id: chatSessionId,
      language: chatLang, input_type: 'text',
    });
    chatSessionId = data.session_id;
    showTyping(false);
    const reply = data.response || 'Sorry, could not get a response.';
    appendMessage('assistant', reply, 'text');
    if (ttsOn) speakChatText(reply);
    updateSessionTitle(msg);
  } catch(err) {
    showTyping(false);
    appendMessage('assistant', '⚠️ Network error. Please check connection and try again.', 'text');
  }
}

function sendSample(q) {
  const ta = document.getElementById('chatInput');
  if (ta) { ta.value = q; sendChatMessage(); }
}

// ── Render message ────────────────────────────────────
function appendMessage(role, text, inputType = 'text') {
  const area = document.getElementById('chatMessages');
  if (!area) return;

  // Remove welcome screen on first message
  const welcome = area.querySelector('.chat-welcome');
  if (welcome) welcome.remove();

  const time  = new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
  const isUser = role === 'user';

  const div = document.createElement('div');
  div.className = `chat-msg ${isUser ? 'user-msg' : 'ai-msg'}`;
  div.innerHTML = `
    <div class="msg-avatar">
      ${isUser ? '<i class="fas fa-user"></i>' : '<span>🌾</span>'}
    </div>
    <div class="msg-bubble">
      <div class="msg-content">${window.KisanAI.renderMarkdown(escapeHtml(text))}</div>
      <div class="msg-meta">
        <span class="msg-time">${time}</span>
        ${inputType === 'voice' ? '<span class="msg-voice-tag"><i class="fas fa-microphone-alt"></i></span>' : ''}
        ${!isUser ? `<button class="msg-speak-btn" onclick="speakChatText(${JSON.stringify(text)})" title="Listen"><i class="fas fa-volume-up"></i></button>` : ''}
      </div>
    </div>`;

  area.appendChild(div);
  scrollToBottom();
}

// ── Typing indicator ──────────────────────────────────
function showTyping(show) {
  const ind = document.getElementById('typingIndicator');
  if (ind) { ind.style.display = show ? 'flex' : 'none'; if (show) scrollToBottom(); }
}

// ── TTS toggle ────────────────────────────────────────
function speakToggle() {
  ttsOn = !ttsOn;
  const btn = document.getElementById('speakToggleBtn');
  if (btn) {
    btn.style.background = ttsOn ? 'rgba(34,197,94,0.15)' : '';
    btn.style.color      = ttsOn ? 'var(--green-400)' : '';
    btn.title = ttsOn ? 'Voice output ON' : 'Voice output OFF';
  }
}

function speakChatText(text) {
  if (!chatSynth) return;
  chatSynth.cancel();
  const clean = text.replace(/[*_#`]/g, '').replace(/\n/g, '. ').substring(0, 600);
  const utt = new SpeechSynthesisUtterance(clean);
  utt.lang  = LANG_CODES[chatLang] || 'en-IN';
  utt.rate  = 0.9;
  const voices = chatSynth.getVoices();
  const lang0  = utt.lang.split('-')[0];
  const v = voices.find(v => v.lang.startsWith(utt.lang))
         || voices.find(v => v.lang.startsWith(lang0))
         || voices.find(v => v.lang.startsWith('en'));
  if (v) utt.voice = v;
  chatSynth.speak(utt);
}

function speakText(text) { speakChatText(text); }

// ── Voice input in chat ───────────────────────────────
function initChatVoice() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) {
    const btn = document.getElementById('voiceInChatBtn');
    if (btn) { btn.disabled = true; btn.title = 'Voice not supported in this browser'; }
    return;
  }
  chatRecognition = new SR();
  chatRecognition.continuous     = false;
  chatRecognition.interimResults = true;
  chatRecognition.lang           = LANG_CODES[chatLang] || 'en-IN';

  chatRecognition.onresult = e => {
    let interim = '', final = '';
    for (let i = e.resultIndex; i < e.results.length; i++) {
      const t = e.results[i][0].transcript;
      e.results[i].isFinal ? (final += t) : (interim += t);
    }
    const ta = document.getElementById('chatInput');
    if (ta) ta.value = final || interim;
  };

  chatRecognition.onend = () => {
    const ta = document.getElementById('chatInput');
    const text = ta?.value?.trim();
    stopVoiceInChat();
    if (text) { sendChatMessage(); }
  };

  chatRecognition.onerror = () => stopVoiceInChat();
}

function toggleVoiceInChat() {
  if (voiceRecording) { stopVoiceInChat(); return; }
  if (!chatRecognition) return;
  chatRecognition.lang = LANG_CODES[chatLang] || 'en-IN';
  try {
    chatRecognition.start();
    voiceRecording = true;
    const btn = document.getElementById('voiceInChatBtn');
    const ico = document.getElementById('voiceChatIcon');
    if (btn) btn.classList.add('recording');
    if (ico) ico.className = 'fas fa-stop';
  } catch(e) { console.warn(e); }
}

function stopVoiceInChat() {
  voiceRecording = false;
  try { chatRecognition?.stop(); } catch(e) {}
  const btn = document.getElementById('voiceInChatBtn');
  const ico = document.getElementById('voiceChatIcon');
  if (btn) btn.classList.remove('recording');
  if (ico) ico.className = 'fas fa-microphone';
}

// ── Session title update ──────────────────────────────
function updateSessionTitle(msg) {
  const titleEl = document.getElementById('chatSessionTitle');
  if (titleEl && (titleEl.textContent === 'New Chat' || !titleEl.textContent)) {
    titleEl.textContent = msg.substring(0, 40) + (msg.length > 40 ? '…' : '');
  }
}

// ── Utility ───────────────────────────────────────────
function escapeHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// Expose globals
window.sendChatMessage    = sendChatMessage;
window.sendSample         = sendSample;
window.handleChatKey      = handleChatKey;
window.autoResize         = autoResize;
window.updateLanguage     = updateLanguage;
window.speakToggle        = speakToggle;
window.speakText          = speakText;
window.speakChatText      = speakChatText;
window.toggleVoiceInChat  = toggleVoiceInChat;
