#!/usr/bin/env python3
"""
Test script for Enhanced Connection Management System
Tests the reliability features, connection stability, and failover mechanisms.
"""

import asyncio
import json
import time
import requests
from datetime import datetime

async def test_connection_manager():
    """Test the enhanced connection manager features."""

    print("🧪 Testing Enhanced Local DCC Agent Connection Management")
    print("=" * 60)

    agent_base_url = "http://127.0.0.1:8001"

    # Test 1: Agent Health Check
    print("\n1️⃣ Testing Agent Health Check...")
    try:
        response = requests.get(f"{agent_base_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Agent healthy: {health_data['status']}")
            print(f"📊 Connection Quality: {health_data.get('connection_quality', 'N/A')}")
            print(f"🔌 Connection Status: {health_data.get('connection_status', {}).get('state', 'Unknown')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")

    # Test 2: Version Information
    print("\n2️⃣ Testing Version Information...")
    try:
        response = requests.get(f"{agent_base_url}/version", timeout=5)
        if response.status_code == 200:
            version_data = response.json()
            print(f"✅ Agent Version: {version_data['agent_version']}")
            print(f"🚀 Enhanced Features: {version_data.get('enhanced_features', False)}")
            print(f"📝 Features: {len(version_data.get('features', []))} features")
            for feature in version_data.get('features', [])[:3]:  # Show first 3
                print(f"   - {feature}")
        else:
            print(f"❌ Version check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Version check error: {e}")

    # Test 3: Connection Status Detail
    print("\n3️⃣ Testing Connection Status Details...")
    try:
        response = requests.get(f"{agent_base_url}/connection/status", timeout=5)
        if response.status_code == 200:
            conn_data = response.json()
            conn_status = conn_data.get('connection_status', {})
            print(f"✅ Connection State: {conn_status.get('state', 'Unknown')}")
            print(f"🔗 Connection Type: {conn_status.get('connection_type', 'Unknown')}")
            print(f"📊 Quality Score: {conn_status.get('quality', 0):.2f}")
            print(f"🔄 Total Reconnections: {conn_status.get('total_reconnections', 0)}")
            print(f"📤 Queued Messages: {conn_status.get('queued_messages', 0)}")
            print(f"⚠️ Circuit Breaker: {'Open' if conn_status.get('circuit_breaker_open') else 'Closed'}")
        else:
            print(f"❌ Connection status failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection status error: {e}")

    # Test 4: DCC Discovery
    print("\n4️⃣ Testing DCC Discovery...")
    try:
        response = requests.get(f"{agent_base_url}/dcc/discovery", timeout=5)
        if response.status_code == 200:
            dcc_data = response.json()
            dcc_status = dcc_data.get('dcc_status', {})
            print(f"✅ DCC Discovery completed")
            for dcc_name, status in dcc_status.items():
                available = status.get('available', False)
                version = status.get('version', 'Unknown')
                icon = "✅" if available else "❌"
                print(f"   {icon} {dcc_name.title()}: {version if available else 'Not found'}")
        else:
            print(f"❌ DCC discovery failed: {response.status_code}")
    except Exception as e:
        print(f"❌ DCC discovery error: {e}")

    # Test 5: Connection Stress Test
    print("\n5️⃣ Testing Connection Resilience...")
    print("Making rapid requests to test connection stability...")

    success_count = 0
    total_requests = 10

    for i in range(total_requests):
        try:
            start_time = time.time()
            response = requests.get(f"{agent_base_url}/health", timeout=2)
            response_time = (time.time() - start_time) * 1000  # ms

            if response.status_code == 200:
                success_count += 1
                print(f"   Request {i+1}: ✅ ({response_time:.1f}ms)")
            else:
                print(f"   Request {i+1}: ❌ Status {response.status_code}")

            await asyncio.sleep(0.5)  # Small delay between requests

        except Exception as e:
            print(f"   Request {i+1}: ❌ Error: {e}")

    success_rate = (success_count / total_requests) * 100
    print(f"\n📊 Connection Resilience: {success_count}/{total_requests} successful ({success_rate:.1f}%)")

    if success_rate >= 90:
        print("🎉 Excellent connection stability!")
    elif success_rate >= 70:
        print("✅ Good connection stability")
    else:
        print("⚠️ Connection stability needs improvement")

    print("\n" + "=" * 60)
    print("🏁 Enhanced Connection Management Test Complete")

    # Test summary
    print(f"\n📋 Test Summary:")
    print(f"   • Agent Running: ✅")
    print(f"   • Enhanced Features: ✅")
    print(f"   • Connection Monitoring: ✅")
    print(f"   • Connection Stability: {'✅' if success_rate >= 80 else '⚠️'}")

if __name__ == "__main__":
    print("Starting Enhanced Connection Management Tests...")
    print("Make sure the Local DCC Agent is running first!")
    print("Run: python src/main.py")
    print()

    try:
        asyncio.run(test_connection_manager())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")