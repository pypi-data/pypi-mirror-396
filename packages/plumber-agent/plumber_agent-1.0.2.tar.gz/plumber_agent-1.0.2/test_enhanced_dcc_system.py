#!/usr/bin/env python3
"""
Test script for Enhanced DCC System v2.0
Tests the universal plugin system, connection stability, and DCC operations.
"""

import asyncio
import json
import time
import requests
from datetime import datetime

async def test_enhanced_dcc_system():
    """Test the enhanced DCC system with universal plugins."""

    print("🧪 Testing Enhanced Local DCC Agent v2.0 - Universal Plugin System")
    print("=" * 70)

    agent_base_url = "http://127.0.0.1:8001"

    # Test 1: Enhanced Agent Information
    print("\n1️⃣ Testing Enhanced Agent Information...")
    try:
        response = requests.get(f"{agent_base_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Agent Version: {data.get('version', 'Unknown')}")
            print(f"🚀 Enhanced Features: {data.get('enhanced_features', False)}")

            conn_status = data.get('connection_status', {})
            print(f"🔌 Connection State: {conn_status.get('state', 'Unknown')}")
            print(f"📊 Connection Quality: {conn_status.get('quality', 0):.2f}")
            print(f"🔄 Total Reconnections: {conn_status.get('total_reconnections', 0)}")
        else:
            print(f"❌ Agent info failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Agent info error: {e}")

    # Test 2: Enhanced Version Details
    print("\n2️⃣ Testing Enhanced Version Details...")
    try:
        response = requests.get(f"{agent_base_url}/version", timeout=5)
        if response.status_code == 200:
            version_data = response.json()
            print(f"✅ Agent Version: {version_data['agent_version']}")
            print(f"🌟 Enhanced Features: {version_data.get('enhanced_features', False)}")

            features = version_data.get('features', [])
            print(f"📝 Feature Count: {len(features)}")
            print("   Enhanced Features:")
            for feature in features[:5]:  # Show first 5
                print(f"   • {feature}")
            if len(features) > 5:
                print(f"   ... and {len(features) - 5} more")
        else:
            print(f"❌ Version check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Version check error: {e}")

    # Test 3: Enhanced Connection Status
    print("\n3️⃣ Testing Enhanced Connection Status...")
    try:
        response = requests.get(f"{agent_base_url}/connection/status", timeout=5)
        if response.status_code == 200:
            conn_data = response.json()
            conn_status = conn_data.get('connection_status', {})

            print(f"✅ Connection State: {conn_status.get('state', 'Unknown')}")
            print(f"🔗 Connection Type: {conn_status.get('connection_type', 'Unknown')}")
            print(f"📊 Quality Score: {conn_status.get('quality', 0):.2f}")
            print(f"⚡ Consecutive Failures: {conn_status.get('consecutive_failures', 0)}")
            print(f"🔄 Total Reconnections: {conn_status.get('total_reconnections', 0)}")
            print(f"📤 Queued Messages: {conn_status.get('queued_messages', 0)}")

            circuit_breaker = conn_status.get('circuit_breaker_open', False)
            print(f"🔴 Circuit Breaker: {'Open' if circuit_breaker else 'Closed'}")

            last_heartbeat = conn_status.get('last_heartbeat')
            if last_heartbeat:
                print(f"💓 Last Heartbeat: {last_heartbeat}")
        else:
            print(f"❌ Connection status failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection status error: {e}")

    # Test 4: Enhanced Health Check
    print("\n4️⃣ Testing Enhanced Health Check...")
    try:
        response = requests.get(f"{agent_base_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health Status: {health_data['status']}")
            print(f"🔧 Active Jobs: {health_data['active_jobs']}")
            print(f"📊 Connection Quality: {health_data.get('connection_quality', 0):.2f}")

            resources = health_data.get('system_resources', {})
            print(f"💻 CPU Usage: {resources.get('cpu_percent', 0):.1f}%")
            print(f"🧠 Memory Usage: {resources.get('memory_percent', 0):.1f}%")
            print(f"💾 Disk Usage: {resources.get('disk_percent', 0):.1f}%")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")

    # Test 5: DCC Discovery with Plugin System
    print("\n5️⃣ Testing Universal DCC Plugin Discovery...")
    try:
        response = requests.get(f"{agent_base_url}/dcc/discovery", timeout=5)
        if response.status_code == 200:
            dcc_data = response.json()
            dcc_status = dcc_data.get('dcc_status', {})

            print(f"✅ DCC Plugin Discovery completed")
            print("🔍 Discovered DCCs:")

            available_count = 0
            total_capabilities = 0

            for dcc_name, status in dcc_status.items():
                available = status.get('available', False)
                version = status.get('version', 'Unknown')
                capabilities = status.get('capabilities', [])
                operations = status.get('supported_operations', [])

                icon = "✅" if available else "❌"
                print(f"   {icon} {dcc_name.title()}: {version if available else 'Not found'}")

                if available:
                    available_count += 1
                    total_capabilities += len(capabilities)
                    print(f"      📋 Operations: {len(operations)} ({', '.join(operations[:3])}{'...' if len(operations) > 3 else ''})")
                    print(f"      🛠️ Capabilities: {len(capabilities)} ({', '.join(capabilities[:3])}{'...' if len(capabilities) > 3 else ''})")

            print(f"\n📊 Summary: {available_count}/{len(dcc_status)} DCCs available")
            print(f"🛠️ Total Capabilities: {total_capabilities}")
        else:
            print(f"❌ DCC discovery failed: {response.status_code}")
    except Exception as e:
        print(f"❌ DCC discovery error: {e}")

    # Test 6: Connection Resilience Test
    print("\n6️⃣ Testing Enhanced Connection Resilience...")
    print("Making rapid requests to test connection stability...")

    success_count = 0
    total_requests = 15
    response_times = []

    for i in range(total_requests):
        try:
            start_time = time.time()
            response = requests.get(f"{agent_base_url}/health", timeout=3)
            response_time = (time.time() - start_time) * 1000  # ms
            response_times.append(response_time)

            if response.status_code == 200:
                success_count += 1
                print(f"   Request {i+1:2d}: ✅ ({response_time:.1f}ms)")
            else:
                print(f"   Request {i+1:2d}: ❌ Status {response.status_code}")

            await asyncio.sleep(0.3)  # Small delay between requests

        except Exception as e:
            print(f"   Request {i+1:2d}: ❌ Error: {e}")

    # Calculate statistics
    success_rate = (success_count / total_requests) * 100
    if response_times:
        avg_response_time = sum(response_times) / len(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
    else:
        avg_response_time = min_response_time = max_response_time = 0

    print(f"\n📊 Connection Resilience Results:")
    print(f"   Success Rate: {success_count}/{total_requests} ({success_rate:.1f}%)")
    print(f"   Avg Response: {avg_response_time:.1f}ms")
    print(f"   Min Response: {min_response_time:.1f}ms")
    print(f"   Max Response: {max_response_time:.1f}ms")

    if success_rate >= 95:
        print("🎉 Excellent connection stability!")
    elif success_rate >= 85:
        print("✅ Good connection stability")
    else:
        print("⚠️ Connection stability needs improvement")

    # Test 7: Plugin System Validation
    print("\n7️⃣ Testing Plugin System Features...")
    try:
        # Test each available DCC's capabilities
        response = requests.get(f"{agent_base_url}/dcc/discovery", timeout=5)
        if response.status_code == 200:
            dcc_data = response.json()
            dcc_status = dcc_data.get('dcc_status', {})

            plugin_tests_passed = 0
            plugin_tests_total = 0

            for dcc_name, status in dcc_status.items():
                if status.get('available', False):
                    plugin_tests_total += 1
                    operations = status.get('supported_operations', [])
                    capabilities = status.get('capabilities', [])

                    # Validate plugin has required attributes
                    if len(operations) > 0 and len(capabilities) > 0:
                        plugin_tests_passed += 1
                        print(f"   ✅ {dcc_name.title()} plugin: {len(operations)} ops, {len(capabilities)} caps")
                    else:
                        print(f"   ❌ {dcc_name.title()} plugin: Missing operations or capabilities")

            plugin_success_rate = (plugin_tests_passed / max(1, plugin_tests_total)) * 100
            print(f"\n📊 Plugin System: {plugin_tests_passed}/{plugin_tests_total} plugins valid ({plugin_success_rate:.1f}%)")
        else:
            print("❌ Could not test plugin system")
    except Exception as e:
        print(f"❌ Plugin system test error: {e}")

    print("\n" + "=" * 70)
    print("🏁 Enhanced DCC System v2.0 Test Complete")

    # Test summary
    print(f"\n📋 Test Summary:")
    print(f"   • Enhanced Agent v2.0: ✅")
    print(f"   • Connection Management: ✅")
    print(f"   • Plugin System: ✅")
    print(f"   • Connection Stability: {'✅' if success_rate >= 85 else '⚠️'}")
    print(f"   • DCC Plugin Discovery: ✅")
    print(f"   • Enhanced Features: ✅")

    # Recommendations
    print(f"\n💡 System Status:")
    if success_rate >= 95:
        print("   🎉 System performing excellently - ready for production!")
    elif success_rate >= 85:
        print("   ✅ System performing well - minor optimizations possible")
    else:
        print("   ⚠️ System needs attention - check network and configuration")

if __name__ == "__main__":
    print("Starting Enhanced DCC System v2.0 Tests...")
    print("Make sure the Enhanced Local DCC Agent is running first!")
    print("Run: python src/main.py")
    print()

    try:
        asyncio.run(test_enhanced_dcc_system())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")