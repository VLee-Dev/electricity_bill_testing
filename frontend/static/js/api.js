const API_BASE = '/api/v1';

function token() {
  return localStorage.getItem('access_token');
}

function userType() {
  return localStorage.getItem('user_type');
}

async function api(path, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };

  if (token()) {
    headers.Authorization = `Bearer ${token()}`;
  }

  try {
    const response = await fetch(API_BASE + path, { ...options, headers });
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new Error(data.detail || data.message || 'Có lỗi xảy ra.');
    }

    return data;
  } catch (err) {
    if (err.message.includes('Failed to fetch')) {
      throw new Error('Không thể kết nối đến server. Vui lòng kiểm tra kết nối.');
    }
    throw err;
  }
}

function showError(error) {
  const errorEl = document.querySelector('[data-testid="error-message"]') || document.querySelector('#error-message');
  if (errorEl) {
    errorEl.textContent = error.message || error;
    errorEl.style.display = 'block';
  }
}

function saveAuth(accessToken, type) {
  localStorage.setItem('access_token', accessToken);
  localStorage.setItem('user_type', type);
}

function clearAuth() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user_type');
}

function requireAuth() {
  if (!token()) {
    // Không có token: chuyển về trang login phù hợp với user_type (nếu có),
    // mặc định về trang chủ.
    const type = userType();
    if (type === 'customer') {
      location.href = '/auth/customer_login.html';
    } else if (type === 'admin') {
      location.href = '/auth/admin_login.html';
    } else {
      location.href = '/';
    }
  }
}

function logout() {
  clearAuth();
  location.href = '/';
}

/* ============ Toast notifications (thay thế alert/confirm) ============ */
function getToastContainer() {
  let c = document.getElementById('toast-container');
  if (!c) {
    c = document.createElement('div');
    c.id = 'toast-container';
    c.className = 'toast-container';
    document.body.appendChild(c);
  }
  return c;
}

function showToast(type, title, message, duration = 3500) {
  const c = getToastContainer();
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.innerHTML = `
    ${title ? `<div class="toast-title">${escapeHtml(title)}</div>` : ''}
    ${message ? `<div class="toast-message">${escapeHtml(message)}</div>` : ''}
  `;
  c.appendChild(t);
  // animate in
  requestAnimationFrame(() => t.classList.add('show'));
  // auto dismiss
  setTimeout(() => {
    t.classList.remove('show');
    setTimeout(() => t.remove(), 300);
  }, duration);
}

function toastSuccess(title, message) { showToast('success', title, message); }
function toastError(title, message)   { showToast('error', title, message, 5000); }
function toastInfo(title, message)    { showToast('info', title, message); }

function escapeHtml(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

/* ============ Toast-based confirm (thay thế window.confirm) ============ */
function toastConfirm(title, message, okLabel = 'Xác nhận', cancelLabel = 'Hủy') {
  return new Promise(resolve => {
    const c = getToastContainer();
    const wrap = document.createElement('div');
    wrap.className = 'toast info';
    wrap.style.minWidth = '320px';
    wrap.innerHTML = `
      <div class="toast-title">${escapeHtml(title)}</div>
      <div class="toast-message">${escapeHtml(message)}</div>
      <div style="display:flex; gap:8px; margin-top:12px; justify-content:flex-end;">
        <button class="button secondary" data-act="cancel" style="padding:6px 14px; font-size:14px;">${escapeHtml(cancelLabel)}</button>
        <button class="button primary"   data-act="ok"     style="padding:6px 14px; font-size:14px;">${escapeHtml(okLabel)}</button>
      </div>
    `;
    c.appendChild(wrap);
    requestAnimationFrame(() => wrap.classList.add('show'));
    wrap.addEventListener('click', (e) => {
      const act = e.target.getAttribute('data-act');
      if (act === 'ok') resolve(true);
      if (act === 'cancel') resolve(false);
      wrap.classList.remove('show');
      setTimeout(() => wrap.remove(), 300);
    }, { once: true });
  });
}

/* ============ Toast-based prompt (thay thế window.prompt cho số) ============ */
function toastPromptNumber(title, currentValue, min = 0) {
  return new Promise(resolve => {
    const c = getToastContainer();
    const wrap = document.createElement('div');
    wrap.className = 'toast info';
    wrap.style.minWidth = '340px';
    wrap.innerHTML = `
      <div class="toast-title">${escapeHtml(title)}</div>
      <div class="toast-message" style="margin-top: 8px;">
        <input id="toast-prompt-input" type="number" min="${min}" value="${escapeHtml(currentValue)}"
               style="width:100%; padding:8px 10px; background:var(--page); border:1px solid var(--line); border-radius:6px; color:var(--ink);" />
      </div>
      <div style="display:flex; gap:8px; margin-top:12px; justify-content:flex-end;">
        <button class="button secondary" data-act="cancel" style="padding:6px 14px; font-size:14px;">Hủy</button>
        <button class="button primary"   data-act="ok"     style="padding:6px 14px; font-size:14px;">Lưu</button>
      </div>
    `;
    c.appendChild(wrap);
    requestAnimationFrame(() => wrap.classList.add('show'));

    const close = (val) => {
      wrap.classList.remove('show');
      setTimeout(() => wrap.remove(), 300);
      resolve(val);
    };

    wrap.addEventListener('click', (e) => {
      const act = e.target.getAttribute('data-act');
      if (act === 'cancel') return close(null);
      if (act === 'ok') {
        const inp = document.getElementById('toast-prompt-input');
        const v = parseInt(inp.value, 10);
        if (isNaN(v) || v < min) {
          toastError('Giá trị không hợp lệ', `Vui lòng nhập số ≥ ${min}`);
          return;
        }
        return close(v);
      }
    });

    // Enter để OK, Esc để cancel
    setTimeout(() => {
      const inp = document.getElementById('toast-prompt-input');
      if (!inp) return;
      inp.focus();
      inp.select();
      inp.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') { e.preventDefault(); wrap.querySelector('[data-act=ok]').click(); }
        if (e.key === 'Escape') { e.preventDefault(); wrap.querySelector('[data-act=cancel]').click(); }
      });
    }, 50);
  });
}
