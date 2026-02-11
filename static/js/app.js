// ── Constants ───────────────────────────────────────────────
const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
const STATUS_POLL_MS = 5000; // poll every 5 seconds

// ── Local state ─────────────────────────────────────────────
let nasOnline        = null;   // true | false | null (unknown)
let actionInProgress = false;
let actionType       = null;   // 'start' | 'stop'
let lastMessage      = '';     // persist success message
let lastMessageType  = '';     // 'ok' | 'err'
let lastScheduleOffset = 5;    // minutes offset for schedule, persisted

// ── DOM elements ────────────────────────────────────────────
const statusDot       = document.getElementById('status-indicator');
const statusText      = document.getElementById('status-text');
const startBtnContainer = document.getElementById('start-button-container');
const startBtn        = document.getElementById('start-btn');
const shutdownButtons = document.getElementById('shutdown-buttons');
const feedback        = document.getElementById('action-feedback');
const schedBody       = document.getElementById('schedule-body');

const shutdownNowBtn      = document.getElementById('shutdown-now-btn');
const scheduleShutdownBtn = document.getElementById('schedule-shutdown-btn');
const scheduleForm        = document.getElementById('schedule-form');
const scheduleDate        = document.getElementById('schedule-date');
const scheduleTime        = document.getElementById('schedule-time');
const scheduleConfirmBtn  = document.getElementById('schedule-confirm-btn');
const scheduleFeedback    = document.getElementById('schedule-feedback');
const scheduledInfo       = document.getElementById('scheduled-info');
const scheduledDateDisplay = document.getElementById('scheduled-date-display');
const cancelScheduleBtn   = document.getElementById('cancel-schedule-btn');

// Modal elements
const confirmModal    = document.getElementById('confirm-modal');
const modalMessage    = document.getElementById('modal-message');
const modalConfirm    = document.getElementById('modal-confirm');
const modalCancel     = document.getElementById('modal-cancel');

let pendingConfirmAction = null; // Stores the action to execute on confirm

// ═══════════════════════════════════════════════════════════
//  CUSTOM CONFIRMATION MODAL
// ═══════════════════════════════════════════════════════════
function showConfirm(message, onConfirm) {
  modalMessage.textContent = message;
  confirmModal.style.display = 'flex';
  pendingConfirmAction = onConfirm;
}

function hideConfirm() {
  confirmModal.style.display = 'none';
  pendingConfirmAction = null;
}

modalConfirm.addEventListener('click', () => {
  if (pendingConfirmAction) {
    pendingConfirmAction();
  }
  hideConfirm();
});

modalCancel.addEventListener('click', hideConfirm);

// Close modal on outside click
confirmModal.addEventListener('click', (e) => {
  if (e.target === confirmModal) {
    hideConfirm();
  }
});

// ═══════════════════════════════════════════════════════════
//  STATUS
// ═══════════════════════════════════════════════════════════
async function fetchStatus() {
  try {
    const res  = await fetch('/api/status');
    const data = await res.json();
    nasOnline = data.online;
    actionInProgress = data.action_in_progress;
    actionType = data.action_type;
  } catch {
    nasOnline = null;
    actionInProgress = false;
    actionType = null;
  }
  renderStatus();
}

function renderStatus() {
  // Hide all buttons first
  startBtnContainer.style.display = 'none';
  shutdownButtons.style.display = 'none';
  
  if (actionInProgress) {
    statusDot.className    = 'status-dot pending';
    statusText.textContent = actionType === 'start' ? 'Starting NAS…' : 'Stopping NAS…';
    // Don't show any buttons during action
  } else if (nasOnline === null) {
    statusDot.className    = 'status-dot offline';
    statusText.textContent = 'Unknown state';
    // Don't show any buttons
  } else if (nasOnline) {
    statusDot.className    = 'status-dot online';
    statusText.textContent = 'NAS online';
    shutdownButtons.style.display = 'block';
  } else {
    statusDot.className    = 'status-dot offline';
    statusText.textContent = 'NAS offline';
    startBtnContainer.style.display = 'block';
  }

  // Show persisted message if exists
  if (lastMessage && !actionInProgress) {
    feedback.className   = `mt-3 small feedback-${lastMessageType}`;
    feedback.textContent = lastMessage;
  } else if (actionInProgress) {
    feedback.textContent = '';
  }
}

