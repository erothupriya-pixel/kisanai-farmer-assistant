/* ═══════════════════════════════════════════════════
   KisanAI — main.js  (global utilities)
═══════════════════════════════════════════════════ */

// ── Hamburger nav ─────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('navToggle');
  const menu   = document.getElementById('mobileMenu');
  if (toggle && menu) {
    toggle.addEventListener('click', () => menu.classList.toggle('open'));
  }

  // Auto-dismiss toasts after 4 s
  document.querySelectorAll('[data-auto-dismiss]').forEach(el => {
    setTimeout(() => el.remove(), 4000);
  });
});

// ── CSRF helper ───────────────────────────────────
function getCsrfToken() {
  const el = document.querySelector('[name=csrfmiddlewaretoken]');
  if (el) return el.value;
  // Try from meta or window global
  return window.CSRF_TOKEN || '';
}

// ── POST JSON helper ──────────────────────────────
async function postJSON(url, data) {
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken(),
    },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

// ── GET JSON helper ───────────────────────────────
async function getJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

// ── Markdown-lite renderer ────────────────────────
function renderMarkdown(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/^#{1,3}\s(.+)$/gm, '<strong>$1</strong>')
    .replace(/\n/g, '<br/>');
}

// ── Simple show/hide spinner ──────────────────────
function setLoading(btn, loading) {
  if (!btn) return;
  if (loading) {
    btn.dataset.originalText = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    btn.disabled = true;
  } else {
    btn.innerHTML = btn.dataset.originalText || btn.innerHTML;
    btn.disabled = false;
  }
}

// ── Scroll element to bottom ──────────────────────
function scrollToBottom(el) {
  if (el) el.scrollTop = el.scrollHeight;
}

window.KisanAI = { postJSON, getJSON, renderMarkdown, setLoading, scrollToBottom, getCsrfToken };
