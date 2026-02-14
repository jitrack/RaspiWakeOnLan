// ── NAS Control – Main Entry Point ──────────────────────────

import { initDom, state } from './state.js';
import { initModal } from './modal.js';
import { fetchStatus, adjustPollingRate, renderStatus } from './status.js';
import { initActions } from './actions.js';
import { loadSchedules, loadScheduledShutdown, initSchedule } from './schedule.js';

// Initialize DOM references
initDom();

// Initialize modules
initModal();
initActions();
initSchedule();

// Initial data load
fetchStatus();
loadSchedules();
loadScheduledShutdown();
adjustPollingRate();

// Periodic refresh
setInterval(loadScheduledShutdown, 10000);
setInterval(() => {
  if (state.actionInProgress) renderStatus();
}, 1000);
