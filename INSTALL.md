# NAS Control - Installation & Deployment Guide

## 🚀 Déploiement Automatique (Recommandé)

### Utilisation du script deploy.sh

Le script `deploy.sh` automatise le déploiement sur votre Raspberry Pi:

```bash
chmod +x deploy.sh
./deploy.sh [IP_RASPBERRY] [SSH_USER]
```

**Exemples:**
```bash
# Avec les valeurs par défaut (IP: 192.168.1.54, User SSH: jitrack)
./deploy.sh

# Avec une IP spécifique
./deploy.sh 192.168.1.100

# Avec IP et user SSH spécifiques
./deploy.sh 192.168.1.100 pi
```

> **Note**: Le 2ème paramètre est le **nom d'utilisateur SSH** de votre Raspberry Pi (ex: pi, jitrack, admin, etc.)

Le script va automatiquement :
- ✓ Copier tous les fichiers nécessaires
- ✓ Créer un environnement virtuel Python
- ✓ Installer toutes les dépendances
- ✓ Configurer le service systemd
- ✓ Activer et démarrer le service
- ✓ Afficher l'URL d'accès

## 📱 Installation PWA sur Android/iOS

### Sur Android (Chrome/Edge):
1. Ouvrez l'URL dans votre navigateur mobile: `http://[IP_RASPBERRY]:5000`
2. Tapez sur le menu (⋮) en haut à droite
3. Sélectionnez **"Installer l'application"** ou **"Ajouter à l'écran d'accueil"**
4. Confirmez l'installation
5. L'icône apparaîtra sur votre écran d'accueil

### Sur iOS (Safari):
1. Ouvrez l'URL dans Safari: `http://[IP_RASPBERRY]:5000`
2. Tapez sur le bouton **Partager** (carré avec flèche vers le haut)
3. Faites défiler et sélectionnez **"Sur l'écran d'accueil"**
4. Tapez **"Ajouter"**
5. L'icône apparaîtra sur votre écran d'accueil

> **Note**: Une fois installée, l'app fonctionne en mode "standalone" (plein écran, comme une app native)

## 🛠️ Installation Manuelle

Si vous préférez une installation manuelle sur la Raspberry Pi :

### 1. Copier les fichiers
```bash
# Sur votre PC
scp -r /chemin/vers/NASControl pi@192.168.1.20:/home/pi/
```

### 2. Installation sur la Raspberry Pi
```bash
ssh pi@192.168.1.20

cd /home/pi/NASControl

# Installer Python3 et pip (si nécessaire)
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv

# Créer l'environnement virtuel
python3 -m venv PythonEnv

# Activer et installer les dépendances
source PythonEnv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Test manuel
```bash
# Lancer l'application manuellement pour tester
source PythonEnv/bin/activate
python app.py
```

L'application devrait être accessible sur `http://[IP_RASPBERRY]:5000`

### 4. Configuration du service systemd

**Éditer le fichier service** (modifier les paths si nécessaire):
```bash
sudo nano /etc/systemd/system/nas-control.service
```

**Coller ce contenu** (ou utiliser le fichier `nas-control.service` fourni):
```ini
[Unit]
Description=NAS Control Web Application
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/NASControl
Environment="PATH=/home/pi/NASControl/PythonEnv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/pi/NASControl/PythonEnv/bin/python /home/pi/NASControl/app.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Activer et démarrer le service**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable nas-control.service
sudo systemctl start nas-control.service
```

## 📝 Commandes du Service

```bash
# Démarrer le service
sudo systemctl start nas-control

# Arrêter le service
sudo systemctl stop nas-control

# Redémarrer le service
sudo systemctl restart nas-control

# Voir le statut
sudo systemctl status nas-control

# Voir les logs en temps réel
sudo journalctl -u nas-control -f

# Voir les logs récents
sudo journalctl -u nas-control -n 50
```

## ⚙️ Configuration

### 1. Éditer config.py
```bash
nano config.py
```

Configurer:
- **NAS_IP_ADDRESS**: L'IP de votre NAS
- **NAS_MAC_ADDRESS**: L'adresse MAC pour Wake-on-LAN
- **TRUENAS_API_KEY**: Votre clé API TrueNAS (si utilisée)

### 2. Utilisateurs autorisés
Par défaut, seul l'utilisateur 'admin' avec le mot de passe 'admin' peut se connecter.

Pour modifier, éditez `app.py` et changez le dictionnaire `USERS`:
```python
USERS = {
    'admin': 'votre_mot_de_passe',
    'autre_user': 'autre_mdp'
}
```

## 🔧 Redéploiement

Après avoir modifié le code localement, redéployez facilement:

```bash
./deploy.sh
```

Le script va:
- Synchroniser tous les fichiers modifiés
- Redémarrer automatiquement le service
- Afficher le nouveau statut

## 🌐 Accès depuis l'extérieur

Pour accéder depuis l'extérieur de votre réseau local:

1. **Configuration du routeur** (Port Forwarding):
   - Port externe: 8080 (ou autre)
   - Port interne: 5000
   - IP locale: IP de votre Raspberry Pi

2. **Utilisation de HTTPS** (recommandé pour la sécurité):
   - Utilisez un reverse proxy comme Nginx avec Let's Encrypt
   - Ou configurez Flask pour utiliser SSL

## 🔍 Dépannage

### Le service ne démarre pas
```bash
# Vérifier les logs
sudo journalctl -u nas-control -n 100

# Vérifier que Python et les dépendances sont installées
source /home/pi/NASControl/PythonEnv/bin/activate
python -c "import flask; print('Flask OK')"
```

### Erreur de permission
```bash
# S'assurer que l'utilisateur 'pi' est propriétaire
sudo chown -R pi:pi /home/pi/NASControl
```

### Port déjà utilisé
```bash
# Vérifier quel processus utilise le port 5000
sudo lsof -i :5000

# Si nécessaire, tuez le processus
sudo kill [PID]
```

## 📦 Dépendances

Liste des dépendances Python (déjà dans `requirements.txt`):
- Flask
- wakeonlan
- paramiko
- APScheduler
- requests

## 🎯 Fonctionnalités

- ✅ Démarrage du NAS via Wake-on-LAN
- ✅ Arrêt du NAS via SSH ou API TrueNAS
- ✅ Arrêt programmé avec date/heure
- ✅ Détection automatique de l'état du NAS
- ✅ Interface responsive (mobile-friendly)
- ✅ PWA installable sur mobile (Android/iOS)
- ✅ Mise à jour en temps réel du statut
- ✅ Timer de countdown fluide pendant les actions
- ✅ Auto-démarrage au boot de la Raspberry Pi

## 🔐 Sécurité

⚠️ **Important**: Cette application est conçue pour un réseau local sécurisé.

Pour une utilisation en production ou accessible depuis Internet:
- Changez les mots de passe par défaut
- Utilisez HTTPS avec des certificats SSL
- Configurez un firewall
- Limitez l'accès par IP si possible
- Utilisez des clés SSH au lieu de mots de passe

## 📞 Support

Pour toute question ou problème:
1. Vérifiez les logs: `sudo journalctl -u nas-control -f`
2. Vérifiez la configuration dans `config.py`
3. Testez la connectivité réseau vers le NAS
