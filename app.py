import logging
from functools import wraps
from datetime import datetime, timedelta

from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from config import ADMIN_PASSWORD, ADMIN_USERNAME, SECRET_KEY
from database import (
    get_schedules,
    init_db,
    update_schedule,
    add_scheduled_shutdown,
    get_pending_shutdowns,
    delete_scheduled_shutdown,
    set_action_in_progress,
    get_action_in_progress,
    clear_action_in_progress,
)
from nas_controller import is_nas_online, shutdown_nas, wake_nas
from scheduler import init_scheduler, reload_schedules, reload_one_time_shutdowns

# ── Logging ──────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s  %(levelname)-8s  %(name)s  %(message)s',
)
logger = logging.getLogger(__name__)

# ── Flask app ────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'


# ── Auth helpers ─────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper


# ── Pages ────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        error = 'Invalid credentials'
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/static/manifest.json')
def manifest():
    """Serve manifest without login requirement."""
    return app.send_static_file('manifest.json')


@app.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html')


# ── API: NAS status ──────────────────────────────────────────
@app.route('/api/status')
@login_required
def api_status():
    online = is_nas_online()
    action = get_action_in_progress()
    
    # Auto-clear action if goal achieved
    if action:
        if action['action_type'] == 'start' and online:
            # NAS started successfully - clear action
            clear_action_in_progress()
            action = None
        elif action['action_type'] == 'stop' and not online:
            # NAS stopped successfully - clear action
            clear_action_in_progress()
            action = None
    
    return jsonify(
        online=online,
        action_in_progress=action is not None,
        action_type=action['action_type'] if action else None,
        action_elapsed=action['elapsed'] if action else None
    )


# ── API: start / stop ────────────────────────────────────────
@app.route('/api/start', methods=['POST'])
@login_required
def api_start():
    set_action_in_progress('start')
    ok, msg = wake_nas()
    return jsonify(success=ok, message=msg)


@app.route('/api/stop', methods=['POST'])
@login_required
def api_stop():
    set_action_in_progress('stop')
    ok, msg = shutdown_nas()
    return jsonify(success=ok, message=msg)


@app.route('/api/clear-action', methods=['POST'])
@login_required
def api_clear_action():
    """Manually clear action in progress (for testing or force reset)."""
    clear_action_in_progress()
    return jsonify(success=True)


# ── API: weekly schedules ────────────────────────────────────
@app.route('/api/schedules')
@login_required
def api_get_schedules():
    return jsonify(schedules=get_schedules())


@app.route('/api/schedules/<int:day>', methods=['PUT'])
@login_required
def api_update_schedule(day: int):
    if day < 0 or day > 6:
        return jsonify(success=False, message='Invalid day'), 400

    data = request.get_json(force=True)
    start_time = data.get('start_time', '08:00')
    stop_time  = data.get('stop_time', '22:00')
    enabled    = bool(data.get('enabled', False))

    update_schedule(day, start_time, stop_time, enabled)
    reload_schedules()
    return jsonify(success=True)


# ── API: one-time scheduled shutdowns ────────────────────────
@app.route('/api/scheduled-shutdowns', methods=['GET'])
@login_required
def api_get_scheduled_shutdowns():
    return jsonify(shutdowns=get_pending_shutdowns())


@app.route('/api/scheduled-shutdowns', methods=['POST'])
@login_required
def api_add_scheduled_shutdown():
    # Delete any existing pending shutdown (replace old with new)
    existing = get_pending_shutdowns()
    for shutdown in existing:
        delete_scheduled_shutdown(shutdown['id'])
    
    data = request.get_json(force=True)
    scheduled_at = data.get('scheduled_at')  # ISO datetime string
    
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


@app.route('/api/scheduled-shutdowns/<int:shutdown_id>', methods=['DELETE'])
@login_required
def api_delete_scheduled_shutdown(shutdown_id: int):
    delete_scheduled_shutdown(shutdown_id)
    reload_one_time_shutdowns()
    return jsonify(success=True)


# ── Startup ──────────────────────────────────────────────────
with app.app_context():
    init_db()
    init_scheduler()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
