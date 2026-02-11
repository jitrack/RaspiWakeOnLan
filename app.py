import logging
from functools import wraps

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
from database import get_schedules, init_db, update_schedule
from nas_controller import is_nas_online, shutdown_nas, wake_nas
from scheduler import init_scheduler, reload_schedules

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
        error = 'Identifiants incorrects'
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html')


# ── API : état du NAS ────────────────────────────────────────
@app.route('/api/status')
@login_required
def api_status():
    return jsonify(online=is_nas_online())


# ── API : démarrer / arrêter ─────────────────────────────────
@app.route('/api/start', methods=['POST'])
@login_required
def api_start():
    ok, msg = wake_nas()
    return jsonify(success=ok, message=msg)


@app.route('/api/stop', methods=['POST'])
@login_required
def api_stop():
    ok, msg = shutdown_nas()
    return jsonify(success=ok, message=msg)


# ── API : planifications ─────────────────────────────────────
@app.route('/api/schedules')
@login_required
def api_get_schedules():
    return jsonify(schedules=get_schedules())


@app.route('/api/schedules/<int:day>', methods=['PUT'])
@login_required
def api_update_schedule(day: int):
    if day < 0 or day > 6:
        return jsonify(success=False, message='Jour invalide'), 400

    data = request.get_json(force=True)
    start_time = data.get('start_time', '08:00')
    stop_time  = data.get('stop_time', '22:00')
    enabled    = bool(data.get('enabled', False))

    update_schedule(day, start_time, stop_time, enabled)
    reload_schedules()
    return jsonify(success=True)


# ── Démarrage ────────────────────────────────────────────────
with app.app_context():
    init_db()
    init_scheduler()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
