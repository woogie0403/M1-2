/**
 * K-BoxOffice AI Assistant Frontend Application
 * - 100% Vanilla JavaScript (No Frameworks)
 * - REST API Integration with FastAPI Backend
 */

// 1. API Base URL 동적 감지 (로컬 localhost:8000 기본 지원)
const API_BASE_URL = window.API_BASE_URL ||
  (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : 'https://k-boxoffice-backend.onrender.com'); // 배포 시 기본 백엔드 주소

// 전역 상태 관리
let currentConversationId = null;
let boxofficeChartInstance = null;

// DOM 요소 참조
const serverStatusBadge = document.getElementById('serverStatusBadge');
const serverStatusText = document.getElementById('serverStatusText');
const summaryPeriod = document.getElementById('summaryPeriod');
const summaryCount = document.getElementById('summaryCount');
const summaryTotal = document.getElementById('summaryTotal');
const summaryAvg = document.getElementById('summaryAvg');
const summaryMinMax = document.getElementById('summaryMinMax');
const summaryTrend = document.getElementById('summaryTrend');

const chatMessages = document.getElementById('chatMessages');
const chatForm = document.getElementById('chatForm');
const chatInput = document.getElementById('chatInput');
const loadingIndicator = document.getElementById('loadingIndicator');
const newChatBtn = document.getElementById('newChatBtn');
const conversationList = document.getElementById('conversationList');

const dataTableBody = document.getElementById('dataTableBody');
const addDataForm = document.getElementById('addDataForm');
const inputDate = document.getElementById('inputDate');
const inputValue = document.getElementById('inputValue');
const inputMemo = document.getElementById('inputMemo');

const editModal = document.getElementById('editModal');
const editDataForm = document.getElementById('editDataForm');
const editId = document.getElementById('editId');
const editDate = document.getElementById('editDate');
const editValue = document.getElementById('editValue');
const editMemo = document.getElementById('editMemo');
const closeModalBtn = document.getElementById('closeModalBtn');
const cancelEditBtn = document.getElementById('cancelEditBtn');

const exportCsvBtn = document.getElementById('exportCsvBtn');
const themeToggleBtn = document.getElementById('themeToggleBtn');

// ==========================================================
// 1. 초기화 및 서버 헬스체크
// ==========================================================
document.addEventListener('DOMContentLoaded', async () => {
  initTheme();
  initTabs();
  initQuickPrompts();
  await checkServerHealth();
  await loadSummary();
  await loadConversations();
  await loadDataTable();
});

async function checkServerHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/`);
    if (res.ok) {
      serverStatusBadge.className = 'status-badge online';
      serverStatusText.textContent = '백엔드 정상 연결됨';
    } else {
      throw new Error(`HTTP ${res.status}`);
    }
  } catch (err) {
    serverStatusBadge.className = 'status-badge error';
    serverStatusText.textContent = '서버 깨우는 중 (슬립/콜드스타트)...';
    // 5초 후 재시도 (Render 슬립 대응 UX)
    setTimeout(checkServerHealth, 5000);
  }
}

// ==========================================================
// 2. 데이터 요약 (Summary Cards)
// ==========================================================
async function loadSummary() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/data/summary`);
    if (!res.ok) throw new Error('요약 로드 실패');
    const data = await res.json();

    summaryPeriod.textContent = data.period || '기간 미상';
    summaryCount.textContent = `${Number(data.count).toLocaleString()}건의 일별 데이터`;

    const metrics = data.metrics || {};
    summaryTotal.textContent = `${Number(metrics.total || 0).toLocaleString()}명`;
    summaryAvg.textContent = `${Number(metrics.average || 0).toLocaleString()}명`;
    summaryMinMax.textContent = `최고: ${Number(metrics.max || 0).toLocaleString()}명 / 최저: ${Number(metrics.min || 0).toLocaleString()}명`;
    summaryTrend.textContent = data.trend || '분석 중';
  } catch (err) {
    console.error('요약 조회 에러:', err);
  }
}

// ==========================================================
// 3. AI 채팅 인터페이스
// ==========================================================
chatForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const message = chatInput.value.trim();
  if (!message) return;

  // 사용자 메시지 화면 추가
  appendMessage('user', message);
  chatInput.value = '';
  loadingIndicator.classList.remove('hidden');
  scrollToBottom();

  try {
    const res = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: message,
        conversation_id: currentConversationId
      })
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    // AI 답변 화면 추가
    appendMessage('assistant', data.response);
    currentConversationId = data.conversation_id;

    // 대화 목록 및 요약 갱신
    await loadConversations();
  } catch (err) {
    appendMessage('assistant', `⚠️ 죄송합니다. 응답 생성 중 오류가 발생했습니다: ${err.message}`);
  } finally {
    loadingIndicator.classList.add('hidden');
    scrollToBottom();
  }
});

