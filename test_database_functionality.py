#!/usr/bin/env python3
"""
SMITE 2 Database Functionality Test
Demonstrates how the small LLM model can query and use the comprehensive database.
"""

import sqlite3
import json
from typing import List, Dict, Any

class SMITE2DatabaseTester:
    def __init__(self, db_path: str = "assets/smite2_comprehensive.db"):
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """Connect to the database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
        
    def disconnect(self):
        """Disconnect from the database"""
        if self.conn:
            self.conn.close()
            
    def get_top_tier_gods(self) -> List[Dict]:
        """Get S and S+ tier gods for Assault"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT name, assault_tier, primary_role, damage_type,
                   sustain_score, team_fight_score, poke_score, cc_score,
                   assault_strengths, synergies
            FROM gods 
            WHERE assault_tier IN ('S+', 'S')
            ORDER BY 
                CASE assault_tier 
                    WHEN 'S+' THEN 1 
                    WHEN 'S' THEN 2 
                END,
                name
        """)
        
        results = []
        for row in cursor.fetchall():
            god_data = dict(row)
            # Parse JSON fields
            god_data['assault_strengths'] = json.loads(god_data['assault_strengths'] or '[]')
            god_data['synergies'] = json.loads(god_data['synergies'] or '[]')
            results.append(god_data)
        
        return results
        
    def get_god_abilities(self, god_name: str) -> List[Dict]:
        """Get all abilities for a specific god"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT a.ability_type, a.name, a.description,
                   a.damage_base, a.damage_scaling, a.cc_type, a.cooldown
            FROM abilities a
            JOIN gods g ON a.god_id = g.id
            WHERE g.name = ?
            ORDER BY 
                CASE a.ability_type
                    WHEN 'passive' THEN 1
                    WHEN 'ability_1' THEN 2
                    WHEN 'ability_2' THEN 3
                    WHEN 'ability_3' THEN 4
                    WHEN 'ability_4' THEN 5
                END
        """, (god_name,))
        
        return [dict(row) for row in cursor.fetchall()]
        
    def get_anti_heal_items(self) -> List[Dict]:
        """Get items that provide anti-heal for countering healers"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT name, cost, category, assault_priority,
                   passive_name, passive_description, recommended_for
            FROM items 
            WHERE assault_priority IN ('Highest', 'Mandatory vs healers')
               OR passive_description LIKE '%anti-heal%'
               OR name LIKE '%Divine Ruin%'
               OR name LIKE '%Pestilence%'
            ORDER BY 
                CASE assault_priority
                    WHEN 'Highest' THEN 1
                    WHEN 'Mandatory vs healers' THEN 2
                    ELSE 3
                END,
                cost
        """)
        
        results = []
        for row in cursor.fetchall():
            item_data = dict(row)
            item_data['recommended_for'] = json.loads(item_data['recommended_for'] or '[]')
            results.append(item_data)
        
        return results
        
    def get_team_composition_analysis(self, god_names: List[str]) -> Dict:
        """Analyze a team composition"""
        if len(god_names) != 5:
            return {"error": "Team must have exactly 5 gods"}
            
        cursor = self.conn.cursor()
        
        # Get god data
        placeholders = ','.join(['?' for _ in god_names])
        cursor.execute(f"""
            SELECT name, primary_role, damage_type, assault_tier,
                   sustain_score, team_fight_score, poke_score, cc_score,
                   assault_strengths, assault_weaknesses
            FROM gods 
            WHERE name IN ({placeholders})
        """, god_names)
        
        gods_data = [dict(row) for row in cursor.fetchall()]
        
        if len(gods_data) != 5:
            missing = set(god_names) - {g['name'] for g in gods_data}
            return {"error": f"Gods not found: {list(missing)}"}
        
        # Analyze composition
        analysis = {
            "gods": gods_data,
            "role_distribution": {},
            "damage_distribution": {"Physical": 0, "Magical": 0},
            "average_scores": {},
            "has_healer": False,
            "tier_distribution": {},
            "strengths": [],
            "weaknesses": [],
            "recommendations": []
        }
        
        # Calculate distributions and averages
        total_sustain = total_teamfight = total_poke = total_cc = 0
        
        for god in gods_data:
            # Role distribution
            role = god['primary_role']
            analysis["role_distribution"][role] = analysis["role_distribution"].get(role, 0) + 1
            
            # Damage distribution
            analysis["damage_distribution"][god['damage_type']] += 1
            
            # Tier distribution
            tier = god['assault_tier']
            analysis["tier_distribution"][tier] = analysis["tier_distribution"].get(tier, 0) + 1
            
            # Score totals
            total_sustain += god['sustain_score']
            total_teamfight += god['team_fight_score']
            total_poke += god['poke_score']
            total_cc += god['cc_score']
            
            # Check for healer
            strengths = json.loads(god['assault_strengths'] or '[]')
            if any('heal' in s.lower() for s in strengths):
                analysis["has_healer"] = True
        
        # Calculate averages
        analysis["average_scores"] = {
            "sustain": round(total_sustain / 5, 1),
            "team_fight": round(total_teamfight / 5, 1),
            "poke": round(total_poke / 5, 1),
            "cc": round(total_cc / 5, 1)
        }
        
        # Generate recommendations
        if not analysis["has_healer"]:
            analysis["recommendations"].append("Consider adding a healer like Aphrodite or Ra")
        
        if analysis["damage_distribution"]["Physical"] == 5:
            analysis["recommendations"].append("All physical damage - enemy can stack physical protections")
        elif analysis["damage_distribution"]["Magical"] == 5:
            analysis["recommendations"].append("All magical damage - enemy can stack magical protections")
        
        if analysis["role_distribution"].get("Guardian", 0) == 0:
            analysis["recommendations"].append("No guardian - team may lack frontline and CC")
        
        if analysis["average_scores"]["cc"] < 6:
            analysis["recommendations"].append("Low CC score - consider adding more crowd control")
        
        if analysis["average_scores"]["sustain"] < 6:
            analysis["recommendations"].append("Low sustain - consider adding healing or lifesteal items")
        
        return analysis
        
    def get_god_synergies(self, god_name: str) -> Dict:
        """Get synergy information for a specific god"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT name, synergies, assault_strengths, assault_weaknesses
            FROM gods 
            WHERE name = ?
        """, (god_name,))
        
        row = cursor.fetchone()
        if not row:
            return {"error": f"God '{god_name}' not found"}
        
        god_data = dict(row)
        synergies = json.loads(god_data['synergies'] or '[]')
        
        # Get detailed info about synergy gods
        if synergies:
            placeholders = ','.join(['?' for _ in synergies])
            cursor.execute(f"""
                SELECT name, primary_role, assault_tier, assault_strengths
                FROM gods 
                WHERE name IN ({placeholders})
            """, synergies)
            
            synergy_details = []
            for row in cursor.fetchall():
                synergy_god = dict(row)
                synergy_god['assault_strengths'] = json.loads(synergy_god['assault_strengths'] or '[]')
                synergy_details.append(synergy_god)
        else:
            synergy_details = []
        
        return {
            "god": god_name,
            "strengths": json.loads(god_data['assault_strengths'] or '[]'),
            "weaknesses": json.loads(god_data['assault_weaknesses'] or '[]'),
            "synergy_gods": synergy_details
        }
        
    def get_starter_items_by_role(self, role: str) -> List[Dict]:
        """Get recommended starter items for a specific role"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT name, cost, category, strength, intelligence, health,
                   notes, recommended_for
            FROM items 
            WHERE tier = 1 
              AND (recommended_for LIKE ? OR recommended_for LIKE '%' || ? || '%')
            ORDER BY cost
        """, (f'%{role}%', role))
        
        results = []
        for row in cursor.fetchall():
            item_data = dict(row)
            item_data['recommended_for'] = json.loads(item_data['recommended_for'] or '[]')
            results.append(item_data)
        
        return results
        
    def search_gods_by_criteria(self, min_tier: str = 'B', role: str = None, 
                               min_sustain: int = None, min_cc: int = None) -> List[Dict]:
        """Search gods by various criteria"""
        tier_order = {'S+': 1, 'S': 2, 'A': 3, 'B': 4, 'C': 5, 'D': 6}
        min_tier_value = tier_order.get(min_tier, 4)
        
        query = """
            SELECT name, primary_role, assault_tier, damage_type,
                   sustain_score, cc_score, team_fight_score, poke_score
            FROM gods 
            WHERE 1=1
        """
        params = []
        
        # Add tier filter
        tier_conditions = []
        for tier, value in tier_order.items():
            if value <= min_tier_value:
                tier_conditions.append(tier)
        
        if tier_conditions:
            query += f" AND assault_tier IN ({','.join(['?' for _ in tier_conditions])})"
            params.extend(tier_conditions)
        
        # Add role filter
        if role:
            query += " AND primary_role = ?"
            params.append(role)
        
        # Add sustain filter
        if min_sustain:
            query += " AND sustain_score >= ?"
            params.append(min_sustain)
        
        # Add CC filter
        if min_cc:
            query += " AND cc_score >= ?"
            params.append(min_cc)
        
        query += " ORDER BY assault_tier, name"
        
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        
        return [dict(row) for row in cursor.fetchall()]

    def run_comprehensive_test(self):
        """Run comprehensive tests to demonstrate database functionality"""
        try:
            self.connect()
            
            print("🎮 SMITE 2 Assault Advisor Database Test")
            print("=" * 50)
            
            # Test 1: Top tier gods
            print("\n1️⃣ TOP TIER GODS (S and S+ tier)")
            print("-" * 30)
            top_gods = self.get_top_tier_gods()
            for god in top_gods:
                print(f"📊 {god['name']} ({god['assault_tier']}) - {god['primary_role']}")
                print(f"   💪 Strengths: {', '.join(god['assault_strengths'][:3])}")
                print(f"   🤝 Synergies: {', '.join(god['synergies'][:3])}")
                print()
            
            # Test 2: God abilities
            print("\n2️⃣ GOD ABILITIES EXAMPLE (Anubis)")
            print("-" * 30)
            abilities = self.get_god_abilities("Anubis")
            for ability in abilities:
                print(f"🔮 {ability['name']} ({ability['ability_type']})")
                print(f"   📝 {ability['description']}")
                if ability['cc_type']:
                    print(f"   🎯 CC: {ability['cc_type']}")
                print()
            
            # Test 3: Anti-heal items
            print("\n3️⃣ ANTI-HEAL ITEMS (Counter healers)")
            print("-" * 30)
            anti_heal = self.get_anti_heal_items()
            for item in anti_heal:
                print(f"🛡️ {item['name']} - {item['cost']}g ({item['assault_priority']})")
                print(f"   📝 {item['passive_description'] or 'Anti-heal effect'}")
                print(f"   👥 For: {', '.join(item['recommended_for'])}")
                print()
            
            # Test 4: Team composition analysis
            print("\n4️⃣ TEAM COMPOSITION ANALYSIS")
            print("-" * 30)
            test_team = ["Anubis", "Athena", "Cupid", "Bellona", "Aphrodite"]
            analysis = self.get_team_composition_analysis(test_team)
            
            print(f"🏆 Team: {', '.join(test_team)}")
            print(f"📊 Average Scores:")
            for score_type, value in analysis['average_scores'].items():
                print(f"   {score_type.title()}: {value}/10")
            
            print(f"🎭 Role Distribution: {analysis['role_distribution']}")
            print(f"⚔️ Damage Split: {analysis['damage_distribution']}")
            print(f"💚 Has Healer: {analysis['has_healer']}")
            
            if analysis['recommendations']:
                print(f"💡 Recommendations:")
                for rec in analysis['recommendations']:
                    print(f"   • {rec}")
            print()
            
            # Test 5: God synergies
            print("\n5️⃣ GOD SYNERGIES EXAMPLE (Zeus)")
            print("-" * 30)
            synergies = self.get_god_synergies("Zeus")
            print(f"⚡ Zeus Synergies:")
            for synergy_god in synergies['synergy_gods']:
                print(f"   🤝 {synergy_god['name']} ({synergy_god['primary_role']}, {synergy_god['assault_tier']})")
            print()
            
            # Test 6: Starter items by role
            print("\n6️⃣ STARTER ITEMS FOR MAGES")
            print("-" * 30)
            starters = self.get_starter_items_by_role("Mage")
            for item in starters:
                print(f"🎯 {item['name']} - {item['cost']}g")
                print(f"   📝 {item['notes']}")
                print()
            
            # Test 7: Search functionality
            print("\n7️⃣ SEARCH: High-tier Guardians with good CC")
            print("-" * 30)
            search_results = self.search_gods_by_criteria(
                min_tier='A', role='Guardian', min_cc=8
            )
            for god in search_results:
                print(f"🛡️ {god['name']} ({god['assault_tier']}) - CC: {god['cc_score']}/10")
            
            print("\n✅ All tests completed successfully!")
            print("\n💡 This database can help the small LLM model:")
            print("   • Recommend gods based on team composition")
            print("   • Suggest counter-picks and synergies")
            print("   • Provide item build recommendations")
            print("   • Analyze team strengths and weaknesses")
            print("   • Give ability details and cooldowns")
            print("   • Offer strategic advice for Assault mode")
            
        except Exception as e:
            print(f"❌ Error during testing: {e}")
        finally:
            self.disconnect()

if __name__ == "__main__":
    tester = SMITE2DatabaseTester()
    tester.run_comprehensive_test()