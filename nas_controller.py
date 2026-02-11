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
    """Ping the NAS – returns True if reachable."""
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
    """Send a Wake-on-LAN Magic Packet."""
    try:
        send_magic_packet(NAS_MAC_ADDRESS)
        logger.info('Magic packet sent to %s', NAS_MAC_ADDRESS)
        return True, 'Magic packet sent'
    except Exception as e:
        logger.error('WOL failed: %s', e)
        return False, str(e)


def shutdown_nas() -> tuple[bool, str]:
    """Shutdown the NAS via SSH (sudo shutdown -h now)."""
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
        logger.info('Shutdown command sent to NAS')
        return True, 'Shutdown command sent'
    except Exception as e:
        logger.error('Shutdown failed: %s', e)
        return False, str(e)
