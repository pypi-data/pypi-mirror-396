#!/usr/bin/env python3
"""
Local DCC Agent Version Checker
Quick script to check if your local agent is the latest version.
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime

async def check_agent_version():
    """Check local agent version and compare with backend."""

    print("🔍 Checking Local DCC Agent Version...")
    print("=" * 50)

    # Check if local agent is running
    try:
        async with aiohttp.ClientSession() as session:
            # Check local agent
            print("📍 Checking local agent...")
            async with session.get("http://127.0.0.1:8001/version") as response:
                if response.status == 200:
                    local_info = await response.json()
                    print(f"✅ Local agent version: {local_info['agent_version']}")
                    print(f"📋 Features: {', '.join(local_info['features'])}")
                    print(f"🔗 Heartbeat support: {local_info['heartbeat_support']}")
                    print(f"📅 Last updated: {local_info['last_updated']}")
                else:
                    print(f"❌ Local agent not responding (status: {response.status})")
                    print("💡 Make sure your local agent is running on port 8001")
                    return

            print()

            # Check compatibility with Railway backend
            print("🌐 Checking Railway backend compatibility...")
            async with session.get("http://127.0.0.1:8001/version/check") as response:
                if response.status == 200:
                    check_info = await response.json()

                    if check_info['status'] == 'up-to-date':
                        print(f"✅ Status: {check_info['status'].upper()}")
                        print(f"🎯 Current version: {check_info['current_version']}")
                        print(f"🏗️  Backend version: {check_info['backend_version']}")
                        print(f"💓 Heartbeat compatible: {check_info['heartbeat_compatible']}")
                        print("\n🎉 Your local agent is up to date!")

                    elif check_info['status'] == 'update-available':
                        print(f"⚠️  Status: {check_info['status'].upper()}")
                        print(f"🎯 Current version: {check_info['current_version']}")
                        print(f"📥 Latest version: Available")
                        print("\n🔄 Update recommended!")

                    elif check_info['status'] == 'check-failed':
                        print(f"❌ Status: {check_info['status'].upper()}")
                        print(f"🚨 Error: {check_info.get('error', 'Unknown error')}")
                        print(f"🎯 Current version: {check_info['current_version']}")
                        print("\n💡 Backend check failed, but local agent appears to be v1.1.0")

                else:
                    print(f"❌ Version check failed (status: {response.status})")

    except aiohttp.ClientConnectorError:
        print("❌ Cannot connect to local agent")
        print("💡 Make sure your local DCC agent is running:")
        print("   1. Navigate to local-dcc-agent directory")
        print("   2. Run: start_agent.bat (Windows) or python src/main.py")
        print("   3. Agent should be available at http://127.0.0.1:8001")

    except Exception as e:
        print(f"❌ Unexpected error: {e}")

async def check_agent_connection():
    """Quick connection test to local agent."""
    print("\n🔌 Testing connection to local agent...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://127.0.0.1:8001/health") as response:
                if response.status == 200:
                    health_info = await response.json()
                    print(f"✅ Agent status: {health_info['status']}")
                    print(f"⏱️  Uptime: {health_info['uptime']:.1f} seconds")
                    print(f"🔧 Active jobs: {health_info['active_jobs']}")

                    # Check Railway connection
                    async with session.get("http://127.0.0.1:8001/") as root_response:
                        if root_response.status == 200:
                            root_info = await root_response.json()
                            print(f"🔗 Agent ID: {root_info['agent_id'][:8]}...")
                            print(f"💓 Heartbeat support: {root_info.get('heartbeat_support', 'Unknown')}")

                else:
                    print(f"❌ Health check failed (status: {response.status})")

    except Exception as e:
        print(f"❌ Connection test failed: {e}")

def main():
    """Main entry point."""
    print("🎭 Plumber Local DCC Agent - Version Checker")
    print(f"📅 Check time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    try:
        # Run version check
        asyncio.run(check_agent_version())

        # Run connection test
        asyncio.run(check_agent_connection())

        print("\n" + "=" * 50)
        print("✅ Version check complete!")
        print("\n💡 Quick reference:")
        print("   • Latest version: v1.1.0 (Enhanced heartbeat support)")
        print("   • Check agent: http://127.0.0.1:8001/version")
        print("   • Check health: http://127.0.0.1:8001/health")
        print("   • Agent info: http://127.0.0.1:8001/")

    except KeyboardInterrupt:
        print("\n❌ Check cancelled by user")
    except Exception as e:
        print(f"\n❌ Check failed: {e}")

if __name__ == "__main__":
    main()