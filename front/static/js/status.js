// ── Status Polling & Timer ──────────────────────────────────

import { state, dom } from './state.js';
import { fetchNasStatus } from './api.js';

const STATUS_POLL_MS = 5000;
const ACTION_POLL_MS = 2000;
const ACTION_TIMEOUT = 180; // seconds

export async function fetchStatus() {
  const wasInProgress = state.actionInProgress;

  try {
    const data = await fetchNasStatus();
    state.nasOnline        = data.online;
    state.actionInProgress = data.action_in_progress;
    state.actionType       = data.action_type;
    state.actionElapsed    = data.action_elapsed || 0;

    if (state.actionInProgress && !state.actionStartTime) {
      state.actionStartTime = Date.now() - (state.actionElapsed * 1000);
    } else if (!state.actionInProgress) {
      state.actionStartTime = null;
      if (wasInProgress && !state.lastMessage) {
        state.lastMessageType = 'ok';
        state.lastMessage = state.actionType === 'start'
          ? '✓ NAS started successfully'
          : '✓ NAS stopped successfully';
      }
    }
  } catch {
    state.nasOnline        = null;
    state.actionInProgress = false;
    state.actionType       = null;
    state.actionElapsed    = 0;
    state.actionStartTime  = null;
  }

  renderStatus();
  adjustPollingRate();
}

export function adjustPollingRate() {
  if (state.statusPollInterval) clearInterval(state.statusPollInterval);
  if (state.timerUpdateInterval) {
    clearInterval(state.timerUpdateInterval);
    state.timerUpdateInterval = null;
  }

  const interval = state.actionInProgress ? ACTION_POLL_MS : STATUS_POLL_MS;
  state.statusPollInterval = setInterval(fetchStatus, interval);

  if (state.actionInProgress && state.actionStartTime) {
    state.timerUpdateInterval = setInterval(updateTimerDisplay, 1000);
  }
}

export function updateTimerDisplay() {
  if (!state.actionInProgress || !state.actionStartTime) return;

  const elapsed   = (Date.now() - state.actionStartTime) / 1000;
  const remaining = Math.max(0, Math.ceil(ACTION_TIMEOUT - elapsed));
  const timeStr   = formatTime(remaining);

  dom.statusText.textContent = state.actionType === 'start'
    ? `Starting NAS… (${timeStr})`
    : `Stopping NAS… (${timeStr})`;

  if (remaining === 0) fetchStatus();
}

export function renderStatus() {
  dom.startBtnContainer.style.display = 'none';
  dom.shutdownButtons.style.display   = 'none';

  if (state.actionInProgress) {
    let elapsed = state.actionElapsed;
    if (state.actionStartTime) elapsed = (Date.now() - state.actionStartTime) / 1000;

    const remaining = Math.max(0, Math.ceil(ACTION_TIMEOUT - elapsed));
    const timeStr   = formatTime(remaining);

    dom.statusDot.className = 'status-dot pending';

    if (state.actionType === 'start') {
      dom.statusText.textContent = `Starting NAS… (${timeStr})`;
      dom.startBtnContainer.style.display = 'block';
    } else {
      dom.statusText.textContent = `Stopping NAS… (${timeStr})`;
      dom.shutdownButtons.style.display = 'block';
    }
  } else if (state.nasOnline === null) {
    dom.statusDot.className    = 'status-dot offline';
    dom.statusText.textContent = 'Unknown state';
  } else if (state.nasOnline) {
    dom.statusDot.className    = 'status-dot online';
    dom.statusText.textContent = 'NAS online';
    dom.shutdownButtons.style.display = 'block';
  } else {
    dom.statusDot.className    = 'status-dot offline';
    dom.statusText.textContent = 'NAS offline';
    dom.startBtnContainer.style.display = 'block';
  }

  if (state.lastMessage && !state.actionInProgress) {
    dom.feedback.className   = `mt-3 small feedback-${state.lastMessageType}`;
    dom.feedback.textContent = state.lastMessage;
  } else if (state.actionInProgress) {
    dom.feedback.textContent = '';
  }
}

// ── Helpers ─────────────────────────────────────────────────
function formatTime(totalSeconds) {
  const m = Math.floor(totalSeconds / 60);
  const s = totalSeconds % 60;
  return `${m}:${s.toString().padStart(2, '0')}`;
}
