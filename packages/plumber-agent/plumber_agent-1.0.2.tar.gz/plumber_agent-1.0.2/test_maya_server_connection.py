"""
Test Maya Server Connection
Run this from native Windows PowerShell to test if Maya server is reachable.
"""

import requests
import time

print("Testing Maya Persistent Server Connection")
print("=" * 60)

server_url = "http://127.0.0.1:8766"

print(f"\nTesting connection to: {server_url}/health")
print("Attempting 10 health checks with 1 second intervals...")
print()

for i in range(10):
    try:
        print(f"Attempt {i+1}/10... ", end="", flush=True)
        response = requests.get(f"{server_url}/health", timeout=2)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS!")
            print()
            print("Server Response:")
            print(f"  Status: {data.get('status')}")
            print(f"  Maya Version: {data.get('maya_version')}")
            print(f"  Active Sessions: {data.get('active_sessions')}")
            print()
            print("🎉 Maya persistent server is working correctly!")
            exit(0)
        else:
            print(f"❌ HTTP {response.status_code}")

    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection refused")
    except requests.exceptions.Timeout:
        print(f"❌ Timeout")
    except Exception as e:
        print(f"❌ Error: {e}")

    if i < 9:  # Don't sleep after last attempt
        time.sleep(1)

print()
print("=" * 60)
print("⚠️  All connection attempts failed!")
print()
print("Troubleshooting:")
print("1. Check if Maya server process is running:")
print("   Get-Process | Where-Object {$_.ProcessName -like '*maya*'}")
print()
print("2. Check if port 8766 is in use:")
print("   netstat -an | findstr 8766")
print()
print("3. Check Maya server log:")
print("   Get-Content maya_server_http.log -Tail 20")
print()
print("4. Make sure you're running this from native Windows (not WSL)")
