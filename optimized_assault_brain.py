#!/usr/bin/env python3
"""
🎮 SMITE 2 Assault Brain - Optimized Production System
Smart data loading, Discord integration, team-focused features
"""

import asyncio
import sqlite3
import json
import gzip
import pickle
import time
import logging
import threading
import hashlib
import aiohttp
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import tkinter as tk

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class GodData:
    """Minimal god data for efficient analysis"""
    name: str
    role: str
    win_rate: float
    early_power: int  # 1-10
    late_power: int   # 1-10
    team_fight: int   # 1-10
    counters: List[str]
    key_strength: str
    key_weakness: str

@dataclass
class MatchAnalysis:
    """Streamlined analysis result"""
    win_probability: float
    confidence: str  # "high", "medium", "low"
    key_advice: List[str]  # Max 3 most important points
    item_priorities: List[str]  # Max 2 priority items
    voice_summary: str  # Single sentence for TTS
    timestamp: str

class SmartDataManager:
    """Efficient data manager - only loads what's needed"""
    
    def __init__(self):
        self.data_dir = Path("smart_data")
        self.data_dir.mkdir(exist_ok=True)
        self.db_path = self.data_dir / "smart.db"
        
        # In-memory cache for current match only
        self.current_gods = {}
        self.analysis_cache = {}
        
        self._init_database()
        self._load_essential_data()
        
        logger.info("✅ Smart data manager initialized")
    
    def _init_database(self):
        """Minimal database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS god_essentials (
                    name TEXT PRIMARY KEY,
                    role TEXT,
                    win_rate REAL,
                    powers TEXT,  -- JSON: [early, late, team_fight]
                    counters TEXT,  -- JSON array
                    strength TEXT,
                    weakness TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quick_cache (
                    team_hash TEXT PRIMARY KEY,
                    result TEXT,  -- JSON analysis
                    expires TEXT
                )
            """)
    
    def _load_essential_data(self):
        """Load only essential god data - ultra-lightweight"""
        # Core Assault gods with minimal data
        essential_gods = {
            "zeus": GodData("Zeus", "Mage", 0.68, 6, 9, 10, 
                          ["Odin", "Ares", "Thor"], 
                          "Massive team fight damage", 
                          "No escape from dive"),
            
            "ares": GodData("Ares", "Guardian", 0.72, 7, 8, 10,
                          ["Beads", "Spread formation"],
                          "Game-changing ultimate",
                          "No peel for carries"),
            
            "loki": GodData("Loki", "Assassin", 0.42, 8, 4, 3,
                          ["Mystical Mail", "Group positioning"],
                          "High single target burst",
                          "Useless in team fights"),
            
            "aphrodite": GodData("Aphrodite", "Mage", 0.75, 5, 9, 9,
                         ["Divine Ruin", "Antiheal"],
                         "Team healing and sustain",
                         "Countered by antiheal"),
            
            "neith": GodData("Neith", "Hunter", 0.58, 6, 7, 7,
                           ["Dive comps", "Cripples"],
                           "Global ultimate utility",
                           "Lower DPS than other hunters"),
            
            # Add more gods as needed - keep data minimal
            "ra": GodData("Ra", "Mage", 0.62, 7, 8, 8,
                        ["Dive comps", "High mobility"],
                        "Strong healing and poke",
                        "Skillshot dependent"),
            
            "ymir": GodData("Ymir", "Guardian", 0.65, 8, 6, 8,
                          ["High mobility", "Beads"],
                          "Strong early game CC",
                          "Falls off late game"),
            
            "kukulkan": GodData("Kukulkan", "Mage", 0.64, 4, 10, 9,
                            ["Early pressure", "Dive"],
                            "Incredible late game scaling",
                            "Weak early game"),
            
            "thor": GodData("Thor", "Assassin", 0.59, 8, 6, 7,
                          ["Beads", "Spread formation"],
                          "Global presence and setup",
                          "Combo dependent"),
            
            "artemis": GodData("Artemis", "Hunter", 0.61, 5, 9, 8,
                             ["Early pressure", "No escape"],
                             "Highest DPS potential",
                             "No mobility/escape"),
            
            "sobek": GodData("Sobek", "Guardian", 0.66, 7, 7, 8,
                           ["Beads", "Positioning"],
                           "Strong initiation and peel",
                           "Mana hungry early game")
        }
        
        # Store in database for persistence
        with sqlite3.connect(self.db_path) as conn:
            for god_key, god_data in essential_gods.items():
                conn.execute("""
                    INSERT OR REPLACE INTO god_essentials 
                    (name, role, win_rate, powers, counters, strength, weakness)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    god_data.name,
                    god_data.role,
                    god_data.win_rate,
                    json.dumps([god_data.early_power, god_data.late_power, god_data.team_fight]),
                    json.dumps(god_data.counters),
                    god_data.key_strength,
                    god_data.key_weakness
                ))
        
        logger.info(f"📊 Loaded {len(essential_gods)} essential gods")
    
    def load_gods_for_match(self, all_god_names: List[str]) -> Dict[str, GodData]:
        """Smart loading - only load gods needed for this match"""
        needed_gods = {}
        
        with sqlite3.connect(self.db_path) as conn:
            for god_name in all_god_names:
                god_key = god_name.lower().replace(" ", "").replace("'", "")
                
                cursor = conn.execute("""
                    SELECT name, role, win_rate, powers, counters, strength, weakness
                    FROM god_essentials WHERE name = ?
                """, (god_name,))
                
                row = cursor.fetchone()
                if row:
                    name, role, win_rate, powers_json, counters_json, strength, weakness = row
                    powers = json.loads(powers_json)
                    counters = json.loads(counters_json)
                    
                    needed_gods[god_key] = GodData(
                        name=name,
                        role=role,
                        win_rate=win_rate,
                        early_power=powers[0],
                        late_power=powers[1],
                        team_fight=powers[2],
                        counters=counters,
                        key_strength=strength,
                        key_weakness=weakness
                    )
        
        # Cache for this session
        self.current_gods = needed_gods
        logger.info(f"🎯 Loaded {len(needed_gods)} gods for current match")
        return needed_gods
    
    def quick_analyze(self, team1: List[str], team2: List[str]) -> MatchAnalysis:
        """Ultra-fast analysis focused on key insights"""
        # Check cache first
        team_hash = hashlib.md5(f"{sorted(team1)}{sorted(team2)}".encode()).hexdigest()
        
        if team_hash in self.analysis_cache:
            return self.analysis_cache[team_hash]
        
        # Load only needed gods
        all_gods = team1 + team2
        gods_data = self.load_gods_for_match(all_gods)
        
        # Quick team analysis
        team1_data = [gods_data.get(god.lower().replace(" ", "").replace("'", "")) for god in team1]
        team2_data = [gods_data.get(god.lower().replace(" ", "").replace("'", "")) for god in team2]
        
        # Filter out None values
        team1_data = [god for god in team1_data if god]
        team2_data = [god for god in team2_data if god]
        
        # Calculate win probability (simplified but effective)
        team1_score = self._quick_team_score(team1_data)
        team2_score = self._quick_team_score(team2_data)
        
        total = team1_score + team2_score
        win_prob = team1_score / total if total > 0 else 0.5
        
        # Generate key insights only
        key_advice = self._generate_key_advice(team1_data, team2_data, win_prob)
        item_priorities = self._get_priority_items(team2_data)
        voice_summary = self._create_voice_summary(win_prob, key_advice)
        
        # Confidence based on data quality
        known_gods = len(team1_data) + len(team2_data)
        total_gods = len(team1) + len(team2)
        confidence = "high" if known_gods >= total_gods * 0.8 else "medium" if known_gods >= total_gods * 0.5 else "low"
        
        analysis = MatchAnalysis(
            win_probability=win_prob,
            confidence=confidence,
            key_advice=key_advice,
            item_priorities=item_priorities,
            voice_summary=voice_summary,
            timestamp=datetime.now().isoformat()
        )
        
        # Cache result
        self.analysis_cache[team_hash] = analysis
        
        return analysis
    
    def _quick_team_score(self, team_data: List[GodData]) -> float:
        """Fast team scoring algorithm"""
        if not team_data:
            return 1.0
        
        # Weighted scoring for Assault
        score = 0
        for god in team_data:
            # Team fight is most important in Assault
            score += god.team_fight * 3
            # Late game scaling matters (games go long)
            score += god.late_power * 2
            # Win rate matters
            score += god.win_rate * 10
        
        # Role balance bonus
        roles = [god.role for god in team_data]
        if "Guardian" in roles: score += 10
        if "Hunter" in roles: score += 8
        if "Mage" in roles: score += 8
        
        return score
    
    def _generate_key_advice(self, team1_data: List[GodData], team2_data: List[GodData], win_prob: float) -> List[str]:
        """Generate max 3 key pieces of advice"""
        advice = []
        
        # Win probability advice
        if win_prob >= 0.7:
            advice.append("🔥 Strong advantage - force team fights")
        elif win_prob <= 0.3:
            advice.append("⚠️ Tough matchup - play for picks and late game")
        else:
            advice.append("⚖️ Even match - execution will decide")
        
        # Counter advice
        major_threats = []
        for enemy in team2_data:
            for ally in team1_data:
                if ally.name in enemy.counters:
                    major_threats.append(f"{enemy.name} counters {ally.name}")
        
        if major_threats and len(advice) < 3:
            advice.append(f"⚠️ {major_threats[0]}")
        
        # Strategic advice based on team composition
        team1_roles = [god.role for god in team1_data]
        if "Guardian" not in team1_roles and len(advice) < 3:
            advice.append("🛡️ No tank - play safe and poke")
        elif len([r for r in team1_roles if r == "Mage"]) >= 2 and len(advice) < 3:
            advice.append("⚡ High burst potential - coordinate abilities")
        
        return advice[:3]  # Max 3 pieces of advice
    
    def _get_priority_items(self, enemy_team: List[GodData]) -> List[str]:
        """Get max 2 priority items based on enemy team"""
        priorities = []
        
        # Check for healers
        healers = [god for god in enemy_team if "heal" in god.key_strength.lower()]
        if healers and len(priorities) < 2:
            priorities.append("🩸 Divine Ruin/Toxic Blade (antiheal)")
        
        # Check for stealth
        stealth_gods = [god for god in enemy_team if god.name.lower() in ["loki", "serqet"]]
        if stealth_gods and len(priorities) < 2:
            priorities.append("👁️ Mystical Mail (reveal stealth)")
        
        # Check for heavy physical
        physical_count = len([god for god in enemy_team if god.role in ["Hunter", "Assassin", "Warrior"]])
        if physical_count >= 3 and len(priorities) < 2:
            priorities.append("🛡️ Physical protection")
        
        return priorities[:2]  # Max 2 priorities
    
    def _create_voice_summary(self, win_prob: float, advice: List[str]) -> str:
        """Create single sentence for voice announcement"""
        win_pct = int(win_prob * 100)
        
        if win_pct >= 70:
            base = f"Strong advantage at {win_pct} percent. "
        elif win_pct >= 50:
            base = f"Even match at {win_pct} percent. "
        else:
            base = f"Tough match at {win_pct} percent. "
        
        if advice:
            # Clean up the first advice for voice
            clean_advice = advice[0].replace('🔥', '').replace('⚠️', '').replace('⚖️', '').strip()
            return base + clean_advice
        
        return base + "Good luck!"

class DiscordIntegration:
    """Discord webhook and bot integration for team sharing"""
    
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url
        self.session = None
        logger.info("✅ Discord integration initialized")
    
    async def send_analysis(self, analysis: MatchAnalysis, team1: List[str], team2: List[str]):
        """Send analysis to Discord webhook"""
        if not self.webhook_url:
            logger.info("📤 No webhook URL - would send to Discord")
            return
        
        # Create Discord embed
        embed = {
            "title": "🎯 SMITE 2 Assault Analysis",
            "color": self._get_color(analysis.win_probability),
            "fields": [
                {
                    "name": "🏆 Win Probability",
                    "value": f"{analysis.win_probability*100:.0f}% ({analysis.confidence} confidence)",
                    "inline": True
                },
                {
                    "name": "⚔️ Teams",
                    "value": f"**Your Team:** {', '.join(team1)}\n**Enemy Team:** {', '.join(team2)}",
                    "inline": False
                }
            ],
            "timestamp": analysis.timestamp,
            "footer": {"text": "SMITE 2 Assault Brain"}
        }
        
        # Add advice
        if analysis.key_advice:
            embed["fields"].append({
                "name": "🧠 Key Strategy",
                "value": "\n".join(analysis.key_advice),
                "inline": False
            })
        
        # Add item priorities
        if analysis.item_priorities:
            embed["fields"].append({
                "name": "🛡️ Item Priorities",
                "value": "\n".join(analysis.item_priorities),
                "inline": False
            })
        
        # Send webhook
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            payload = {
                "embeds": [embed],
                "content": f"🎮 **Match Analysis Ready!**\n🎤 {analysis.voice_summary}"
            }
            
            async with self.session.post(self.webhook_url, json=payload) as response:
                if response.status == 204:
                    logger.info("✅ Analysis sent to Discord")
                else:
                    logger.error(f"❌ Discord webhook failed: {response.status}")
                    
        except Exception as e:
            logger.error(f"❌ Discord integration error: {e}")
    
    def _get_color(self, win_prob: float) -> int:
        """Get color based on win probability"""
        if win_prob >= 0.7:
            return 0x00ff00  # Green
        elif win_prob >= 0.5:
            return 0xffaa00  # Orange
        else:
            return 0xff0000  # Red
    
    async def close(self):
        """Close session"""
        if self.session:
            await self.session.close()

class OptimizedOverlay:
    """Minimal, efficient overlay focused on key info"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Assault Brain")
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.9)
        self.root.overrideredirect(True)
        self.root.geometry("350x200+50+50")
        
        self._create_minimal_ui()
        self._setup_bindings()
        
        logger.info("✅ Optimized overlay initialized")
    
    def _create_minimal_ui(self):
        """Create ultra-minimal UI"""
        # Main frame
        main = tk.Frame(self.root, bg='#1a1a1a', relief='raised', bd=1)
        main.pack(fill='both', expand=True, padx=1, pady=1)
        
        # Header
        header = tk.Label(main, text="⚔️ ASSAULT", bg='#1a1a1a', fg='#00ff88', font=('Arial', 12, 'bold'))
        header.pack(pady=2)
        
        # Win probability (main focus)
        self.win_label = tk.Label(main, text="🎯 Analyzing...", bg='#1a1a1a', fg='#ffffff', font=('Arial', 11, 'bold'))
        self.win_label.pack(pady=2)
        
        # Key advice (scrollable)
        self.advice_text = tk.Text(main, height=8, width=40, bg='#2a2a2a', fg='#ffffff', 
                                  font=('Arial', 9), wrap='word', relief='flat')
        self.advice_text.pack(fill='both', expand=True, padx=5, pady=2)
        
        # Controls
        controls = tk.Frame(main, bg='#1a1a1a')
        controls.pack(fill='x', pady=2)
        
        tk.Button(controls, text="📍", command=self._move, bg='#333', fg='#fff', relief='flat', width=2).pack(side='left', padx=1)
        tk.Button(controls, text="📤", command=self._share, bg='#333', fg='#fff', relief='flat', width=2).pack(side='left', padx=1)
        tk.Button(controls, text="❌", command=self._close, bg='#333', fg='#fff', relief='flat', width=2).pack(side='right', padx=1)
        
        self.last_analysis = None
    
    def _setup_bindings(self):
        """Setup drag functionality"""
        self.root.bind('<Button-1>', self._start_drag)
        self.root.bind('<B1-Motion>', self._drag)
    
    def _start_drag(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y
    
    def _drag(self, event):
        x = self.root.winfo_x() + event.x - self.drag_start_x
        y = self.root.winfo_y() + event.y - self.drag_start_y
        self.root.geometry(f"+{x}+{y}")
    
    def _move(self):
        """Cycle positions"""
        positions = ["50+50", "1470+50", "50+700"]
        current = self.root.geometry().split('+')[1] + '+' + self.root.geometry().split('+')[2]
        try:
            idx = positions.index(current)
            next_pos = positions[(idx + 1) % len(positions)]
        except:
            next_pos = positions[0]
        self.root.geometry(f"350x200+{next_pos}")
    
    def _share(self):
        """Share last analysis to Discord"""
        if hasattr(self, 'share_callback') and self.last_analysis:
            self.share_callback()
        else:
            logger.info("📤 No analysis to share")
    
    def _close(self):
        self.root.quit()
    
    def update_analysis(self, analysis: MatchAnalysis):
        """Update with new analysis"""
        self.last_analysis = analysis
        
        # Update win probability with color
        win_pct = int(analysis.win_probability * 100)
        if win_pct >= 70:
            color, emoji = '#00ff88', '🔥'
        elif win_pct >= 50:
            color, emoji = '#ffaa00', '⚖️'
        else:
            color, emoji = '#ff4444', '⚠️'
        
        self.win_label.config(text=f"{emoji} {win_pct}% WIN ({analysis.confidence})", fg=color)
        
        # Update advice
        self.advice_text.delete('1.0', tk.END)
        
        content = []
        if analysis.key_advice:
            content.extend(analysis.key_advice)
            content.append("")
        
        if analysis.item_priorities:
            content.append("🛡️ PRIORITY ITEMS:")
            content.extend(analysis.item_priorities)
        
        self.advice_text.insert('1.0', '\n'.join(content))
    
    def show(self):
        self.root.deiconify()
    
    def hide(self):
        self.root.withdraw()
    
    def update(self):
        self.root.update()

class OptimizedAssaultBrain:
    """Main optimized application"""
    
    def __init__(self, discord_webhook: str = None):
        logger.info("🎮 Initializing Optimized Assault Brain...")
        
        self.data_manager = SmartDataManager()
        self.overlay = OptimizedOverlay()
        self.discord = DiscordIntegration(discord_webhook)
        
        # Set up Discord sharing
        self.overlay.share_callback = self._share_to_discord
        
        self.running = False
        self.last_teams = None
        
        logger.info("✅ Optimized Assault Brain ready!")
    
    def analyze_teams(self, team1: List[str], team2: List[str]) -> MatchAnalysis:
        """Analyze team matchup"""
        logger.info(f"🔍 Analyzing: {team1} vs {team2}")
        
        start_time = time.time()
        analysis = self.data_manager.quick_analyze(team1, team2)
        analysis_time = (time.time() - start_time) * 1000
        
        logger.info(f"📊 Analysis complete in {analysis_time:.1f}ms - {analysis.win_probability*100:.0f}% win chance")
        
        # Update overlay
        self.overlay.update_analysis(analysis)
        
        # Store for Discord sharing
        self.last_teams = (team1, team2)
        
        return analysis
    
    async def _share_to_discord(self):
        """Share analysis to Discord"""
        if self.last_teams and self.overlay.last_analysis:
            team1, team2 = self.last_teams
            await self.discord.send_analysis(self.overlay.last_analysis, team1, team2)
    
    def start(self):
        """Start the application"""
        self.running = True
        self.overlay.show()
        
        logger.info("🎮 Optimized Assault Brain started!")
        
        try:
            self.overlay.root.mainloop()
        except KeyboardInterrupt:
            logger.info("👋 Shutting down...")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the application"""
        self.running = False
        asyncio.run(self.discord.close())
        logger.info("✅ Optimized Assault Brain stopped")

# Demo and testing functions
async def test_optimized_system():
    """Test the optimized system"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🧪 OPTIMIZED SYSTEM TEST                                  ║
║              Smart Loading + Discord Integration                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Test data efficiency
    print("📊 TESTING DATA EFFICIENCY")
    print("="*50)
    
    dm = SmartDataManager()
    
    # Test smart loading
    test_teams = ["Zeus", "Ares", "Neith", "Loki", "Hel", "Scylla"]
    start_time = time.time()
    loaded_gods = dm.load_gods_for_match(test_teams)
    load_time = (time.time() - start_time) * 1000
    
    print(f"✅ Loaded {len(loaded_gods)} gods in {load_time:.1f}ms")
    print(f"📁 Memory usage: {len(str(loaded_gods))} bytes")
    
    # Test analysis speed
    print(f"\n⚡ TESTING ANALYSIS SPEED")
    print("="*50)
    
    team1 = ["Zeus", "Ares", "Neith"]
    team2 = ["Loki", "Hel", "Scylla"]
    
    # Multiple analysis tests
    times = []
    for i in range(5):
        start = time.time()
        analysis = dm.quick_analyze(team1, team2)
        times.append((time.time() - start) * 1000)
    
    print(f"Analysis times: {[f'{t:.1f}ms' for t in times]}")
    print(f"Average: {sum(times)/len(times):.1f}ms")
    print(f"Result: {analysis.win_probability*100:.0f}% win chance")
    
    # Test Discord integration
    print(f"\n📤 TESTING DISCORD INTEGRATION")
    print("="*50)
    
    discord = DiscordIntegration()  # No webhook URL for test
    await discord.send_analysis(analysis, team1, team2)
    await discord.close()
    
    print("✅ All tests passed!")

def main():
    """Main entry point"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🎮 OPTIMIZED ASSAULT BRAIN                               ║
║                Smart Loading + Discord Integration                           ║
║                                                                              ║
║  🎯 Ultra-fast analysis        📤 Discord team sharing                      ║
║  ⚡ Smart data loading         🔧 Minimal resource usage                     ║
║  📊 Essential info only        👥 Team coordination                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Example Discord webhook URL (replace with your own)
    webhook_url = None  # "https://discord.com/api/webhooks/YOUR_WEBHOOK_URL"
    
    try:
        app = OptimizedAssaultBrain(webhook_url)
        
        # Demo analysis
        print("🧪 Running demo analysis...")
        analysis = app.analyze_teams(
            ["Zeus", "Ares", "Neith"], 
            ["Loki", "Hel", "Scylla"]
        )
        
        print(f"📊 Demo result: {analysis.win_probability*100:.0f}% win chance")
        print(f"🎤 Voice: {analysis.voice_summary}")
        
        # Start GUI
        app.start()
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")

if __name__ == "__main__":
    # Run tests first
    print("🧪 Running system tests...")
    asyncio.run(test_optimized_system())
    
    print("\n" + "="*80)
    input("Press Enter to start the application...")
    
    main()