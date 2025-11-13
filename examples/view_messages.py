"""
View messages in the OmniSync Hub
Useful for debugging and testing
"""

import asyncio
import sys
import os
import requests
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sdk', 'python'))

HUB_URL = "http://localhost:8080"


def view_all_messages(limit=50):
    """View all messages in the hub"""
    try:
        response = requests.get(f"{HUB_URL}/api/messages?limit={limit}")
        if response.status_code == 200:
            data = response.json()
            messages = data.get("messages", [])
            print(f"\n📨 Total Messages: {len(messages)}\n")
            print("=" * 80)
            for msg in messages:
                print(f"\n🆔 ID: {msg.get('id', 'N/A')[:8]}...")
                print(f"📤 From: {msg.get('from', 'N/A')}")
                print(f"📥 To: {msg.get('to', 'N/A')}")
                print(f"🎯 Intent: {msg.get('intent', 'N/A')}")
                print(f"⏰ Time: {msg.get('timestamp', 'N/A')}")
                if msg.get('response_to'):
                    print(f"↩️  Response to: {msg.get('response_to', 'N/A')[:8]}...")
                print(f"📝 Content: {msg.get('content', {})}")
                print("-" * 80)
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error connecting to hub: {e}")
        print(f"   Make sure the hub is running at {HUB_URL}")


def view_agents():
    """View all registered agents"""
    try:
        response = requests.get(f"{HUB_URL}/api/agents")
        if response.status_code == 200:
            data = response.json()
            agents = data.get("agents", [])
            print(f"\n🤖 Registered Agents: {len(agents)}\n")
            print("=" * 80)
            for agent in agents:
                print(f"\n🆔 ID: {agent.get('agent_id', 'N/A')}")
                print(f"📛 Name: {agent.get('name', 'N/A')}")
                print(f"🔧 Framework: {agent.get('framework', 'N/A')}")
                print(f"💪 Capabilities: {agent.get('capabilities', [])}")
                if agent.get('model'):
                    print(f"🧠 Model: {agent.get('model')}")
                print("-" * 80)
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error connecting to hub: {e}")


def view_stats():
    """View hub statistics"""
    try:
        response = requests.get(f"{HUB_URL}/api/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"\n📊 Hub Statistics\n")
            print("=" * 80)
            print(f"📨 Total Messages: {stats.get('total_messages', 0)}")
            print(f"🤖 Total Agents: {stats.get('total_agents', 0)}")
            print(f"\n📈 Messages by Intent:")
            intent_counts = stats.get('intent_counts', {})
            for intent, count in intent_counts.items():
                print(f"   {intent}: {count}")
            print("=" * 80)
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error connecting to hub: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="View OmniSync Hub messages and stats")
    parser.add_argument("--messages", action="store_true", help="View all messages")
    parser.add_argument("--agents", action="store_true", help="View registered agents")
    parser.add_argument("--stats", action="store_true", help="View hub statistics")
    parser.add_argument("--limit", type=int, default=50, help="Limit number of messages")
    parser.add_argument("--all", action="store_true", help="Show everything")
    
    args = parser.parse_args()
    
    if args.all or (not args.messages and not args.agents and not args.stats):
        view_stats()
        view_agents()
        view_all_messages(args.limit)
    else:
        if args.stats:
            view_stats()
        if args.agents:
            view_agents()
        if args.messages:
            view_all_messages(args.limit)

