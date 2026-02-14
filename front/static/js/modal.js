// ── Confirmation Modal ──────────────────────────────────────

import { dom } from './state.js';

let pendingAction = null;

export function showConfirm(message, onConfirm) {
  dom.modalMessage.textContent = message;
  dom.confirmModal.style.display = 'flex';
  pendingAction = onConfirm;
}

export function hideConfirm() {
  dom.confirmModal.style.display = 'none';
  pendingAction = null;
}

export function initModal() {
  dom.modalConfirm.addEventListener('click', () => {
    if (pendingAction) pendingAction();
    hideConfirm();
  });

  dom.modalCancel.addEventListener('click', hideConfirm);

  dom.confirmModal.addEventListener('click', (e) => {
    if (e.target === dom.confirmModal) hideConfirm();
  });
}
