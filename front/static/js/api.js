// ── API Routes ──────────────────────────────────────────────
// Encapsulated API calls for NAS Control

const API = {
  status:             '/api/status',
  start:              '/api/start',
  stop:               '/api/stop',
  clearAction:        '/api/clear-action',
  schedules:          '/api/schedules',
  scheduledShutdowns: '/api/scheduled-shutdowns',
};

export async function fetchNasStatus() {
  const res = await fetch(API.status);
  return res.json();
}

export async function startNas() {
  const res = await fetch(API.start, { method: 'POST' });
  return res.json();
}

export async function stopNas() {
  const res = await fetch(API.stop, { method: 'POST' });
  return res.json();
}

export async function clearAction() {
  const res = await fetch(API.clearAction, { method: 'POST' });
  return res.json();
}

export async function getSchedules() {
  const res = await fetch(API.schedules);
  return res.json();
}

export async function updateSchedule(day, data) {
  const res = await fetch(`${API.schedules}/${day}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function getScheduledShutdowns() {
  const res = await fetch(API.scheduledShutdowns);
  return res.json();
}

export async function addScheduledShutdown(scheduledAt) {
  const res = await fetch(API.scheduledShutdowns, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scheduled_at: scheduledAt }),
  });
  return res.json();
}

export async function deleteScheduledShutdown(id) {
  const res = await fetch(`${API.scheduledShutdowns}/${id}`, { method: 'DELETE' });
  return res.json();
}
