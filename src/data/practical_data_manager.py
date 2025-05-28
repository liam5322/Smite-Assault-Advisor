#!/usr/bin/env python3
"""
🎯 Practical Data Manager for SMITE 2 Assault Brain
Focuses on actually useful data integration and functionality
"""

import asyncio
import aiohttp
import json
import sqlite3
import gzip
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass, asdict
import pickle

logger = logging.getLogger(__name__)

@dataclass
class AssaultGodData:
    """Assault-specific god data"""
    name: str
    role: str
    assault_win_rate: float
    assault_pick_rate: float
    strengths: List[str]
    weaknesses: List[str]
    counters: List[str]
    synergies: List[str]
    recommended_builds: List[Dict[str, Any]]
    early_game_power: int  # 1-10 scale
    late_game_power: int   # 1-10 scale
    team_fight_impact: int # 1-10 scale
    last_updated: str

@dataclass
class AssaultItemData:
    """Assault-specific item data"""
    name: str
    cost: int
    stats: Dict[str, Any]
    assault_effectiveness: int  # 1-10 scale
    situational_use: str
    counters_what: List[str]
    build_priority: str  # "core", "situational", "luxury"
    assault_notes: str
    last_updated: str

class PracticalDataManager:
    """Practical data manager focused on useful functionality"""
    
    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path(__file__).parent.parent.parent / "practical_data"
        self.data_dir.mkdir(exist_ok=True)
        
        self.db_path = self.data_dir / "assault_data.db"
        self.cache_dir = self.data_dir / "cache"
        self.cache_dir.mkdir(exist_ok=True)
        
        self._init_database()
        self._load_static_data()
    
    def _init_database(self):
        """Initialize the practical database"""
        with sqlite3.connect(self.db_path) as conn:
            # Gods table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS assault_gods (
                    name TEXT PRIMARY KEY,
                    role TEXT,
                    assault_win_rate REAL,
                    assault_pick_rate REAL,
                    data BLOB,
                    last_updated TEXT
                )
            """)
            
            # Items table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS assault_items (
                    name TEXT PRIMARY KEY,
                    cost INTEGER,
                    assault_effectiveness INTEGER,
                    build_priority TEXT,
                    data BLOB,
                    last_updated TEXT
                )
            """)
            
            # Match analysis cache
            conn.execute("""
                CREATE TABLE IF NOT EXISTS match_analysis (
                    team_hash TEXT PRIMARY KEY,
                    analysis BLOB,
                    timestamp TEXT
                )
            """)
            
            # User preferences
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated TEXT
                )
            """)
    
    def _load_static_data(self):
        """Load curated static data for Assault mode"""
        # This would be manually curated data based on Assault meta
        self.static_god_data = {
            "zeus": AssaultGodData(
                name="Zeus",
                role="Mage",
                assault_win_rate=0.68,
                assault_pick_rate=0.25,
                strengths=["High burst damage", "Chain lightning clears waves", "Strong team fight presence"],
                weaknesses=["No escape", "Vulnerable to dive", "Mana hungry early"],
                counters=["Odin", "Ares", "Thor", "Any dive comp"],
                synergies=["Ares", "Cerberus", "Ymir", "Setup tanks"],
                recommended_builds=[
                    {
                        "name": "Standard Burst",
                        "items": ["Doom Orb", "Spear of Desolation", "Rod of Tahuti", "Chronos' Pendant", "Soul Reaver", "Staff of Myrddin"],
                        "notes": "Max damage output for team fights"
                    },
                    {
                        "name": "Survivability",
                        "items": ["Warlock's Staff", "Breastplate of Valor", "Rod of Tahuti", "Void Stone", "Mantle of Discord", "Staff of Myrddin"],
                        "notes": "When facing heavy dive comps"
                    }
                ],
                early_game_power=6,
                late_game_power=9,
                team_fight_impact=10,
                last_updated=datetime.now().isoformat()
            ),
            
            "ares": AssaultGodData(
                name="Ares",
                role="Guardian",
                assault_win_rate=0.72,
                assault_pick_rate=0.30,
                strengths=["Game-changing ultimate", "High damage for tank", "Chain CC"],
                weaknesses=["No peel for carries", "Ultimate countered by beads", "Mana issues"],
                counters=["Beads users", "High mobility gods", "Spread formations"],
                synergies=["Zeus", "Scylla", "Any burst mage", "Follow-up damage"],
                recommended_builds=[
                    {
                        "name": "Blink Combo",
                        "items": ["Sentinel's Gift", "Sovereignty", "Heartward Amulet", "Pridwen", "Mantle of Discord", "Rod of Tahuti"],
                        "notes": "Blink + Ult combo focus"
                    }
                ],
                early_game_power=7,
                late_game_power=8,
                team_fight_impact=10,
                last_updated=datetime.now().isoformat()
            ),
            
            "loki": AssaultGodData(
                name="Loki",
                role="Assassin",
                assault_win_rate=0.42,
                assault_pick_rate=0.15,
                strengths=["High single target burst", "Stealth engage", "Split push potential"],
                weaknesses=["Useless in team fights", "One-trick pony", "Falls off late"],
                counters=["Mystical Mail", "AOE abilities", "Group positioning"],
                synergies=["Distraction comps", "Other split pushers"],
                recommended_builds=[
                    {
                        "name": "Burst Build",
                        "items": ["Jotunn's Wrath", "Hydra's Lament", "Heartseeker", "Titan's Bane", "Bloodforge", "Mantle of Discord"],
                        "notes": "One-shot potential on squishies"
                    }
                ],
                early_game_power=8,
                late_game_power=4,
                team_fight_impact=3,
                last_updated=datetime.now().isoformat()
            )
        }
        
        self.static_item_data = {
            "meditation_cloak": AssaultItemData(
                name="Meditation Cloak",
                cost=500,
                stats={"mp5": 7, "hp5": 7},
                assault_effectiveness=10,
                situational_use="Essential for sustain in Assault",
                counters_what=["Poke comps", "Mana pressure"],
                build_priority="core",
                assault_notes="Mandatory for most gods. Coordinate team usage for maximum effect.",
                last_updated=datetime.now().isoformat()
            ),
            
            "divine_ruin": AssaultItemData(
                name="Divine Ruin",
                cost=2300,
                stats={"power": 80, "penetration": 15},
                assault_effectiveness=9,
                situational_use="Against healing comps",
                counters_what=["Healers", "Lifesteal", "Sustain comps"],
                build_priority="situational",
                assault_notes="Rush against Hel, Aphrodite, Chang'e, or heavy lifesteal comps.",
                last_updated=datetime.now().isoformat()
            ),
            
            "mystical_mail": AssaultItemData(
                name="Mystical Mail",
                cost=2150,
                stats={"health": 300, "physical_protection": 40},
                assault_effectiveness=8,
                situational_use="Against stealth/melee gods",
                counters_what=["Loki", "Serqet", "Melee assassins"],
                build_priority="situational",
                assault_notes="Reveals stealth gods and provides AOE damage in team fights.",
                last_updated=datetime.now().isoformat()
            )
        }
    
    def get_god_analysis(self, god_name: str) -> Optional[AssaultGodData]:
        """Get comprehensive god analysis for Assault"""
        god_key = god_name.lower().replace(" ", "").replace("'", "")
        
        # Check static data first
        if god_key in self.static_god_data:
            return self.static_god_data[god_key]
        
        # Check database
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT data FROM assault_gods WHERE name = ?", (god_name,))
                row = cursor.fetchone()
                if row:
                    return pickle.loads(gzip.decompress(row[0]))
        except Exception as e:
            logger.error(f"Error retrieving god data for {god_name}: {e}")
        
        return None
    
    def get_item_analysis(self, item_name: str) -> Optional[AssaultItemData]:
        """Get item analysis for Assault"""
        item_key = item_name.lower().replace(" ", "_").replace("'", "")
        
        # Check static data first
        if item_key in self.static_item_data:
            return self.static_item_data[item_key]
        
        # Check database
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT data FROM assault_items WHERE name = ?", (item_name,))
                row = cursor.fetchone()
                if row:
                    return pickle.loads(gzip.decompress(row[0]))
        except Exception as e:
            logger.error(f"Error retrieving item data for {item_name}: {e}")
        
        return None
    
    def analyze_team_composition(self, team1: List[str], team2: List[str]) -> Dict[str, Any]:
        """Analyze team composition matchup"""
        team1_analysis = self._analyze_single_team(team1)
        team2_analysis = self._analyze_single_team(team2)
        
        # Calculate win probability based on team strengths
        team1_score = self._calculate_team_score(team1_analysis)
        team2_score = self._calculate_team_score(team2_analysis)
        
        total_score = team1_score + team2_score
        win_probability = team1_score / total_score if total_score > 0 else 0.5
        
        # Generate strategic advice
        advice = self._generate_strategic_advice(team1_analysis, team2_analysis)
        
        return {
            "team1_analysis": team1_analysis,
            "team2_analysis": team2_analysis,
            "win_probability": win_probability,
            "strategic_advice": advice,
            "key_matchups": self._identify_key_matchups(team1, team2),
            "item_priorities": self._suggest_item_priorities(team1, team2),
            "timestamp": datetime.now().isoformat()
        }
    
    def _analyze_single_team(self, team: List[str]) -> Dict[str, Any]:
        """Analyze a single team composition"""
        team_data = []
        total_early_power = 0
        total_late_power = 0
        total_team_fight = 0
        
        roles = {"Guardian": 0, "Warrior": 0, "Mage": 0, "Hunter": 0, "Assassin": 0}
        
        for god_name in team:
            god_data = self.get_god_analysis(god_name)
            if god_data:
                team_data.append(god_data)
                total_early_power += god_data.early_game_power
                total_late_power += god_data.late_game_power
                total_team_fight += god_data.team_fight_impact
                roles[god_data.role] += 1
        
        # Calculate team composition balance
        has_tank = roles["Guardian"] + roles["Warrior"] > 0
        has_adc = roles["Hunter"] > 0
        has_mage = roles["Mage"] > 0
        
        balance_score = 0
        if has_tank: balance_score += 3
        if has_adc: balance_score += 2
        if has_mage: balance_score += 2
        if roles["Guardian"] >= 1: balance_score += 1  # Prefer guardians in assault
        
        # Identify team strengths and weaknesses
        strengths = []
        weaknesses = []
        
        if total_team_fight >= 35:
            strengths.append("Excellent team fight potential")
        if total_early_power >= 35:
            strengths.append("Strong early game pressure")
        if total_late_power >= 40:
            strengths.append("Powerful late game scaling")
        if has_tank and has_adc and has_mage:
            strengths.append("Balanced composition")
        
        if not has_tank:
            weaknesses.append("No frontline/tank")
        if total_team_fight < 25:
            weaknesses.append("Weak team fight presence")
        if not has_adc:
            weaknesses.append("Lacks sustained DPS")
        if roles["Assassin"] >= 2:
            weaknesses.append("Too many assassins for Assault")
        
        return {
            "gods": team_data,
            "role_distribution": roles,
            "early_game_power": total_early_power / len(team) if team else 0,
            "late_game_power": total_late_power / len(team) if team else 0,
            "team_fight_impact": total_team_fight / len(team) if team else 0,
            "balance_score": balance_score,
            "strengths": strengths,
            "weaknesses": weaknesses
        }
    
    def _calculate_team_score(self, team_analysis: Dict[str, Any]) -> float:
        """Calculate overall team score for win probability"""
        score = 0
        
        # Base score from team fight impact (most important in Assault)
        score += team_analysis["team_fight_impact"] * 3
        
        # Balance score
        score += team_analysis["balance_score"] * 2
        
        # Late game scaling (Assault games tend to go long)
        score += team_analysis["late_game_power"] * 2
        
        # Early game power (less important but still relevant)
        score += team_analysis["early_game_power"] * 1
        
        return max(score, 1)  # Minimum score of 1
    
    def _generate_strategic_advice(self, team1: Dict[str, Any], team2: Dict[str, Any]) -> List[str]:
        """Generate strategic advice based on team analysis"""
        advice = []
        
        # Early game advice
        if team1["early_game_power"] > team2["early_game_power"] + 1:
            advice.append("🚀 You have early game advantage - pressure them before they scale")
        elif team2["early_game_power"] > team1["early_game_power"] + 1:
            advice.append("🛡️ Play safe early - they have stronger early game")
        
        # Late game advice
        if team1["late_game_power"] > team2["late_game_power"] + 1:
            advice.append("⏰ You scale better - farm safely and wait for late game")
        elif team2["late_game_power"] > team1["late_game_power"] + 1:
            advice.append("⚡ End early - they outscale you in late game")
        
        # Team fight advice
        if team1["team_fight_impact"] > team2["team_fight_impact"] + 1:
            advice.append("⚔️ Force team fights - you have better team fight potential")
        elif team2["team_fight_impact"] > team1["team_fight_impact"] + 1:
            advice.append("🏃 Avoid extended team fights - look for picks instead")
        
        # Composition-specific advice
        if team2["role_distribution"]["Guardian"] == 0:
            advice.append("🎯 They have no tank - focus their squishies")
        
        if team2["role_distribution"]["Hunter"] == 0:
            advice.append("🏹 They lack sustained DPS - survive their burst")
        
        return advice
    
    def _identify_key_matchups(self, team1: List[str], team2: List[str]) -> List[Dict[str, str]]:
        """Identify key god matchups to watch"""
        matchups = []
        
        for god1 in team1:
            god1_data = self.get_god_analysis(god1)
            if not god1_data:
                continue
                
            for god2 in team2:
                if god2 in god1_data.counters:
                    matchups.append({
                        "type": "counter",
                        "description": f"{god2} counters {god1}",
                        "advice": f"Be careful of {god2} when playing {god1}"
                    })
                elif god1_data.role == "Mage" and god2.lower() in ["odin", "ares", "thor"]:
                    matchups.append({
                        "type": "threat",
                        "description": f"{god2} can dive {god1}",
                        "advice": f"{god1} needs to position safely against {god2}"
                    })
        
        return matchups[:3]  # Return top 3 most important matchups
    
    def _suggest_item_priorities(self, team1: List[str], team2: List[str]) -> List[Dict[str, str]]:
        """Suggest item priorities based on enemy team"""
        priorities = []
        
        # Check for healers
        healers = ["hel", "aphrodite", "chang'e", "ra", "sylvanus"]
        enemy_healers = [god for god in team2 if god.lower() in healers]
        
        if enemy_healers:
            priorities.append({
                "item": "Divine Ruin / Toxic Blade",
                "reason": f"Counter healing from {', '.join(enemy_healers)}",
                "priority": "high"
            })
        
        # Check for stealth gods
        stealth_gods = ["loki", "serqet", "ao_kuang"]
        enemy_stealth = [god for god in team2 if god.lower().replace(" ", "_") in stealth_gods]
        
        if enemy_stealth:
            priorities.append({
                "item": "Mystical Mail",
                "reason": f"Reveal stealth from {', '.join(enemy_stealth)}",
                "priority": "medium"
            })
        
        # Check for heavy physical damage
        physical_gods = []
        for god in team2:
            god_data = self.get_god_analysis(god)
            if god_data and god_data.role in ["Hunter", "Assassin", "Warrior"]:
                physical_gods.append(god)
        
        if len(physical_gods) >= 3:
            priorities.append({
                "item": "Physical Protection",
                "reason": f"Heavy physical damage from {len(physical_gods)} gods",
                "priority": "high"
            })
        
        return priorities
    
    def get_build_suggestion(self, god_name: str, enemy_team: List[str], ally_team: List[str]) -> Dict[str, Any]:
        """Get build suggestion for a specific god against enemy team"""
        god_data = self.get_god_analysis(god_name)
        if not god_data:
            return {"error": f"No data available for {god_name}"}
        
        # Start with recommended build
        base_build = god_data.recommended_builds[0] if god_data.recommended_builds else None
        if not base_build:
            return {"error": f"No builds available for {god_name}"}
        
        # Modify build based on enemy team
        suggested_items = base_build["items"].copy()
        modifications = []
        
        # Check for specific counters needed
        item_priorities = self._suggest_item_priorities([god_name], enemy_team)
        
        for priority in item_priorities:
            if priority["priority"] == "high":
                # Suggest replacing a luxury item with counter item
                if "Divine Ruin" in priority["item"] and god_data.role == "Mage":
                    modifications.append(f"Consider {priority['item']} - {priority['reason']}")
                elif "Mystical Mail" in priority["item"] and god_data.role in ["Guardian", "Warrior"]:
                    modifications.append(f"Consider {priority['item']} - {priority['reason']}")
        
        return {
            "god": god_name,
            "base_build": suggested_items,
            "modifications": modifications,
            "build_notes": base_build.get("notes", ""),
            "situational_advice": self._get_situational_advice(god_data, enemy_team)
        }
    
    def _get_situational_advice(self, god_data: AssaultGodData, enemy_team: List[str]) -> List[str]:
        """Get situational advice for playing this god"""
        advice = []
        
        # Check if any enemies counter this god
        countered_by = [god for god in enemy_team if god in god_data.counters]
        if countered_by:
            advice.append(f"⚠️ Be careful of {', '.join(countered_by)} - they counter you")
        
        # Role-specific advice
        if god_data.role == "Mage":
            advice.append("🎯 Position safely behind your frontline")
            advice.append("⚡ Save your escape for enemy dive attempts")
        elif god_data.role == "Guardian":
            advice.append("🛡️ Initiate team fights when your team is ready")
            advice.append("🤝 Peel for your carries when they're threatened")
        elif god_data.role == "Hunter":
            advice.append("🏹 Focus on consistent DPS in team fights")
            advice.append("👁️ Watch for flanking assassins")
        
        return advice

async def demo_practical_data():
    """Demo the practical data manager"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🎯 PRACTICAL DATA MANAGER DEMO                           ║
