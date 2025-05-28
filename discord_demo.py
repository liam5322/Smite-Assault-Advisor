#!/usr/bin/env python3
"""
🎮 SMITE 2 Assault Brain - Discord Demo
Perfect for showing your Discord mates the power of AI-powered Assault analysis!
"""

import json
import time
import requests
from datetime import datetime

class DiscordAssaultDemo:
    def __init__(self, server_url="http://localhost:9000"):
        self.server_url = server_url
        self.demo_scenarios = self.create_demo_scenarios()
    
    def create_demo_scenarios(self):
        """Create impressive demo scenarios for Discord"""
        return [
            {
                "name": "🔥 THE HEALER NIGHTMARE",
                "description": "Enemy team has double healers - watch the AI prioritize anti-heal!",
                "team1": ["Zeus", "Ares", "Neith", "Thor", "Ymir"],
                "team2": ["Aphrodite", "Ra", "Kukulkan", "Geb", "Artemis"],
                "expected": "Priority 10 anti-heal items"
            },
            {
                "name": "⚡ THE HUNTER META",
                "description": "Multiple hunters vs balanced comp - see the counter-building magic!",
                "team1": ["Zeus", "Ares", "Sobek", "Anubis", "Ymir"],
                "team2": ["Artemis", "Neith", "Apollo", "Geb", "Janus"],
                "expected": "Spectral Armor recommendations"
            },
            {
                "name": "🎯 THE CC LOCKDOWN",
                "description": "Ares + Ymir combo - AI knows you need beads!",
                "team1": ["Zeus", "Kukulkan", "Neith", "Thor", "Bacchus"],
                "team2": ["Ares", "Ymir", "Artemis", "Ra", "Fenrir"],
                "expected": "Purification Beads priority"
            },
            {
                "name": "🧠 THE BALANCED MATCH",
                "description": "Even teams - watch the AI calculate win probabilities!",
                "team1": ["Zeus", "Ares", "Neith", "Ra", "Ymir"],
                "team2": ["Poseidon", "Sobek", "Apollo", "Anubis", "Thor"],
                "expected": "Balanced analysis with strategic advice"
            },
            {
                "name": "❌ THE INVALID GODS TEST",
                "description": "Try using SMITE 1 gods - see the smart validation!",
                "team1": ["Zeus", "Ares", "Neith", "Ra", "Ymir"],
                "team2": ["Scylla", "Hel", "Loki", "Thor", "Sobek"],
                "expected": "Error with helpful god suggestions"
            }
        ]
    
    def format_discord_embed(self, scenario, result):
        """Format analysis as Discord embed JSON"""
        if "error" in result:
            # Error case - show validation
            embed = {
                "title": f"{scenario['name']} - Validation Demo",
                "description": f"🛡️ **SMITE 2 Validation Active**\n{result['error']}",
                "color": 0xff4444,
                "fields": [
                    {
                        "name": "✅ Valid SMITE 2 Gods (Examples)",
                        "value": ", ".join(result.get('valid_gods', [])[:8]),
                        "inline": False
                    },
                    {
                        "name": "📊 Total Gods Available",
                        "value": f"{result.get('total_gods', 27)} confirmed SMITE 2 gods",
                        "inline": True
                    }
                ],
                "footer": {"text": "SMITE 2 Assault Brain - Keeping it accurate! 🎮"}
            }
        else:
            # Success case - show analysis
            win_rate = f"{result['win_probability']:.1%}"
            embed = {
                "title": f"{scenario['name']} - Analysis Complete",
                "description": f"🎯 **Win Probability: {win_rate}**\n{scenario['description']}",
                "color": 0x00ff88,
                "fields": [
                    {
                        "name": "🔥 Priority Items (Assault Meta)",
                        "value": "\n".join(result.get('item_priorities', ['No specific recommendations'])),
                        "inline": False
                    },
                    {
                        "name": "⚡ Strategic Advice",
                        "value": "\n".join(result.get('key_advice', ['Play smart!'])),
                        "inline": False
                    },
                    {
                        "name": "⏱️ Analysis Speed",
                        "value": f"{result.get('analysis_time_ms', 0):.1f}ms",
                        "inline": True
                    },
                    {
                        "name": "🎮 Game Mode",
                        "value": "Assault (5v5)",
                        "inline": True
                    }
                ],
                "footer": {"text": f"SMITE 2 Assault Brain - {datetime.now().strftime('%H:%M:%S')}"}
            }
        
        return {
            "content": f"🎮 **SMITE 2 Assault Analysis Demo**",
            "embeds": [embed]
        }
    
    def run_analysis(self, team1, team2):
        """Run analysis via API"""
        try:
            response = requests.post(
                f"{self.server_url}/api/analyze",
                json={"team1": team1, "team2": team2},
                timeout=10
            )
            return response.json()
        except Exception as e:
            return {"error": f"Connection failed: {e}"}
    
    def demo_scenario(self, scenario_index):
        """Run a specific demo scenario"""
        if scenario_index >= len(self.demo_scenarios):
            return None
        
        scenario = self.demo_scenarios[scenario_index]
        print(f"\n🎮 Running: {scenario['name']}")
        print(f"📝 {scenario['description']}")
        print(f"👥 Team 1: {', '.join(scenario['team1'])}")
        print(f"👥 Team 2: {', '.join(scenario['team2'])}")
        print("⏳ Analyzing...")
        
        start_time = time.time()
        result = self.run_analysis(scenario['team1'], scenario['team2'])
        analysis_time = (time.time() - start_time) * 1000
        
        print(f"✅ Complete in {analysis_time:.1f}ms")
        
        # Create Discord embed
        discord_embed = self.format_discord_embed(scenario, result)
        
        return {
            "scenario": scenario,
            "result": result,
            "discord_embed": discord_embed,
            "analysis_time": analysis_time
        }
    
    def run_full_demo(self):
        """Run all demo scenarios"""
        print("🎮 SMITE 2 Assault Brain - Discord Demo")
        print("=" * 50)
        print("Perfect for impressing your Discord mates! 🚀")
        
        results = []
        for i, scenario in enumerate(self.demo_scenarios):
            demo_result = self.demo_scenario(i)
            if demo_result:
                results.append(demo_result)
                time.sleep(1)  # Brief pause between demos
        
        return results
    
    def generate_webhook_examples(self, results):
        """Generate webhook examples for Discord"""
        print("\n🔗 DISCORD WEBHOOK EXAMPLES")
        print("=" * 50)
        print("Copy these to send to your Discord channel:\n")
        
        for i, result in enumerate(results):
            print(f"# Example {i+1}: {result['scenario']['name']}")
            print("```python")
            print("import requests")
            print()
            print("webhook_url = 'YOUR_DISCORD_WEBHOOK_URL'")
            print("data = " + json.dumps(result['discord_embed'], indent=2))
            print("requests.post(webhook_url, json=data)")
            print("```\n")
    
    def create_bot_command_demo(self):
        """Create example Discord bot commands"""
        print("\n🤖 DISCORD BOT COMMAND EXAMPLES")
        print("=" * 50)
        
        commands = [
            "!assault Zeus Ares Neith Ra Ymir vs Artemis Fenrir Kukulkan Geb Janus",
            "!assault analyze Aphrodite Ra Sobek Anubis Thor vs Zeus Ares Neith Apollo Ymir",
            "!assault quick Zeus Poseidon vs Artemis Neith",
            "!assault gods",  # List valid gods
            "!assault help"   # Show help
        ]
        
        for cmd in commands:
            print(f"💬 {cmd}")
        
        print("\n📝 Bot Response Example:")
        print("```")
        print("🎮 SMITE 2 Assault Analysis")
        print("Win Rate: 67% (Medium Confidence)")
        print()
        print("🔥 Priority Items:")
        print("• Divine Ruin (2050g) - Priority 10")
        print("• Meditation Cloak (0g) - Priority 9") 
        print("• Spectral Armor (2100g) - Priority 7")
        print()
        print("⚡ Key Advice:")
        print("• Anti-heal is MANDATORY vs Aphrodite/Ra")
        print("• Focus the healers in team fights")
        print("• Meditation timing is crucial")
        print()
        print("⏱️ Analysis: 1.2ms | 🎮 Mode: Assault")
        print("```")

def main():
    """Run the Discord demo"""
    demo = DiscordAssaultDemo()
    
    print("🚀 Starting SMITE 2 Assault Brain Demo...")
    print("Make sure the web server is running on localhost:9000")
    
    # Test connection
    try:
        response = requests.get("http://localhost:9000", timeout=5)
        print("✅ Server connection successful!")
    except:
        print("❌ Server not running! Start with: python web_demo.py")
        return
    
    # Run full demo
    results = demo.run_full_demo()
    
    # Generate Discord examples
    demo.generate_webhook_examples(results)
    demo.create_bot_command_demo()
    
    print("\n🎉 Demo Complete!")
    print("Your Discord mates will be impressed! 🎮✨")
    print("\nNext steps:")
    print("1. Copy webhook examples to your Discord")
    print("2. Set up a Discord bot with these commands")
    print("3. Share the web interface: http://localhost:9000")

if __name__ == "__main__":
    main()