// ── Constants ───────────────────────────────────────────────
const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
const STATUS_POLL_MS = 5000; // poll every 5 seconds

// ── Local state ─────────────────────────────────────────────
let nasOnline      = null;   // true | false | null (unknown)
let actionPending  = false;
let lastMessage    = '';     // persist success message
let lastMessageType = '';    // 'ok' | 'err'
let lastScheduleOffset = 5;  // minutes offset for schedule, persisted

// ── DOM elements ────────────────────────────────────────────
const statusDot       = document.getElementById('status-indicator');
const statusText      = document.getElementById('status-text');
const powerBtn        = document.getElementById('power-btn');
const powerIcon       = document.getElementById('power-icon');
const powerLabel      = document.getElementById('power-label');
const feedback        = document.getElementById('action-feedback');
const schedBody       = document.getElementById('schedule-body');

const shutdownNowBtn     = document.getElementById('shutdown-now-btn');
const scheduleShutdownBtn = document.getElementById('schedule-shutdown-btn');
const scheduleForm       = document.getElementById('schedule-form');
const scheduleDate       = document.getElementById('schedule-date');
const scheduleTime       = document.getElementById('schedule-time');
const scheduleConfirmBtn = document.getElementById('schedule-confirm-btn');
const scheduleFeedback   = document.getElementById('schedule-feedback');
const scheduledList      = document.getElementById('scheduled-list');

// ═══════════════════════════════════════════════════════════
//  STATUS
// ═══════════════════════════════════════════════════════════
async function fetchStatus() {
  try {
    const res  = await fetch('/api/status');
    const data = await res.json();
    nasOnline = data.online;
  } catch {
    nasOnline = null;
  }
  renderStatus();
}

function renderStatus() {
  if (actionPending) {
    statusDot.className    = 'status-dot pending';
    statusText.textContent = 'Action in progress…';
    powerBtn.disabled = true;
    return;
  }

  if (nasOnline === null) {
    statusDot.className    = 'status-dot offline';
    statusText.textContent = 'Unknown state';
    powerBtn.disabled = true;
    return;
  }

  powerBtn.disabled = false;

  if (nasOnline) {
    statusDot.className    = 'status-dot online';
    statusText.textContent = 'NAS online';
    powerBtn.className     = 'btn btn-lg px-5 btn-stop';
    powerIcon.className    = 'bi bi-stop-fill';
    powerLabel.textContent = 'Stop';
  } else {
    statusDot.className    = 'status-dot offline';
    statusText.textContent = 'NAS offline';
    powerBtn.className     = 'btn btn-lg px-5 btn-start';
    powerIcon.className    = 'bi bi-play-fill';
    powerLabel.textContent = 'Start';
  }

  // Show persisted message if exists
  if (lastMessage) {
    feedback.className   = `mt-3 small feedback-${lastMessageType}`;
    feedback.textContent = lastMessage;
  }
}

// ═══════════════════════════════════════════════════════════
//  ACTIONS START / STOP
// ═══════════════════════════════════════════════════════════
powerBtn.addEventListener('click', async () => {
  const endpoint = nasOnline ? '/api/stop' : '/api/start';
  actionPending = true;
  renderStatus();
  feedback.textContent = '';
  lastMessage = '';

  try {
    const res  = await fetch(endpoint, { method: 'POST' });
    const data = await res.json();

    if (data.success) {
      lastMessageType = 'ok';
      lastMessage = data.message;
    } else {
      lastMessageType = 'err';
      lastMessage = '⚠ ' + data.message;
    }
  } catch (err) {
    lastMessageType = 'err';
    lastMessage = '⚠ Network error';
  }

  // Wait for NAS to start/stop before re-polling
  setTimeout(() => {
    actionPending = false;
    fetchStatus();
  }, 8000);
});

// ═══════════════════════════════════════════════════════════
//  SHUTDOWN NOW
// ═══════════════════════════════════════════════════════════
shutdownNowBtn.addEventListener('click', async () => {
  if (!confirm('Shutdown NAS now?')) return;
  
  shutdownNowBtn.disabled = true;
  try {
    const res  = await fetch('/api/stop', { method: 'POST' });
    const data = await res.json();
    
    alert(data.success ? data.message : '⚠ ' + data.message);
  } catch {
    alert('⚠ Network error');
  }
  shutdownNowBtn.disabled = false;
  fetchStatus();
});

// ═══════════════════════════════════════════════════════════
//  SCHEDULED SHUTDOWN
// ═══════════════════════════════════════════════════════════
scheduleShutdownBtn.addEventListener('click', () => {
  const isVisible = scheduleForm.style.display !== 'none';
  scheduleForm.style.display = isVisible ? 'none' : 'block';
  
  if (!isVisible) {
    // Set default to current date/time + offset
    const now = new Date();
    now.setMinutes(now.getMinutes() + lastScheduleOffset);
    
    const dateStr = now.toISOString().split('T')[0];
    const timeStr = now.toTimeString().substring(0, 5);
    
    scheduleDate.value = dateStr;
    scheduleTime.value = timeStr;
  }
});

