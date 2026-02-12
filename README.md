# RaspiWakeOnLan

Interface web pour contrôler le démarrage/arrêt d'un NAS via Wake-on-LAN et SSH, avec planification hebdomadaire.

## 🚀 Installation

### 1. Cloner le projet
```bash
cd ~
git clone <url> RaspiWakeOnLan
cd RaspiWakeOnLan
```

### 2. Installer les dépendances Python
**All dependencies are installed in the virtual environment PythonEnv/**
```bash
# Dependencies are already installed in PythonEnv/
# If you need to reinstall:
./PythonEnv/bin/pip install -r requirements.txt
```

### 3. Configurer
Éditer `config.py` avec vos valeurs :
- `NAS_MAC_ADDRESS` : adresse MAC du NAS (pour WOL)
- `NAS_IP_ADDRESS` : adresse IP du NAS
- `NAS_SSH_USER` : utilisateur SSH du NAS
- `NAS_SSH_KEY_PATH` : chemin vers la clé SSH
- `ADMIN_USERNAME` / `ADMIN_PASSWORD` : identifiants web

### 4. Configurer l'accès SSH au NAS

**Sur le Raspberry Pi :**
```bash
ssh-keygen -t ed25519 -f ~/.ssh/nas
ssh-copy-id -i ~/.ssh/nas.pub truenas_admin@192.168.1.81
```

**Sur le NAS (permettre shutdown sans mot de passe) :**
```bash
echo "truenas_admin ALL=(ALL) NOPASSWD: /sbin/shutdown" | sudo tee /etc/sudoers.d/shutdown
sudo chmod 440 /etc/sudoers.d/shutdown
```

## ▶️ Démarrage

**Using the start script (recommended):**
```bash
./start.sh
```

**Or manually:**
```bash
source PythonEnv/bin/activate
python app.py
```

Accessible sur : `http://<ip-raspberry>:5000`

## 🔄 Démarrage automatique (systemd)

Créer `/etc/systemd/system/naswol.service` :
```ini
[Unit]
Description=NAS Wake-on-LAN Controller
After=network.target

[Service]
Type=simple
User=jitrack
WorkingDirectory=/home/jitrack/NAS/RaspiWakeOnLan
ExecStart=/home/jitrack/NAS/RaspiWakeOnLan/start.sh
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Activer :
```bash
sudo systemctl daemon-reload
sudo systemctl enable naswol
sudo systemctl start naswol
```

## � Progressive Web App (PWA)

L'application peut être installée sur votre téléphone comme une app native !
Voir [PWA_SETUP.md](PWA_SETUP.md) pour les instructions.

## 🔌 API TrueNAS (Recommandé)

**Nouveau !** Utilisez l'API TrueNAS pour éteindre le NAS sans besoin de sudo.
Voir [TRUENAS_API.md](TRUENAS_API.md) pour la configuration complète.

**Avantages** :
- ✓ Pas de permissions sudo nécessaires
- ✓ Configuration stable après reboot
- ✓ Gestion des permissions via TrueNAS

## �🗑️ Reset de la base de données

```bash
rm schedules.db
```

La DB sera recréée au prochain démarrage avec les valeurs par défaut.

## 🌐 Accès via Cloudflare Tunnel

```bash
cloudflared tunnel --url http://localhost:5000
```

## 📋 Fonctionnalités

- ✅ Détection automatique de l'état du NAS (ping toutes les 5s)
- ✅ Bouton dynamique Start/Stop
- ✅ Wake-on-LAN pour démarrer
- ✅ SSH shutdown pour éteindre
- ✅ Planification hebdomadaire (heure de démarrage/arrêt par jour)
- ✅ Authentification web simple
