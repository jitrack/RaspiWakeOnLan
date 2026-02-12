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
    USE_TRUENAS_API,
    TRUENAS_API_KEY,
    TRUENAS_API_URL,
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
    """Shutdown the NAS via TrueNAS API or SSH."""
    if USE_TRUENAS_API:
        return _shutdown_via_api()
    else:
        return _shutdown_via_ssh()


def _shutdown_via_api() -> tuple[bool, str]:
    """Shutdown via TrueNAS API (no sudo needed!)."""
    try:
        import requests
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        response = requests.post(
            f'{TRUENAS_API_URL}/api/v2.0/system/shutdown',
            headers={'Authorization': f'Bearer {TRUENAS_API_KEY}'},
            verify=False,  # Skip SSL verification for self-signed certs
            timeout=10,
        )
        
        if response.status_code in [200, 202]:
            logger.info('Shutdown command sent via API')
            return True, 'Shutdown command sent via API'
        else:
            logger.error(f'API shutdown failed: {response.status_code} {response.text}')
            return False, f'API error: {response.status_code}'
    except Exception as e:
        logger.error('API shutdown failed: %s', e)
        return False, str(e)


def _shutdown_via_ssh() -> tuple[bool, str]:
    """Shutdown via SSH (requires sudo permissions)."""
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
        client.exec_command('sudo /sbin/shutdown now')
        client.close()
        logger.info('Shutdown command sent via SSH')
        return True, 'Shutdown command sent via SSH'
    except Exception as e:
        logger.error('SSH shutdown failed: %s', e)
        return False, str(e)
