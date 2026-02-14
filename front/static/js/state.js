// ── Shared Application State ────────────────────────────────

export const state = {
  nasOnline:           null,
  actionInProgress:    false,
  actionType:          null,
  actionElapsed:       0,
  actionStartTime:     null,
  lastMessage:         '',
  lastMessageType:     '',
  lastScheduleOffset:  5,
  statusPollInterval:  null,
  timerUpdateInterval: null,
};

// ── DOM element references ──────────────────────────────────
export const dom = {};

export function initDom() {
  dom.statusDot           = document.getElementById('status-indicator');
  dom.statusText          = document.getElementById('status-text');
  dom.startBtnContainer   = document.getElementById('start-button-container');
  dom.startBtn            = document.getElementById('start-btn');
  dom.shutdownButtons     = document.getElementById('shutdown-buttons');
  dom.feedback            = document.getElementById('action-feedback');
  dom.schedBody           = document.getElementById('schedule-body');

  dom.shutdownNowBtn      = document.getElementById('shutdown-now-btn');
  dom.scheduleShutdownBtn = document.getElementById('schedule-shutdown-btn');
  dom.scheduleForm        = document.getElementById('schedule-form');
  dom.scheduleDate        = document.getElementById('schedule-date');
  dom.scheduleTime        = document.getElementById('schedule-time');
  dom.scheduleConfirmBtn  = document.getElementById('schedule-confirm-btn');
  dom.scheduleFeedback    = document.getElementById('schedule-feedback');
  dom.scheduledInfo       = document.getElementById('scheduled-info');
  dom.scheduledDateDisplay = document.getElementById('scheduled-date-display');
  dom.cancelScheduleBtn   = document.getElementById('cancel-schedule-btn');

  dom.confirmModal        = document.getElementById('confirm-modal');
  dom.modalMessage        = document.getElementById('modal-message');
  dom.modalConfirm        = document.getElementById('modal-confirm');
  dom.modalCancel         = document.getElementById('modal-cancel');
}
