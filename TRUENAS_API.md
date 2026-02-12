# Configuration TrueNAS API pour Shutdown

## 🎯 Pourquoi utiliser l'API ?

**Avantage principal : Pas besoin de sudo !**

Avec l'API TrueNAS, votre utilisateur `truenas_admin` peut éteindre le NAS **sans avoir besoin de permissions sudo** dans le système. L'API gère les permissions elle-même basée sur les droits de l'utilisateur dans TrueNAS.

### SSH vs API

| Méthode | Avantages | Inconvénients |
|---------|-----------|---------------|
| **SSH** | Simple, standard | Nécessite sudo, fichier sudoers se réinitialise au reboot sur TrueNAS Scale |
| **API** | Pas de sudo nécessaire, permissions via TrueNAS, stable après reboot | Nécessite configuration API key |

## 📝 Configuration de l'API

### Étape 1 : Créer une API Key dans TrueNAS

1. **Connectez-vous** à l'interface web TrueNAS : `https://192.168.1.81`

2. **Créer la clé API** :
   - Cliquez sur votre nom d'utilisateur en haut à droite
   - Sélectionnez **"API Keys"**
   - Cliquez **"Add"**

3. **Configuration de la clé** :
   - **Name** : `NAS Control App` (ou tout autre nom descriptif)
   - **User** : `truenas_admin` (votre utilisateur admin)
   - **Allowed Methods** : `POST` (pour shutdown)
   - **Reset** : Ne pas cocher

4. **Copier la clé** :
   - Une fois créée, TrueNAS affiche la clé API
   - **IMPORTANT** : Copiez-la immédiatement, elle ne sera plus affichée !
   - Format : `1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### Étape 2 : Configurer l'application

Éditez [config.py](config.py) :

```python
# TrueNAS API (alternative à SSH pour shutdown)
USE_TRUENAS_API = True  # ✓ Changer à True
TRUENAS_API_KEY = '1-votre-clé-api-ici'  # ✓ Coller votre clé
TRUENAS_API_URL = f'https://{NAS_IP_ADDRESS}'  # ✓ Devrait être déjà correct
```

### Étape 3 : Tester

1. **Redémarrez l'application** :
   ```bash
   # Si l'app est déjà lancée, arrêtez-la (Ctrl+C)
   ./start.sh
   ```

2. **Testez le shutdown** :
   - Connectez-vous à l'interface web
   - Cliquez sur "Shutdown Now"
   - Le NAS devrait s'éteindre sans erreur

## 🔍 Vérification des Permissions

### Permissions API nécessaires

Pour que l'API fonctionne, votre utilisateur `truenas_admin` doit avoir :
- ✓ **Droits d'administration** dans TrueNAS (admin group)
- ✓ **API key valide** créée pour cet utilisateur

### Test manuel de l'API

Vous pouvez tester l'API manuellement avec curl :

```bash
curl -k -X POST https://192.168.1.81/api/v2.0/system/shutdown \
  -H "Authorization: Bearer 1-votre-clé-api-ici"
```

**Réponse attendue** :
- Code 200 ou 202 : ✓ Succès
- Code 401 : ✗ Clé API invalide
- Code 403 : ✗ Permissions insuffisantes

## ⚙️ Comment ça marche

### Avec SSH (ancienne méthode)
```
App → SSH → truenas_admin@NAS → sudo shutdown → besoin sudoers
                                  ↑ PROBLÈME : Se réinitialise au reboot
```

### Avec API (nouvelle méthode)
```
App → HTTPS → TrueNAS API → Permissions utilisateur → Shutdown
              ↑ PAS DE SUDO NÉCESSAIRE
              ↑ Permissions gérées par TrueNAS
              ↑ Stable après reboot
```

## 🔐 Sécurité de l'API Key

### Bonnes pratiques

✓ **Stocker en sécurité** : La clé est dans `config.py` (non versionnée via .gitignore)
✓ **Permissions minimales** : Créer une clé spécifique pour cette app
✓ **Renouvellement** : Changer la clé régulièrement
✗ **Ne jamais** : Commiter la clé dans Git, la partager publiquement

### Révoquer une clé

Si la clé est compromise :
1. TrueNAS Web UI → API Keys
2. Sélectionner la clé → Delete
3. Créer une nouvelle clé
4. Mettre à jour `config.py`

## 🐛 Dépannage

### Erreur : "API error: 401"
**Cause** : Clé API invalide ou expirée
**Solution** : Vérifier la clé dans `config.py`, créer une nouvelle si nécessaire

### Erreur : "API error: 403"
**Cause** : Utilisateur sans permissions suffisantes
**Solution** : 
- Vérifier que `truenas_admin` est dans le groupe admin
- Créer une nouvelle API key avec l'utilisateur admin

### Erreur : "SSL Certificate verify failed"
**Cause** : Certificat auto-signé TrueNAS
**Solution** : Normal, l'app utilise `verify=False` pour ignorer le certificat

### Erreur : "Connection refused"
**Cause** : TrueNAS inaccessible ou URL incorrecte
**Solution** : Vérifier `TRUENAS_API_URL` dans `config.py`, tester ping vers le NAS

## 🔄 Retour à SSH

Si vous préférez revenir à SSH :

1. Éditez [config.py](config.py) :
   ```python
   USE_TRUENAS_API = False
   ```

2. Configurez les sudoers via Init Script (voir [TRUENAS_SUDOERS.md](TRUENAS_SUDOERS.md))

3. Redémarrez l'application

## 📚 Référence API TrueNAS

Documentation officielle : https://www.truenas.com/docs/api/

Endpoints utilisés par cette app :
- `POST /api/v2.0/system/shutdown` : Éteindre le système
