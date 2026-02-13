#!/usr/bin/env python3
"""
Diagnostic tool for NAS Control application issues
"""
import sys
sys.path.insert(0, '.')

from config import NAS_IP_ADDRESS, USE_TRUENAS_API, TRUENAS_API_KEY, TRUENAS_API_URL
from nas_controller import is_nas_online, wake_nas, shutdown_nas
import subprocess

def test_connectivity():
    print("=" * 60)
    print("NAS Control - Diagnostic Tool")
    print("=" * 60)
    
    print(f"\n📋 Configuration:")
    print(f"  NAS IP: {NAS_IP_ADDRESS}")
    print(f"  API Mode: {'Enabled' if USE_TRUENAS_API else 'SSH'}")
    print(f"  API URL: {TRUENAS_API_URL}")
    
    print(f"\n🔌 Testing Network Connectivity...")
    
    # Test 1: Ping
    print(f"  [1/4] Ping {NAS_IP_ADDRESS}... ", end='', flush=True)
    try:
        result = subprocess.run(
            ['ping', '-c', '1', '-W', '2', NAS_IP_ADDRESS],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✅ OK")
        else:
            print("❌ FAILED - NAS is not reachable")
            return
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return
    
    # Test 2: NAS online check
    print(f"  [2/4] is_nas_online()... ", end='', flush=True)
    online = is_nas_online()
    print(f"{'✅ Online' if online else '❌ Offline'}")
    
    # Test 3: TrueNAS web interface
    print(f"  [3/4] HTTPS web interface... ", end='', flush=True)
    try:
        import requests
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        response = requests.get(
            f'https://{NAS_IP_ADDRESS}',
            verify=False,
            timeout=5
        )
        if response.status_code == 200:
            print("✅ Accessible")
        else:
            print(f"⚠️  Status {response.status_code}")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Test 4: API
    if USE_TRUENAS_API:
        print(f"  [4/4] TrueNAS API... ", end='', flush=True)
        try:
            response = requests.get(
                f'{TRUENAS_API_URL}/api/v2.0/system/info',
                headers={'Authorization': f'Bearer {TRUENAS_API_KEY}'},
                verify=False,
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ OK (v{data.get('version', 'unknown')})")
            elif response.status_code == 401:
                print("❌ Authentication failed - Invalid API key")
            else:
                print(f"⚠️  Status {response.status_code}")
        except Exception as e:
            print(f"❌ FAILED: {e}")
    else:
        print(f"  [4/4] SSH... (skipped in diagnostic)")
    
    print(f"\n🔍 Application Status:")
    print(f"  Flask app running: Check with 'ps aux | grep app.py'")
    print(f"  Access URL: http://localhost:5000")
    print(f"  Or: http://{subprocess.getoutput('hostname -I').split()[0]}:5000")
    
    print("\n" + "=" * 60)
    print("💡 Common Issues:")
    print("  - Browser cache: Hard refresh (Ctrl+Shift+R)")
    print("  - Check browser console (F12) for JavaScript errors")
    print("  - Restart Flask app: ./start.sh")
    print("  - Check firewall rules on NAS")
    print("=" * 60)

if __name__ == '__main__':
    test_connectivity()
