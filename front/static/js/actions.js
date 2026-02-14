// ── Start / Shutdown Actions ────────────────────────────────

import { state, dom } from './state.js';
import { startNas, stopNas } from './api.js';
import { showConfirm } from './modal.js';
import { fetchStatus } from './status.js';

export function initActions() {
  // ── Start NAS ──
  dom.startBtn.addEventListener('click', async () => {
    dom.feedback.textContent = '';
    state.lastMessage = '';

    try {
      const data = await startNas();
      state.lastMessageType = data.success ? 'ok' : 'err';
      state.lastMessage     = data.success ? data.message : '⚠ ' + data.message;
    } catch {
      state.lastMessageType = 'err';
      state.lastMessage     = '⚠ Network error';
    }

    fetchStatus();
  });

  // ── Shutdown Now ──
  dom.shutdownNowBtn.addEventListener('click', () => {
    showConfirm('Shutdown NAS now?', async () => {
      dom.feedback.textContent = '';
      state.lastMessage = '';

      try {
        const data = await stopNas();
        state.lastMessageType = data.success ? 'ok' : 'err';
        state.lastMessage     = data.success ? data.message : '⚠ ' + data.message;
      } catch {
        state.lastMessageType = 'err';
        state.lastMessage     = '⚠ Network error';
      }

      fetchStatus();
    });
  });
}
