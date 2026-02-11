// ── Constantes ──────────────────────────────────────────────
const DAYS = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'];
const STATUS_POLL_MS = 5000; // poll toutes les 5 s

// ── État local ──────────────────────────────────────────────
let nasOnline   = null;   // true | false | null (inconnu)
let actionPending = false;

// ── Éléments DOM ────────────────────────────────────────────
const statusDot   = document.getElementById('status-indicator');
const statusText  = document.getElementById('status-text');
const powerBtn    = document.getElementById('power-btn');
const powerIcon   = document.getElementById('power-icon');
const powerLabel  = document.getElementById('power-label');
const feedback    = document.getElementById('action-feedback');
const schedBody   = document.getElementById('schedule-body');

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
    statusDot.className  = 'status-dot pending';
    statusText.textContent = 'Action en cours…';
    powerBtn.disabled = true;
    return;
  }

  if (nasOnline === null) {
    statusDot.className  = 'status-dot offline';
    statusText.textContent = 'État inconnu';
    powerBtn.disabled = true;
    return;
  }

  powerBtn.disabled = false;

  if (nasOnline) {
    statusDot.className    = 'status-dot online';
    statusText.textContent = 'NAS en ligne';
    powerBtn.className     = 'btn btn-lg px-5 btn-stop';
    powerIcon.className    = 'bi bi-stop-fill';
    powerLabel.textContent = 'Éteindre';
  } else {
    statusDot.className    = 'status-dot offline';
    statusText.textContent = 'NAS hors-ligne';
    powerBtn.className     = 'btn btn-lg px-5 btn-start';
    powerIcon.className    = 'bi bi-play-fill';
    powerLabel.textContent = 'Démarrer';
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

  try {
    const res  = await fetch(endpoint, { method: 'POST' });
    const data = await res.json();

    if (data.success) {
      feedback.className   = 'mt-3 small feedback-ok';
      feedback.textContent = data.message;
    } else {
      feedback.className   = 'mt-3 small feedback-err';
      feedback.textContent = '⚠ ' + data.message;
    }
  } catch (err) {
    feedback.className   = 'mt-3 small feedback-err';
    feedback.textContent = '⚠ Erreur réseau';
  }

  // Laisser le temps au NAS de démarrer/s'éteindre avant de re-poll
  setTimeout(() => {
    actionPending = false;
    fetchStatus();
  }, 8000);
});

// ═══════════════════════════════════════════════════════════
//  PLANIFICATION
// ═══════════════════════════════════════════════════════════
async function loadSchedules() {
  try {
    const res  = await fetch('/api/schedules');
    const data = await res.json();
    renderSchedules(data.schedules);
  } catch {
    schedBody.innerHTML = '<tr><td colspan="5" class="text-center">Erreur de chargement</td></tr>';
  }
}

function renderSchedules(schedules) {
  schedBody.innerHTML = '';

  schedules.forEach(s => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td class="fw-semibold">${DAYS[s.day_of_week]}</td>
      <td class="text-center">
        <div class="form-check form-switch d-flex justify-content-center mb-0">
          <input class="form-check-input" type="checkbox"
                 id="en-${s.day_of_week}" ${s.enabled ? 'checked' : ''}>
        </div>
      </td>
      <td class="text-center">
        <input type="time" id="start-${s.day_of_week}" value="${s.start_time}">
      </td>
      <td class="text-center">
        <input type="time" id="stop-${s.day_of_week}" value="${s.stop_time}">
      </td>
      <td class="text-center">
        <button class="btn btn-outline-light btn-save-day"
                onclick="saveDay(${s.day_of_week})" title="Sauver">
          <i class="bi bi-check-lg"></i>
        </button>
      </td>
    `;
    schedBody.appendChild(tr);
  });
}

async function saveDay(day) {
  const enabled    = document.getElementById(`en-${day}`).checked;
  const start_time = document.getElementById(`start-${day}`).value;
  const stop_time  = document.getElementById(`stop-${day}`).value;

  try {
    const res = await fetch(`/api/schedules/${day}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enabled, start_time, stop_time }),
    });
    const data = await res.json();

    // Flash row
    const btn = document.querySelector(`#schedule-body tr:nth-child(${day + 1}) .btn-save-day`);
    if (data.success) {
      btn.classList.replace('btn-outline-light', 'btn-success');
      setTimeout(() => btn.classList.replace('btn-success', 'btn-outline-light'), 1200);
    } else {
      btn.classList.replace('btn-outline-light', 'btn-danger');
      setTimeout(() => btn.classList.replace('btn-danger', 'btn-outline-light'), 1200);
    }
  } catch {
    alert('Erreur réseau');
  }
}

// ═══════════════════════════════════════════════════════════
//  INIT
// ═══════════════════════════════════════════════════════════
fetchStatus();
loadSchedules();
setInterval(fetchStatus, STATUS_POLL_MS);
