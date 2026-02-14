// ── Schedule Management ─────────────────────────────────────

import { state, dom } from './state.js';
import {
  getSchedules,
  updateSchedule,
  getScheduledShutdowns,
  addScheduledShutdown,
  deleteScheduledShutdown,
} from './api.js';
import { showConfirm } from './modal.js';

const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

// ═══════════════════════════════════════════════════════════
//  WEEKLY SCHEDULE
// ═══════════════════════════════════════════════════════════
export async function loadSchedules() {
  try {
    const data = await getSchedules();
    renderSchedules(data.schedules);
  } catch {
    dom.schedBody.innerHTML =
      '<tr><td colspan="4" class="text-center">Error loading schedules</td></tr>';
  }
}

function renderSchedules(schedules) {
  dom.schedBody.innerHTML = '';

  schedules.forEach((s) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td class="fw-semibold">${DAYS[s.day_of_week]}</td>
      <td class="text-center">
        <div class="form-check form-switch d-flex justify-content-center mb-0">
          <input class="form-check-input" type="checkbox"
                 data-day="${s.day_of_week}" data-field="enabled"
                 ${s.enabled ? 'checked' : ''}>
        </div>
      </td>
      <td class="text-center">
        <input type="time" value="${s.start_time}"
               data-day="${s.day_of_week}" data-field="start">
      </td>
      <td class="text-center">
        <input type="time" value="${s.stop_time}"
               data-day="${s.day_of_week}" data-field="stop">
      </td>
    `;
    dom.schedBody.appendChild(tr);
  });

  dom.schedBody
    .querySelectorAll('input[type="checkbox"], input[type="time"]')
    .forEach((input) => input.addEventListener('change', handleScheduleChange));
}

async function handleScheduleChange(e) {
  const day  = parseInt(e.target.dataset.day);
  const row  = e.target.closest('tr');
  const data = {
    enabled:    row.querySelector('input[type="checkbox"]').checked,
    start_time: row.querySelector('input[data-field="start"]').value,
    stop_time:  row.querySelector('input[data-field="stop"]').value,
  };

  try {
    await updateSchedule(day, data);
    row.style.backgroundColor = 'rgba(166, 227, 161, 0.1)';
    setTimeout(() => (row.style.backgroundColor = ''), 800);
  } catch {
    alert('⚠ Failed to save schedule');
  }
}

// ═══════════════════════════════════════════════════════════
//  ONE-TIME SCHEDULED SHUTDOWN
// ═══════════════════════════════════════════════════════════
export async function loadScheduledShutdown() {
  try {
    const data = await getScheduledShutdowns();
    renderScheduledShutdown(data.shutdowns);
  } catch {
    dom.scheduledInfo.style.display = 'none';
  }
}

function renderScheduledShutdown(shutdowns) {
  if (!shutdowns || shutdowns.length === 0) {
    dom.scheduledInfo.style.display = 'none';
    dom.scheduledInfo.classList.remove('d-flex');
    return;
  }

  const s  = shutdowns[0];
  const dt = new Date(s.scheduled_at);

  dom.scheduledDateDisplay.textContent = dt.toLocaleString('en-US', {
    year: 'numeric', month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
  dom.scheduledInfo.style.display = 'flex';
  dom.scheduledInfo.classList.add('d-flex');
  dom.scheduleForm.style.display = 'block';

  dom.scheduleDate.value = dt.toISOString().split('T')[0];
  dom.scheduleTime.value = dt.toTimeString().substring(0, 5);

  dom.scheduledInfo.dataset.scheduleId  = s.id;
  dom.scheduledInfo.dataset.scheduleIso = s.scheduled_at;
}

export function initSchedule() {
  // ── Toggle schedule form ──
  dom.scheduleShutdownBtn.addEventListener('click', () => {
    const hasActive = dom.scheduledInfo.dataset.scheduleId;
    const isVisible = dom.scheduleForm.style.display !== 'none';

    if (hasActive) {
      dom.scheduleForm.style.display = 'block';
      const existing = new Date(dom.scheduledInfo.dataset.scheduleIso);
      dom.scheduleDate.value = existing.toISOString().split('T')[0];
      dom.scheduleTime.value = existing.toTimeString().substring(0, 5);
      dom.scheduleFeedback.textContent = '';
      return;
    }

    if (isVisible) {
      dom.scheduleForm.style.display = 'none';
    } else {
      dom.scheduleForm.style.display = 'block';
      const now = new Date();
      now.setMinutes(now.getMinutes() + state.lastScheduleOffset);
      dom.scheduleDate.value = now.toISOString().split('T')[0];
      dom.scheduleTime.value = now.toTimeString().substring(0, 5);
      dom.scheduleFeedback.textContent = '';
    }
  });

  // ── Confirm schedule ──
  dom.scheduleConfirmBtn.addEventListener('click', async () => {
    const date = dom.scheduleDate.value;
    const time = dom.scheduleTime.value;

    if (!date || !time) {
      dom.scheduleFeedback.className   = 'mt-2 small feedback-err';
      dom.scheduleFeedback.textContent = '⚠ Please select date and time';
      return;
    }

    const scheduledAt = `${date}T${time}:00`;
    const scheduled   = new Date(scheduledAt);
    state.lastScheduleOffset = Math.round((scheduled - new Date()) / 60000);

    try {
      const data = await addScheduledShutdown(scheduledAt);
      if (data.success) {
        dom.scheduleFeedback.className   = 'mt-2 small feedback-ok';
        dom.scheduleFeedback.textContent = '✓ ' + data.message;
        loadScheduledShutdown();
      } else {
        dom.scheduleFeedback.className   = 'mt-2 small feedback-err';
        dom.scheduleFeedback.textContent = '⚠ ' + data.message;
      }
    } catch {
      dom.scheduleFeedback.className   = 'mt-2 small feedback-err';
      dom.scheduleFeedback.textContent = '⚠ Network error';
    }
  });

  // ── Cancel schedule ──
  dom.cancelScheduleBtn.addEventListener('click', () => {
    const id = dom.scheduledInfo.dataset.scheduleId;
    if (!id) return;

    showConfirm('Cancel scheduled shutdown?', async () => {
      try {
        await deleteScheduledShutdown(id);
        loadScheduledShutdown();
      } catch {
        alert('⚠ Failed to cancel');
      }
    });
  });
}