function appendMessage(role, text) {
  const msgDiv = document.createElement('div');
  msgDiv.className = `message ${role === 'user' ? 'user-message' : 'bot-message'}`;

  const avatar = role === 'user' ? '👤' : '🤖';
  const author = role === 'user' ? '사용자' : 'K-BoxOffice AI';

  msgDiv.innerHTML = `
    <div class="message-avatar">${avatar}</div>
    <div class="message-body">
      <div class="message-author">${author}</div>
      <div class="message-text">${escapeHtml(text)}</div>
    </div>
  `;
  chatMessages.appendChild(msgDiv);
}

function scrollToBottom() {
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function initQuickPrompts() {
  document.querySelectorAll('.prompt-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const q = chip.getAttribute('data-question');
      chatInput.value = q;
      chatForm.dispatchEvent(new Event('submit'));
    });
  });
}

// 새 대화 시작
newChatBtn.addEventListener('click', () => {
  currentConversationId = null;
  chatMessages.innerHTML = `
    <div class="message bot-message">
      <div class="message-avatar">🤖</div>
      <div class="message-body">
        <div class="message-author">K-BoxOffice AI</div>
        <div class="message-text">
          새 대화를 시작합니다! 2024~2025 박스오피스 실적 데이터에 대해 무엇이든 질문해 주세요.
        </div>
      </div>
    </div>
  `;
  document.querySelectorAll('.conversation-item').forEach(el => el.classList.remove('active'));
});

// ==========================================================
// 4. 대화 기록 (Conversations) 관리
// ==========================================================
async function loadConversations() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/conversations`);
    if (!res.ok) throw new Error('대화 목록 로드 실패');
    const convs = await res.json();

    conversationList.innerHTML = '';
    if (convs.length === 0) {
      conversationList.innerHTML = '<li class="empty-state">저장된 대화가 없습니다.</li>';
      return;
    }

    convs.forEach(conv => {
      const li = document.createElement('li');
      li.className = `conversation-item ${conv.id === currentConversationId ? 'active' : ''}`;
      li.innerHTML = `
        <div class="conv-info">
          <div class="conv-title">${escapeHtml(conv.title || '새 대화')}</div>
          <div class="conv-date">${formatDate(conv.updated_at)}</div>
        </div>
        <button class="conv-delete-btn" title="대화 삭제" data-id="${conv.id}">&times;</button>
      `;

      // 클릭 시 대화 불러오기 (과제 요구사항: 불러오기 UX)
      li.addEventListener('click', (e) => {
        if (e.target.classList.contains('conv-delete-btn')) return;
        loadConversationDetail(conv.id);
      });

      // 삭제 버튼
      li.querySelector('.conv-delete-btn').addEventListener('click', async (e) => {
        e.stopPropagation();
        if (confirm('이 대화 기록을 삭제하시겠습니까?')) {
          await deleteConversation(conv.id);
        }
      });

      conversationList.appendChild(li);
    });
  } catch (err) {
    conversationList.innerHTML = '<li class="empty-state">대화 목록 로드 오류</li>';
  }
}

async function loadConversationDetail(convId) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/conversations/${convId}`);
    if (!res.ok) throw new Error('대화 상세 로드 실패');
    const conv = await res.json();

    currentConversationId = conv.id;
    chatMessages.innerHTML = '';

    const messages = conv.messages || [];
    if (messages.length === 0) {
      appendMessage('assistant', '이 대화에는 기록된 메시지가 없습니다.');
    } else {
      messages.forEach(m => appendMessage(m.role, m.content));
    }

    scrollToBottom();
    await loadConversations();
  } catch (err) {
    alert('대화를 불러오지 못했습니다: ' + err.message);
  }
}

async function deleteConversation(convId) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/conversations/${convId}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('대화 삭제 실패');
    if (currentConversationId === convId) {
      newChatBtn.click();
    }
    await loadConversations();
  } catch (err) {
    alert('대화 삭제 실패: ' + err.message);
  }
}

// ==========================================================
// 5. 데이터 관리 (CRUD)
// ==========================================================
async function loadDataTable() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/data?limit=50`);
    if (!res.ok) throw new Error('데이터 목록 로드 실패');
    const items = await res.json();

    dataTableBody.innerHTML = '';
    if (items.length === 0) {
      dataTableBody.innerHTML = '<tr><td colspan="4" class="text-center">등록된 데이터가 없습니다.</td></tr>';
      return;
    }

    items.forEach(item => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td><strong>${item.date}</strong></td>
        <td>${Number(item.value).toLocaleString()}</td>
        <td>${escapeHtml(item.memo || '-')}</td>
        <td>
          <div class="action-btns">
            <button class="btn-table btn-edit" data-id="${item.id}" data-date="${item.date}" data-value="${item.value}" data-memo="${escapeHtml(item.memo || '')}">수정</button>
            <button class="btn-table danger btn-delete" data-id="${item.id}">삭제</button>
          </div>
        </td>
      `;

      // 수정 버튼
      tr.querySelector('.btn-edit').addEventListener('click', (e) => {
        const btn = e.currentTarget;
        openEditModal(btn.dataset.id, btn.dataset.date, btn.dataset.value, btn.dataset.memo);
      });

      // 삭제 버튼
      tr.querySelector('.btn-delete').addEventListener('click', async (e) => {
        const id = e.currentTarget.dataset.id;
        if (confirm(`${item.date} 데이터를 삭제하시겠습니까?`)) {
          await deleteData(id);
        }
      });

      dataTableBody.appendChild(tr);
    });

    // 차트 데이터 갱신
    renderChart(items);
  } catch (err) {
    dataTableBody.innerHTML = '<tr><td colspan="4" class="text-center">데이터 로드 오류</td></tr>';
  }
}

