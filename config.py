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

# TrueNAS API (alternative à SSH pour shutdown)
# Créer une API Key : TrueNAS Web UI → Top right → API Keys
USE_TRUENAS_API = True  # True pour utiliser l'API, False pour SSH
TRUENAS_API_KEY = '1-NE2GQKbO0AYBVVSHgBKx9HFwl36056Mv7IUrIJeOR5ginTadivtO1vpwYkB1rutr'  # Votre API key TrueNAS
TRUENAS_API_URL = f'https://{NAS_IP_ADDRESS}'  # URL de l'API TrueNAS

# ---------- Authentification web ----------
ADMIN_USERNAME = 'jitrack'
ADMIN_PASSWORD = 'Harko-yann96'              # ⚠ À modifier !

# ---------- Flask ----------
SECRET_KEY = '2Yfq6ZaMrfFigT'    # ⚠ À modifier !

# ---------- Base de données ----------
DATABASE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'schedules.db'
)