║                     Actually Useful SMITE Analysis                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Initialize data manager
    data_manager = PracticalDataManager()
    
    # Demo team analysis
    print("📊 TEAM COMPOSITION ANALYSIS")
    print("="*50)
    
    team1 = ["Zeus", "Ares", "Neith", "Thor", "Ra"]
    team2 = ["Loki", "Ymir", "Scylla", "Artemis", "Hel"]
    
    print(f"Team 1: {', '.join(team1)}")
    print(f"Team 2: {', '.join(team2)}")
    print()
    
    analysis = data_manager.analyze_team_composition(team1, team2)
    
    print(f"🎯 Win Probability: {analysis['win_probability']*100:.1f}%")
    print()
    
    print("💪 Team 1 Strengths:")
    for strength in analysis['team1_analysis']['strengths']:
        print(f"  ✓ {strength}")
    print()
    
    print("⚠️ Team 1 Weaknesses:")
    for weakness in analysis['team1_analysis']['weaknesses']:
        print(f"  ✗ {weakness}")
    print()
    
    print("🧠 Strategic Advice:")
    for advice in analysis['strategic_advice']:
        print(f"  {advice}")
    print()
    
    print("🎯 Key Matchups:")
    for matchup in analysis['key_matchups']:
        print(f"  {matchup['description']} - {matchup['advice']}")
    print()
    
    print("🛡️ Item Priorities:")
    for priority in analysis['item_priorities']:
        print(f"  {priority['item']} ({priority['priority']}) - {priority['reason']}")
    print()
    
    # Demo build suggestion
    print("🔨 BUILD SUGGESTION DEMO")
    print("="*50)
    
    build_suggestion = data_manager.get_build_suggestion("Zeus", team2, team1)
    
    print(f"God: {build_suggestion['god']}")
    print(f"Recommended Build: {' → '.join(build_suggestion['base_build'])}")
    print()
    
    if build_suggestion['modifications']:
        print("🔧 Suggested Modifications:")
        for mod in build_suggestion['modifications']:
            print(f"  {mod}")
        print()
    
    print("💡 Situational Advice:")
    for advice in build_suggestion['situational_advice']:
        print(f"  {advice}")
    print()
    
    # Demo individual god analysis
    print("🎭 INDIVIDUAL GOD ANALYSIS")
    print("="*50)
    
    zeus_data = data_manager.get_god_analysis("Zeus")
    if zeus_data:
        print(f"God: {zeus_data.name} ({zeus_data.role})")
        print(f"Assault Win Rate: {zeus_data.assault_win_rate*100:.1f}%")
        print(f"Pick Rate: {zeus_data.assault_pick_rate*100:.1f}%")
        print(f"Power Curve: Early {zeus_data.early_game_power}/10, Late {zeus_data.late_game_power}/10")
        print(f"Team Fight Impact: {zeus_data.team_fight_impact}/10")
        print()
        
        print("Strengths:")
        for strength in zeus_data.strengths:
            print(f"  ✓ {strength}")
        print()
        
        print("Countered by:")
        for counter in zeus_data.counters:
            print(f"  ⚠️ {counter}")
    
    print("\n🚀 Practical data manager ready for production!")
    print("💡 This provides actually useful analysis for SMITE Assault players")

if __name__ == "__main__":
    asyncio.run(demo_practical_data())