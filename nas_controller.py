import subprocess
import logging

import paramiko
from wakeonlan import send_magic_packet

from config import (
    NAS_MAC_ADDRESS,
    NAS_IP_ADDRESS,
    NAS_SSH_USER,
    NAS_SSH_KEY_PATH,
    NAS_SSH_PORT,
)

logger = logging.getLogger(__name__)


def is_nas_online() -> bool:
    """Ping le NAS – retourne True si joignable."""
    try:
        result = subprocess.run(
            ['ping', '-c', '1', '-W', '2', NAS_IP_ADDRESS],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False


def wake_nas() -> tuple[bool, str]:
    """Envoie un Magic Packet Wake-on-LAN."""
    try:
        send_magic_packet(NAS_MAC_ADDRESS)
        logger.info('Magic packet envoyé à %s', NAS_MAC_ADDRESS)
        return True, 'Magic packet envoyé'
    except Exception as e:
        logger.error('Échec WOL : %s', e)
        return False, str(e)


def shutdown_nas() -> tuple[bool, str]:
    """Éteint le NAS via SSH (sudo shutdown -h now)."""
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            NAS_IP_ADDRESS,
            port=NAS_SSH_PORT,
            username=NAS_SSH_USER,
            key_filename=NAS_SSH_KEY_PATH,
            timeout=10,
        )
        client.exec_command('sudo shutdown -h now')
        client.close()
        logger.info('Commande shutdown envoyée au NAS')
        return True, "Commande d'arrêt envoyée"
    except Exception as e:
        logger.error('Échec shutdown : %s', e)
        return False, str(e)