// 새 데이터 추가
addDataForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const dateVal = inputDate.value;
  const numVal = parseFloat(inputValue.value);
  const memoVal = inputMemo.value.trim();

  try {
    const res = await fetch(`${API_BASE_URL}/api/data`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ date: dateVal, value: numVal, memo: memoVal })
    });

    if (!res.ok) throw new Error('데이터 추가 실패');
    inputDate.value = '';
    inputValue.value = '';
    inputMemo.value = '';

    alert('새 데이터가 추가되었습니다.');
    await loadSummary();
    await loadDataTable();
  } catch (err) {
    alert('데이터 추가 실패: ' + err.message);
  }
});

// 데이터 수정 모달
function openEditModal(id, date, value, memo) {
  editId.value = id;
  editDate.value = date;
  editValue.value = value;
  editMemo.value = memo;
  editModal.classList.remove('hidden');
}

function closeEditModal() {
  editModal.classList.add('hidden');
}

closeModalBtn.addEventListener('click', closeEditModal);
cancelEditBtn.addEventListener('click', closeEditModal);

editDataForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const id = editId.value;
  const dateVal = editDate.value;
  const numVal = parseFloat(editValue.value);
  const memoVal = editMemo.value.trim();

  try {
    const res = await fetch(`${API_BASE_URL}/api/data/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ date: dateVal, value: numVal, memo: memoVal })
    });

    if (!res.ok) throw new Error('데이터 수정 실패');
    closeEditModal();
    alert('데이터가 수정되었습니다.');
    await loadSummary();
    await loadDataTable();
  } catch (err) {
    alert('데이터 수정 실패: ' + err.message);
  }
});

async function deleteData(id) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/data/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('데이터 삭제 실패');
    alert('데이터가 삭제되었습니다.');
    await loadSummary();
    await loadDataTable();
  } catch (err) {
    alert('데이터 삭제 실패: ' + err.message);
  }
}

// ==========================================================
// 6. 보너스 기능: 시각화 차트 (Chart.js)
// ==========================================================
function renderChart(items) {
  const ctx = document.getElementById('boxofficeChart');
  if (!ctx || typeof Chart === 'undefined') return;

  // 최근 30개 데이터 역순 정렬
  const displayItems = [...items].slice(0, 30);
  const labels = displayItems.map(d => d.date);
  const values = displayItems.map(d => d.value);

  if (boxofficeChartInstance) {
    boxofficeChartInstance.destroy();
  }

  boxofficeChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: '일일 관객수(명)',
        data: values,
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.3,
        fill: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: {
          ticks: {
            callback: (val) => `${(val / 10000).toFixed(0)}만`
          }
        }
      }
    }
  });
}

// ==========================================================
// 7. 보너스 기능: CSV 내보내기 & 다크 모드
// ==========================================================
exportCsvBtn.addEventListener('click', async () => {
  try {
    const res = await fetch(`${API_BASE_URL}/api/data`);
    const data = await res.json();

    let csvContent = "data:text/csv;charset=utf-8,\uFEFF";
    csvContent += "날짜(date),관객수(value),1위영화/메모(memo)\n";
    data.forEach(row => {
      csvContent += `${row.date},${row.value},"${(row.memo || '').replace(/"/g, '""')}"\n`;
    });

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `k_boxoffice_data_${new Date().toISOString().slice(0,10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } catch (err) {
    alert('CSV 내보내기 실패: ' + err.message);
  }
});

function initTheme() {
  const saved = localStorage.getItem('theme');
  if (saved === 'dark') {
    document.body.classList.add('dark-mode');
    themeToggleBtn.textContent = '☀️';
  }
}

themeToggleBtn.addEventListener('click', () => {
  const isDark = document.body.classList.toggle('dark-mode');
  themeToggleBtn.textContent = isDark ? '☀️' : '🌙';
  localStorage.setItem('theme', isDark ? 'dark' : 'light');
});

function initTabs() {
  const tabBtns = document.querySelectorAll('.tab-btn');
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

      btn.classList.add('active');
      const targetId = btn.id.replace('Btn', '');
      const targetContent = document.getElementById(targetId);
      if (targetContent) targetContent.classList.add('active');
    });
  });
}

// 유틸리티
function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/[&<>'"]/g, tag => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    "'": '&#39;',
    '"': '&quot;'
  }[tag] || tag));
}

function formatDate(isoStr) {
  if (!isoStr) return '';
  try {
    const d = new Date(isoStr);
    return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
  } catch {
    return isoStr;
  }
}
