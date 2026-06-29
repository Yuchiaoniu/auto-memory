/* ===== Data Loading ===== */

const DATA_BASE = '../data/';
const DATA_CACHE = {};

async function loadData(filename) {
  if (DATA_CACHE[filename]) return DATA_CACHE[filename];
  const res = await fetch(DATA_BASE + filename);
  if (!res.ok) throw new Error(`Failed to load ${filename}`);
  const data = await res.json();
  DATA_CACHE[filename] = data;
  return data;
}

/* ===== URL Params ===== */

function getParam(key) {
  return new URLSearchParams(window.location.search).get(key);
}

/* ===== Popup / Modal ===== */

let popupOverlay = null;

function initPopup() {
  popupOverlay = document.getElementById('popup-overlay');
  if (!popupOverlay) {
    popupOverlay = document.createElement('div');
    popupOverlay.id = 'popup-overlay';
    popupOverlay.className = 'popup-overlay';
    popupOverlay.innerHTML = `
      <div class="popup-box">
        <div class="popup-word" id="popup-word"></div>
        <div class="popup-phonetic" id="popup-phonetic"></div>
        <div class="popup-meaning" id="popup-meaning"></div>
        <span class="popup-close" id="popup-close">關閉 ✕</span>
      </div>
    `;
    document.body.appendChild(popupOverlay);
  }
  popupOverlay.addEventListener('click', (e) => {
    if (e.target === popupOverlay || e.target.id === 'popup-close') closePopup();
  });
}

function openPopup({ word, phonetic, meaning }) {
  if (!popupOverlay) initPopup();
  document.getElementById('popup-word').textContent = word;
  document.getElementById('popup-phonetic').textContent = phonetic || '';
  document.getElementById('popup-meaning').textContent = meaning;
  popupOverlay.classList.add('active');
  document.body.style.overflow = 'hidden';
}

function closePopup() {
  if (popupOverlay) popupOverlay.classList.remove('active');
  document.body.style.overflow = '';
}

/* ===== Vocabulary Highlight ===== */

function applyVocabHighlight(container, vocabulary, paragraphIndex) {
  if (!vocabulary || !vocabulary.length) return;
  const relevant = vocabulary.filter(v =>
    paragraphIndex === undefined || v.paragraph_index === paragraphIndex
  );
  let html = container.innerHTML;
  relevant.forEach(v => {
    const escaped = v.word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(escaped, 'g');
    html = html.replace(regex, `<span class="vocab-word" data-word="${v.word}" data-phonetic="${v.phonetic || ''}" data-meaning="${v.meaning}">${v.word}</span>`);
  });
  container.innerHTML = html;
  container.querySelectorAll('.vocab-word').forEach(el => {
    el.addEventListener('click', () => {
      openPopup({
        word: el.dataset.word,
        phonetic: el.dataset.phonetic,
        meaning: el.dataset.meaning
      });
    });
  });
}

/* ===== Grade Filter ===== */

function initGradeTabs(tabsContainer, onFilter) {
  const tabs = tabsContainer.querySelectorAll('.grade-tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const grade = tab.dataset.grade;
      onFilter(grade === 'all' ? null : parseInt(grade));
    });
  });
}

/* ===== Module Tabs ===== */

function initModuleTabs(tabsContainer, panels) {
  const tabs = tabsContainer.querySelectorAll('.module-tab');
  tabs.forEach((tab, i) => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      panels.forEach((p, j) => {
        p.style.display = i === j ? 'block' : 'none';
      });
    });
  });
  if (tabs.length > 0) {
    tabs[0].classList.add('active');
    panels.forEach((p, j) => { p.style.display = j === 0 ? 'block' : 'none'; });
  }
}

/* ===== Accordion ===== */

function initAccordion(container) {
  container.querySelectorAll('.accordion-header').forEach(header => {
    header.addEventListener('click', () => {
      const body = header.nextElementSibling;
      const isOpen = header.classList.contains('open');
      header.classList.toggle('open', !isOpen);
      body.classList.toggle('open', !isOpen);
    });
  });
}

/* ===== Local Storage ===== */

function saveToStorage(key, value) {
  try { localStorage.setItem(key, JSON.stringify(value)); } catch(e) {}
}

function loadFromStorage(key, defaultValue = null) {
  try {
    const v = localStorage.getItem(key);
    return v !== null ? JSON.parse(v) : defaultValue;
  } catch(e) { return defaultValue; }
}

/* ===== Render Helpers ===== */

function createBadge(text, color = 'blue') {
  return `<span class="badge badge-${color}">${text}</span>`;
}

function gradeLabel(grade) {
  const labels = { 7: '七年級', 8: '八年級', 9: '九年級' };
  return labels[grade] || `${grade}年級`;
}

function genreColor(genre) {
  const colors = {
    '記敘文': 'blue',
    '說明文': 'green',
    '議論文': 'red',
    '詩詞': 'purple',
    '古文': 'gold'
  };
  return colors[genre] || 'gray';
}

/* ===== Toast Notification ===== */

function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  const colors = { info: '#1e40af', success: '#16a34a', error: '#dc2626' };
  toast.style.cssText = `
    position:fixed; bottom:1.5rem; right:1.5rem; z-index:9999;
    background:${colors[type]||colors.info}; color:white;
    padding:0.75rem 1.25rem; border-radius:8px;
    font-size:0.9rem; font-family:inherit;
    box-shadow:0 4px 16px rgba(0,0,0,0.2);
    opacity:0; transition:opacity 0.3s;
    max-width:300px;
  `;
  toast.textContent = message;
  document.body.appendChild(toast);
  requestAnimationFrame(() => { toast.style.opacity = '1'; });
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 2500);
}

/* ===== Error State ===== */

function showError(container, message = '資料載入失敗，請重新整理頁面') {
  container.innerHTML = `
    <div class="empty-state">
      <div class="empty-state-icon">⚠️</div>
      <p>${message}</p>
    </div>
  `;
}

/* ===== Init ===== */

document.addEventListener('DOMContentLoaded', () => {
  initPopup();
});
