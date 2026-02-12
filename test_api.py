#!/usr/bin/env python3
"""
Test TrueNAS API connection and permissions
"""
import sys
sys.path.insert(0, '.')

from config import USE_TRUENAS_API, TRUENAS_API_KEY, TRUENAS_API_URL, NAS_IP_ADDRESS

def test_api():
    print("=" * 60)
    print("TrueNAS API Configuration Test")
    print("=" * 60)
    
    print(f"\n📋 Configuration:")
    print(f"  USE_TRUENAS_API: {USE_TRUENAS_API}")
    print(f"  TRUENAS_API_URL: {TRUENAS_API_URL}")
    print(f"  API Key set: {'Yes' if TRUENAS_API_KEY != 'YOUR_API_KEY_HERE' else 'No (not configured)'}")
    
    if not USE_TRUENAS_API:
        print(f"\n⚠️  API mode is DISABLED")
        print(f"   To enable: Edit config.py and set USE_TRUENAS_API = True")
        return
    
    if TRUENAS_API_KEY == 'YOUR_API_KEY_HERE':
        print(f"\n❌ API key not configured!")
        print(f"   1. Create an API key in TrueNAS Web UI")
        print(f"   2. Edit config.py and paste your key in TRUENAS_API_KEY")
        print(f"\n   See TRUENAS_API.md for detailed instructions")
        return
    
    print(f"\n🔌 Testing API connection...")
    
    try:
        import requests
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Test API with a simple GET request (system/info)
        response = requests.get(
            f'{TRUENAS_API_URL}/api/v2.0/system/info',
            headers={'Authorization': f'Bearer {TRUENAS_API_KEY}'},
            verify=False,
            timeout=10,
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API connection successful!")
            print(f"   Hostname: {data.get('hostname', 'N/A')}")
            print(f"   Version: {data.get('version', 'N/A')}")
            print(f"\n✅ Your API key has valid permissions!")
            print(f"   Shutdown via API should work correctly.")
        elif response.status_code == 401:
            print(f"❌ Authentication failed (401)")
            print(f"   Your API key is invalid or expired")
            print(f"   Create a new key in TrueNAS Web UI")
        elif response.status_code == 403:
            print(f"❌ Permission denied (403)")
            print(f"   Your user doesn't have sufficient permissions")
            print(f"   Ensure your user is in the admin group")
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to TrueNAS")
        print(f"   URL: {TRUENAS_API_URL}")
        print(f"   Check that:")
        print(f"   - NAS IP is correct in config.py: {NAS_IP_ADDRESS}")
        print(f"   - NAS is online and reachable")
        print(f"   - TrueNAS web interface is accessible")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    test_api()