scheduleConfirmBtn.addEventListener('click', async () => {
  const date = scheduleDate.value;
  const time = scheduleTime.value;
  
  if (!date || !time) {
    scheduleFeedback.className   = 'mt-2 small feedback-err';
    scheduleFeedback.textContent = '⚠ Please select date and time';
    return;
  }
  
  const scheduledAt = `${date}T${time}:00`;
  
  // Update last offset
  const now = new Date();
  const scheduled = new Date(scheduledAt);
  lastScheduleOffset = Math.round((scheduled - now) / 60000);
  
  try {
    const res = await fetch('/api/scheduled-shutdowns', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scheduled_at: scheduledAt }),
    });
    const data = await res.json();
    
    if (data.success) {
      scheduleFeedback.className   = 'mt-2 small feedback-ok';
      scheduleFeedback.textContent = '✓ ' + data.message;
      scheduleForm.style.display = 'none';
      loadScheduledShutdowns();
    } else {
      scheduleFeedback.className   = 'mt-2 small feedback-err';
      scheduleFeedback.textContent = '⚠ ' + data.message;
    }
  } catch {
    scheduleFeedback.className   = 'mt-2 small feedback-err';
    scheduleFeedback.textContent = '⚠ Network error';
  }
});

async function loadScheduledShutdowns() {
  try {
    const res  = await fetch('/api/scheduled-shutdowns');
    const data = await res.json();
    renderScheduledShutdowns(data.shutdowns);
  } catch {
    scheduledList.innerHTML = '<div class=\"small text-danger\">Error loading scheduled shutdowns</div>';
  }
}

function renderScheduledShutdowns(shutdowns) {
  if (!shutdowns || shutdowns.length === 0) {
    scheduledList.innerHTML = '';
    return;
  }
  
  scheduledList.innerHTML = '<div class=\"small text-muted mt-2 mb-1\">Scheduled shutdowns:</div>';
  
  shutdowns.forEach(s => {
    const dt = new Date(s.scheduled_at);
    const dateStr = dt.toLocaleString('en-US', {
      month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
    });
    
    const div = document.createElement('div');
    div.className = 'scheduled-item';
    div.innerHTML = `
      <span class=\"scheduled-item-time\"><i class=\"bi bi-clock\"></i> ${dateStr}</span>
      <button class=\"btn btn-sm btn-outline-danger\" onclick=\"deleteScheduledShutdown(${s.id})\">
        <i class=\"bi bi-trash\"></i>
      </button>
    `;
    scheduledList.appendChild(div);
  });
}

async function deleteScheduledShutdown(id) {
  try {
    await fetch(`/api/scheduled-shutdowns/${id}`, { method: 'DELETE' });
    loadScheduledShutdowns();
  } catch {
    alert('⚠ Failed to delete');
  }
}

// ═══════════════════════════════════════════════════════════
//  WEEKLY SCHEDULE (auto-save on change)
// ═══════════════════════════════════════════════════════════
async function loadSchedules() {
  try {
    const res  = await fetch('/api/schedules');
    const data = await res.json();
    renderSchedules(data.schedules);
  } catch {
    schedBody.innerHTML = '<tr><td colspan=\"4\" class=\"text-center\">Error loading schedules</td></tr>';
  }
}

function renderSchedules(schedules) {
  schedBody.innerHTML = '';

  schedules.forEach(s => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td class=\"fw-semibold\">${DAYS[s.day_of_week]}</td>
      <td class=\"text-center\">
        <div class=\"form-check form-switch d-flex justify-content-center mb-0\">
          <input class=\"form-check-input\" type=\"checkbox\"
                 data-day=\"${s.day_of_week}\" data-field=\"enabled\"
                 ${s.enabled ? 'checked' : ''}>
        </div>
      </td>
      <td class=\"text-center\">
        <input type=\"time\" value=\"${s.start_time}\"
               data-day=\"${s.day_of_week}\" data-field=\"start\">
      </td>
      <td class=\"text-center\">
        <input type=\"time\" value=\"${s.stop_time}\"
               data-day=\"${s.day_of_week}\" data-field=\"stop\">
      </td>
    `;
    schedBody.appendChild(tr);
  });

  // Attach auto-save listeners
  schedBody.querySelectorAll('input[type=\"checkbox\"], input[type=\"time\"]').forEach(input => {
    input.addEventListener('change', handleScheduleChange);
  });
}

async function handleScheduleChange(e) {
  const day = parseInt(e.target.dataset.day);
  const field = e.target.dataset.field;
  
  // Get current values for this day
  const row = e.target.closest('tr');
  const enabled = row.querySelector('input[type=\"checkbox\"]').checked;
  const start = row.querySelector('input[data-field=\"start\"]').value;
  const stop = row.querySelector('input[data-field=\"stop\"]').value;
  
  try {
    const res = await fetch(`/api/schedules/${day}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        enabled: enabled,
        start_time: start,
        stop_time: stop
      }),
    });
    
    if (res.ok) {
      // Visual feedback: flash the row
      row.style.backgroundColor = 'rgba(166, 227, 161, 0.1)';
      setTimeout(() => row.style.backgroundColor = '', 800);
    }
  } catch {
    alert('⚠ Failed to save schedule');
  }
}

// ═══════════════════════════════════════════════════════════
//  INIT
// ═══════════════════════════════════════════════════════════
fetchStatus();
loadSchedules();
loadScheduledShutdowns();
setInterval(fetchStatus, STATUS_POLL_MS);
