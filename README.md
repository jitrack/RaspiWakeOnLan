# NAS Control

Interface web pour contrôler le démarrage/arrêt d'un NAS via Wake-on-LAN et l'API TrueNAS, avec planification hebdomadaire. Installable en PWA sur mobile.

## 📁 Architecture

```
├── server/                  # Backend Python (Flask)
│   ├── app.py               # Application Flask + routes API
│   ├── config.py            # Configuration (NAS, auth, DB)
│   ├── database.py          # Couche SQLite
│   ├── nas_controller.py    # WOL, ping, TrueNAS API client
│   └── scheduler.py         # APScheduler (tâches planifiées)
├── front/                   # Frontend
│   ├── templates/
│   │   ├── base.html        # Template de base (head, PWA, SW)
│   │   ├── components/      # Composants réutilisables
│   │   │   ├── navbar.html
│   │   │   ├── status_card.html
│   │   │   ├── weekly_schedule.html
│   │   │   └── confirm_modal.html
│   │   ├── dashboard.html   # Page principale
│   │   └── login.html       # Page de connexion
│   └── static/
│       ├── css/style.css     # Thème Catppuccin Mocha
│       ├── js/
│       │   ├── api.js        # Routes API encapsulées
│       │   ├── state.js      # État global + refs DOM
│       │   ├── status.js     # Polling + timer countdown
│       │   ├── actions.js    # Actions start/stop
│       │   ├── schedule.js   # Planification hebdo + one-time
│       │   ├── modal.js      # Modal de confirmation
│       │   └── app.js        # Point d'entrée (init modules)
│       ├── service-worker.js # PWA offline support
│       └── manifest.json     # PWA manifest
├── deploy/                  # Scripts de déploiement
│   ├── deploy.sh            # Déploiement auto sur Raspberry Pi
│   ├── setup-ssh-key.sh     # Config SSH sans mot de passe
│   ├── nas-control.service  # Service systemd
│   ├── create_icons.py      # Génération icônes PWA
│   └── generate_favicon.py  # Génération favicon
├── requirements.txt         # Dépendances Python
├── start.sh                 # Script de lancement local
├── README.md
├── INSTALL.md               # Guide d'installation complet
└── TRUENAS_API.md           # Documentation API TrueNAS
```

## 🚀 Déploiement rapide

```bash
# Déployer sur la Raspberry Pi (une seule commande)
./deploy/deploy.sh

# Ou avec IP/user spécifiques
./deploy/deploy.sh 192.168.1.100 pi
```

Voir [INSTALL.md](INSTALL.md) pour le guide complet.

## ⚙️ Configuration

Éditer `server/config.py` :
- `NAS_MAC_ADDRESS` – adresse MAC du NAS (pour WOL)
- `NAS_IP_ADDRESS` – adresse IP du NAS
- `TRUENAS_API_KEY` – clé API TrueNAS (recommandé)
- `ADMIN_USERNAME` / `ADMIN_PASSWORD` – identifiants web

## ▶️ Lancement local

```bash
./start.sh
# ou
PythonEnv/bin/python server/app.py
```

Accessible sur : `http://localhost:5000`

## 📋 Fonctionnalités

- ✅ Démarrage du NAS via Wake-on-LAN
- ✅ Arrêt via API TrueNAS (ou SSH fallback)
- ✅ Planification hebdomadaire (start/stop par jour)
- ✅ Arrêt programmé ponctuel (date/heure)
- ✅ Détection automatique de l'état (ping adaptatif)
- ✅ Timer countdown fluide pendant les actions
- ✅ PWA installable sur Android/iOS
- ✅ Thème dark Catppuccin Mocha
- ✅ Auto-démarrage via systemd
- ✅ Déploiement automatisé

## 🔌 API TrueNAS

Voir [TRUENAS_API.md](TRUENAS_API.md) pour la configuration de l'API.
Avantages : pas de sudo, pas de clé SSH, gestion via TrueNAS directement.

