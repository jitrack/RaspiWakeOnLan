import os

# =============================================================
#  Configuration – Modifier les valeurs ci-dessous
# =============================================================

# ---------- NAS ----------
NAS_MAC_ADDRESS = '54:bf:64:68:99:a8'   # Adresse MAC du NAS
NAS_IP_ADDRESS  = '192.168.1.81'       # Adresse IP du NAS

# SSH (utilisé pour éteindre le NAS)
NAS_SSH_USER     = 'truenas_admin'
NAS_SSH_PORT     = 22
NAS_SSH_KEY_PATH = os.path.expanduser('~/.ssh/nas')

# ---------- Authentification web ----------
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'Harko-yann96'              # ⚠ À modifier !

# ---------- Flask ----------
SECRET_KEY = 'change-this-secret-key'    # ⚠ À modifier !

# ---------- Base de données ----------
DATABASE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'schedules.db'
)
