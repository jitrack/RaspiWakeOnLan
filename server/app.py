"""NAS Control – Flask application entry point."""

import logging
import os

from flask import Flask

from config import SECRET_KEY
from database import init_db
from scheduler import init_scheduler

# ── Logging ──────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s  %(levelname)-8s  %(name)s  %(message)s',
)

# ── Flask app ────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(
    __name__,
    template_folder=os.path.join(PROJECT_ROOT, 'front', 'templates'),
    static_folder=os.path.join(PROJECT_ROOT, 'front', 'static'),
    static_url_path='/static',
)
app.secret_key = SECRET_KEY
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# ── Register blueprints ─────────────────────────────────────
from routes_front import front  # noqa: E402
from routes_api import api      # noqa: E402

app.register_blueprint(front)
app.register_blueprint(api)


# ── Serve manifest without auth ──────────────────────────────
@app.route('/static/manifest.json')
def manifest():
    return app.send_static_file('manifest.json')


# ── Startup ──────────────────────────────────────────────────
with app.app_context():
    init_db()
    init_scheduler()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
