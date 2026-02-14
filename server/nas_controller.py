"""NAS controller – WOL, ping, shutdown (API or SSH)."""

import logging
import subprocess

import paramiko
import requests
import urllib3
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

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


# ── TrueNAS API Client ──────────────────────────────────────
class TrueNASAPI:
    """Client for TrueNAS Scale REST API v2.0."""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        })
        self.session.verify = False

    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        url = f'{self.base_url}/api/v2.0{endpoint}'
        return self.session.request(method, url, timeout=10, **kwargs)

    def get_system_info(self) -> dict | None:
        """Fetch system info (hostname, version, uptime)."""
        try:
            res = self._request('GET', '/system/info')
            if res.ok:
                return res.json()
        except Exception as e:
            logger.error('TrueNAS API – system info failed: %s', e)
        return None

    def shutdown(self, reason: str = 'Shutdown via NAS Control') -> tuple[bool, str]:
        """Send shutdown command via REST API."""
        try:
            res = self._request('POST', '/system/shutdown', json={'reason': reason})
            if res.status_code in (200, 202):
                logger.info('TrueNAS API – shutdown command sent')
                return True, 'Shutdown command sent via API'
            logger.error('TrueNAS API – shutdown failed: %d %s', res.status_code, res.text)
            return False, f'API error: {res.status_code}'
        except requests.ConnectionError:
            return False, 'Cannot connect to TrueNAS API'
        except requests.Timeout:
            return False, 'TrueNAS API timeout'
        except Exception as e:
            logger.error('TrueNAS API – shutdown error: %s', e)
            return False, str(e)


# Initialize API client (singleton)
_api = TrueNASAPI(TRUENAS_API_URL, TRUENAS_API_KEY) if USE_TRUENAS_API else None


# ── Public functions ─────────────────────────────────────────
def is_nas_online() -> bool:
    """Ping the NAS – returns True if reachable."""
    try:
        result = subprocess.run(
            ['ping', '-c', '1', '-W', '1', NAS_IP_ADDRESS],
            capture_output=True, timeout=2,
        )
        return result.returncode == 0
    except Exception:
        return False


def wake_nas() -> tuple[bool, str]:
    """Send a Wake-on-LAN magic packet."""
    try:
        send_magic_packet(NAS_MAC_ADDRESS)
        logger.info('Magic packet sent to %s', NAS_MAC_ADDRESS)
        return True, 'Magic packet sent'
    except Exception as e:
        logger.error('WOL failed: %s', e)
        return False, str(e)


def shutdown_nas() -> tuple[bool, str]:
    """Shutdown NAS via TrueNAS API or SSH fallback."""
    if _api:
        return _api.shutdown()
    return _shutdown_via_ssh()


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
