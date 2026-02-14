"""API routes – all /api/* endpoints."""

from datetime import datetime

from flask import Blueprint, jsonify, request

from database import (
    get_schedules,
    update_schedule,
    add_scheduled_shutdown,
    get_pending_shutdowns,
    delete_scheduled_shutdown,
    set_action_in_progress,
    get_action_in_progress,
    clear_action_in_progress,
)
from nas_controller import is_nas_online, shutdown_nas, wake_nas
from scheduler import reload_schedules, reload_one_time_shutdowns
from auth import login_required

api = Blueprint('api', __name__, url_prefix='/api')


# ── Status ───────────────────────────────────────────────────
@api.route('/status')
@login_required
def status():
    online = is_nas_online()
    action = get_action_in_progress()

    if action:
        if action['action_type'] == 'start' and online:
            clear_action_in_progress()
            action = None
        elif action['action_type'] == 'stop' and not online:
            clear_action_in_progress()
            action = None

    return jsonify(
        online=online,
        action_in_progress=action is not None,
        action_type=action['action_type'] if action else None,
        action_elapsed=action['elapsed'] if action else None,
    )


# ── Start / Stop ─────────────────────────────────────────────
@api.route('/start', methods=['POST'])
@login_required
def start():
    set_action_in_progress('start')
    ok, msg = wake_nas()
    return jsonify(success=ok, message=msg)


@api.route('/stop', methods=['POST'])
@login_required
def stop():
    set_action_in_progress('stop')
    ok, msg = shutdown_nas()
    return jsonify(success=ok, message=msg)


@api.route('/clear-action', methods=['POST'])
@login_required
def clear_action():
    clear_action_in_progress()
    return jsonify(success=True)


# ── Weekly schedules ─────────────────────────────────────────
@api.route('/schedules')
@login_required
def get_schedules_route():
    return jsonify(schedules=get_schedules())


@api.route('/schedules/<int:day>', methods=['PUT'])
@login_required
def update_schedule_route(day: int):
    if day < 0 or day > 6:
        return jsonify(success=False, message='Invalid day'), 400

    data = request.get_json(force=True)
    update_schedule(
        day,
        data.get('start_time', '08:00'),
        data.get('stop_time', '22:00'),
        bool(data.get('enabled', False)),
    )
    reload_schedules()
    return jsonify(success=True)


# ── Scheduled shutdowns ─────────────────────────────────────
@api.route('/scheduled-shutdowns', methods=['GET'])
@login_required
def get_shutdowns():
    return jsonify(shutdowns=get_pending_shutdowns())


@api.route('/scheduled-shutdowns', methods=['POST'])
@login_required
def add_shutdown():
    for s in get_pending_shutdowns():
        delete_scheduled_shutdown(s['id'])

    data = request.get_json(force=True)
    scheduled_at = data.get('scheduled_at')

    if not scheduled_at:
        return jsonify(success=False, message='Missing scheduled_at'), 400

    try:
        dt = datetime.fromisoformat(scheduled_at)
        if dt <= datetime.now():
            return jsonify(success=False, message='Time must be in the future'), 400

        add_scheduled_shutdown(scheduled_at)
        reload_one_time_shutdowns()
        return jsonify(success=True, message=f'Shutdown scheduled for {dt.strftime("%Y-%m-%d %H:%M")}')
    except ValueError:
        return jsonify(success=False, message='Invalid datetime format'), 400


@api.route('/scheduled-shutdowns/<int:shutdown_id>', methods=['DELETE'])
@login_required
def remove_shutdown(shutdown_id: int):
    delete_scheduled_shutdown(shutdown_id)
    reload_one_time_shutdowns()
    return jsonify(success=True)