// ═══════════════════════════════════════════════════════════
//  START ACTION
// ═══════════════════════════════════════════════════════════
startBtn.addEventListener('click', async () => {
  feedback.textContent = '';
  lastMessage = '';

  try {
    const res  = await fetch('/api/start', { method: 'POST' });
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

  // Immediately fetch status to show "action in progress"
  fetchStatus();
});

// ═══════════════════════════════════════════════════════════
//  SHUTDOWN NOW
// ═══════════════════════════════════════════════════════════
shutdownNowBtn.addEventListener('click', () => {
  showConfirm('Shutdown NAS now?', async () => {
    feedback.textContent = '';
    lastMessage = '';

    try {
      const res  = await fetch('/api/stop', { method: 'POST' });
      const data = await res.json();
      
      if (data.success) {
        lastMessageType = 'ok';
        lastMessage = data.message;
      } else {
        lastMessageType = 'err';
        lastMessage = '⚠ ' + data.message;
      }
    } catch {
      lastMessageType = 'err';
      lastMessage = '⚠ Network error';
    }

    // Immediately fetch status to show "action in progress"
    fetchStatus();
  });
});

// ═══════════════════════════════════════════════════════════
//  SCHEDULED SHUTDOWN
// ═══════════════════════════════════════════════════════════
scheduleShutdownBtn.addEventListener('click', () => {
  const isVisible = scheduleForm.style.display !== 'none';
  
  if (isVisible) meoit{
    // hide form, show scheduled info if exists
    scheduleform.style.display = 'none';
    loadscheduledshutdown();
  } else {
    // show form
    scheduleform.style.display = 'block';
    scheduledinfo.style.display = 'none';
    
    // if there's an existing schedule, use its time; otherwise use offset
    if (scheduledinfo.dataset.scheduleiso) {
      const existingdt = new date(scheduledinfo.dataset.scheduleiso);
      scheduledate.value = existingdt.toisostring().split('t')[0];
      scheduletime.value = existingdt.totimestring().substring(0, 5);
    } else {
      // default to current time + offset
      const now = new date();
      now.setminutes(now.getminutes() + lastscheduleoffset);
      scheduledate.value = now.toisostring().split('t')[0];
      scheduletime.value = now.totimestring().substring(0, 5);
    }
    
    schedulefeedback.textcontent = '';
  }
});

scheduleconfirmbtn.addeventlistener('click', async () => {
  const date = scheduledate.value;
  const time = scheduletime.value;
  
  if (!date || !time) {
    schedulefeedback.classname   = 'mt-2 small feedback-err';
    schedulefeedback.textcontent = '⚠ please select date and time';
    return;
  }
  
  const scheduledat = `${date}t${time}:00`;
  
  // update last offset
  const now = new date();
  const scheduled = new date(scheduledat);
  lastscheduleoffset = math.round((scheduled - now) / 60000);
  
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
      loadScheduledShutdown();
    } else {
      scheduleFeedback.className   = 'mt-2 small feedback-err';
      scheduleFeedback.textContent = '⚠ ' + data.message;
    }
  } catch {
    scheduleFeedback.className   = 'mt-2 small feedback-err';
    scheduleFeedback.textContent = '⚠ Network error';
  }
});

async function loadScheduledShutdown() {
  try {
    const res  = await fetch('/api/scheduled-shutdowns');
    const data = await res.json();
    renderScheduledShutdown(data.shutdowns);
  } catch {
    scheduledInfo.style.display = 'none';
  }
}

function renderScheduledShutdown(shutdowns) {
  if (!shutdowns || shutdowns.length === 0) {
    scheduledInfo.style.display = 'none';
    return;
  }
  
  // Display the first (and only) scheduled shutdown
  const s = shutdowns[0];
  const dt = new Date(s.scheduled_at);
  const dateStr = dt.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
  
  scheduledDateDisplay.textContent = dateStr;
  scheduledInfo.style.display = 'block';
  scheduleForm.style.display = 'none'; // Hide form when schedule is active
  
  // Store ID and ISO date for cancellation/editing
  scheduledInfo.dataset.scheduleId = s.id;
  scheduledInfo.dataset.scheduleIso = s.scheduled_at;
}

cancelScheduleBtn.addEventListener('click', () => {
  const scheduleId = scheduledInfo.dataset.scheduleId;
  if (!scheduleId) return;
  
  showConfirm('Cancel scheduled shutdown?', async () => {
    try {
      await fetch(`/api/scheduled-shutdowns/${scheduleId}`, { method: 'DELETE' });
      loadScheduledShutdown();
    } catch {
      alert('⚠ Failed to cancel');
    }
  });
});

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
loadScheduledShutdown();
setInterval(fetchStatus, STATUS_POLL_MS);
setInterval(loadScheduledShutdown, 10000); // Refresh schedule every 10s
