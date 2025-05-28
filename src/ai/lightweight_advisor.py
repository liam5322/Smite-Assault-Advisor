#!/usr/bin/env python3
"""
Lightweight AI Advisor for SMITE 2 Assault
Optimized for small AI models (Qwen 0.6B, TinyLlama 1.1B, etc.)
Uses structured database queries to minimize token usage
"""

import sqlite3
import json
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging

@dataclass
class TeamAnalysis:
    """Structured team analysis results"""
    overall_score: int
    sustain_score: int
    damage_score: int
    cc_score: int
    wave_clear_score: int
    has_healer: bool
    physical_damage_count: int
    magical_damage_count: int
    tank_count: int
    strengths: List[str]
    weaknesses: List[str]
    recommended_strategy: str
    priority_items: List[str]
    win_probability: float

@dataclass
class GodRecommendation:
    """Individual god build recommendation"""
    god_name: str
    priority_items: List[str]
    situational_items: List[str]
    build_order: List[str]
    playstyle_notes: str
    aspect_recommendation: Optional[str]

class LightweightAssaultAdvisor:
    """
    Lightweight AI advisor that uses database queries and rule-based logic
    to provide assault recommendations without requiring large language models
    """
    
    def __init__(self, db_path: str = "assets/smite2_comprehensive.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Initialize database connection
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
        
        # Cache frequently used data
        self._god_cache = {}
        self._item_cache = {}
        self._load_caches()
    
    def _load_caches(self):
        """Load frequently accessed data into memory for performance"""
        cursor = self.conn.cursor()
        
        # Cache god data
        cursor.execute("""
        SELECT name, assault_tier, sustain_score, team_fight_score, 
               damage_type, primary_role, assault_strengths, assault_weaknesses
        FROM gods
        """)
        
        for row in cursor.fetchall():
            self._god_cache[row['name']] = {
                'tier': row['assault_tier'],
                'sustain': row['sustain_score'],
                'team_fight': row['team_fight_score'],
                'damage_type': row['damage_type'],
                'role': row['primary_role'],
                'strengths': json.loads(row['assault_strengths']) if row['assault_strengths'] else [],
                'weaknesses': json.loads(row['assault_weaknesses']) if row['assault_weaknesses'] else []
            }
        
        # Cache high-priority items
        cursor.execute("""
        SELECT name, assault_priority, assault_utility, cost, recommended_for
        FROM items
        WHERE assault_priority IN ('Highest', 'Mandatory vs healers', 'High')
        ORDER BY 
            CASE assault_priority
                WHEN 'Highest' THEN 1
                WHEN 'Mandatory vs healers' THEN 2
                WHEN 'High' THEN 3
                ELSE 4
            END, cost ASC
        """)
        
        for row in cursor.fetchall():
            self._item_cache[row['name']] = {
                'priority': row['assault_priority'],
                'utility': row['assault_utility'],
                'cost': row['cost'],
                'recommended_for': json.loads(row['recommended_for']) if row['recommended_for'] else []
            }
    
    def analyze_team_composition(self, team_gods: List[str]) -> TeamAnalysis:
        """
        Analyze a team composition and provide structured recommendations
        
        Args:
            team_gods: List of god names in the team
            
        Returns:
            TeamAnalysis object with scores and recommendations
        """
        if len(team_gods) != 5:
            raise ValueError("Team must have exactly 5 gods")
        
        # Check if we have cached analysis
        composition_hash = self._get_composition_hash(team_gods)
        cached_analysis = self._get_cached_analysis(composition_hash)
        if cached_analysis:
            return cached_analysis
        
        # Analyze team composition
        analysis = self._perform_team_analysis(team_gods)
        
        # Cache the analysis
        self._cache_analysis(composition_hash, team_gods, analysis)
        
        return analysis
    
    def _get_composition_hash(self, team_gods: List[str]) -> str:
        """Generate a hash for the team composition"""
        sorted_gods = sorted(team_gods)
        return hashlib.md5(json.dumps(sorted_gods).encode()).hexdigest()
    
    def _get_cached_analysis(self, composition_hash: str) -> Optional[TeamAnalysis]:
        """Retrieve cached team analysis if available"""
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT * FROM team_compositions WHERE composition_hash = ?
        """, (composition_hash,))
        
        row = cursor.fetchone()
        if row:
            return TeamAnalysis(
                overall_score=row['overall_score'],
                sustain_score=row['sustain_score'],
                damage_score=row['damage_score'],
                cc_score=row['cc_score'],
                wave_clear_score=row['wave_clear_score'],
                has_healer=bool(row['has_healer']),
                physical_damage_count=row['physical_damage_count'],
                magical_damage_count=row['magical_damage_count'],
                tank_count=row['tank_count'],
                strengths=json.loads(row['strengths']) if row['strengths'] else [],
                weaknesses=json.loads(row['weaknesses']) if row['weaknesses'] else [],
                recommended_strategy=row['recommended_strategy'],
                priority_items=json.loads(row['priority_items']) if row['priority_items'] else [],
                win_probability=row['overall_score'] / 10.0  # Convert to probability
            )
        return None
    
    def _perform_team_analysis(self, team_gods: List[str]) -> TeamAnalysis:
        """Perform detailed team composition analysis"""
        
        # Initialize counters and scores
        sustain_total = 0
        damage_total = 0
        cc_total = 0
        wave_clear_total = 0
        physical_count = 0
        magical_count = 0
        tank_count = 0
        has_healer = False
        
        strengths = []
        weaknesses = []
        
        # Analyze each god
        for god_name in team_gods:
            god_data = self._god_cache.get(god_name)
            if not god_data:
                continue
            
            # Accumulate scores
            sustain_total += god_data['sustain']
            damage_total += god_data['team_fight']
            
            # Count damage types
            if god_data['damage_type'] == 'Physical':
                physical_count += 1
            else:
                magical_count += 1
            
            # Check for tanks
            if god_data['role'] in ['Guardian', 'Tank']:
                tank_count += 1
            
            # Check for healers (high sustain + S+ tier)
            if god_data['sustain'] >= 8 and god_data['tier'] in ['S+', 'S']:
                has_healer = True
                strengths.append(f"Strong healer: {god_name}")
            
            # Add god-specific strengths
            strengths.extend([f"{god_name}: {s}" for s in god_data['strengths'][:2]])  # Limit to top 2
        
        # Calculate average scores
        sustain_score = min(10, sustain_total // 5)
        damage_score = min(10, damage_total // 5)
        cc_score = self._calculate_cc_score(team_gods)
        wave_clear_score = self._calculate_wave_clear_score(team_gods)
        
        # Analyze team balance
        if not has_healer:
            weaknesses.append("No healer - limited sustain")
        
        if tank_count == 0:
            weaknesses.append("No tank - vulnerable to dive")
        elif tank_count >= 3:
            weaknesses.append("Too many tanks - low damage")
        
        if physical_count == 0 or magical_count == 0:
            weaknesses.append("Single damage type - easy to counter")
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(
            sustain_score, damage_score, cc_score, wave_clear_score, 
            has_healer, tank_count, physical_count, magical_count
        )
        
        # Generate strategy and item recommendations
        strategy = self._generate_strategy(has_healer, tank_count, sustain_score)
        priority_items = self._get_priority_items(has_healer, team_gods)
        
        return TeamAnalysis(
            overall_score=overall_score,
            sustain_score=sustain_score,
            damage_score=damage_score,
            cc_score=cc_score,
            wave_clear_score=wave_clear_score,
            has_healer=has_healer,
            physical_damage_count=physical_count,
            magical_damage_count=magical_count,
            tank_count=tank_count,
            strengths=strengths[:5],  # Limit to top 5
            weaknesses=weaknesses[:3],  # Limit to top 3
            recommended_strategy=strategy,
            priority_items=priority_items,
            win_probability=overall_score / 10.0
        )
    
    def _calculate_cc_score(self, team_gods: List[str]) -> int:
        """Calculate team CC score based on god abilities"""
        cursor = self.conn.cursor()
        
        cc_score = 0
        for god_name in team_gods:
            cursor.execute("""
            SELECT COUNT(*) as cc_count
            FROM abilities a
            JOIN gods g ON a.god_id = g.id
            WHERE g.name = ? AND a.cc_type IS NOT NULL AND a.cc_type != ''
            """, (god_name,))
            
            result = cursor.fetchone()
            if result:
                cc_score += min(3, result['cc_count'])  # Cap per god at 3
        
        return min(10, cc_score)
    
    def _calculate_wave_clear_score(self, team_gods: List[str]) -> int:
        """Calculate team wave clear score"""
        cursor = self.conn.cursor()
        
        wave_clear_score = 0
        for god_name in team_gods:
            cursor.execute("""
            SELECT wave_clear_score
            FROM gods
            WHERE name = ?
            """, (god_name,))
            
            result = cursor.fetchone()
            if result:
                wave_clear_score += result['wave_clear_score']
        
        return min(10, wave_clear_score // 5)
    
    def _calculate_overall_score(self, sustain: int, damage: int, cc: int, 
                                wave_clear: int, has_healer: bool, tank_count: int,
                                physical_count: int, magical_count: int) -> int:
        """Calculate overall team score with assault-specific weighting"""
        
        # Assault-specific weights
        score = (
            sustain * 0.35 +      # Sustain is most important in assault
            damage * 0.25 +       # Damage output
            cc * 0.20 +           # Crowd control
            wave_clear * 0.20     # Wave clear
        )
        
        # Bonuses and penalties
        if has_healer:
            score += 2  # Huge bonus for healer
        
        if tank_count >= 1:
            score += 1  # Bonus for having a tank
        
        if physical_count > 0 and magical_count > 0:
            score += 1  # Bonus for damage type balance
        
        return min(10, max(1, int(score)))
    
    def _generate_strategy(self, has_healer: bool, tank_count: int, sustain_score: int) -> str:
        """Generate recommended strategy based on team composition"""
        
        if has_healer and tank_count >= 1:
            return "Play defensively, use healer to sustain through poke, engage when enemy is low"
        elif has_healer:
            return "Focus on sustain and poke, avoid all-ins without proper frontline"
        elif sustain_score >= 7:
            return "Use built-in sustain to your advantage, play for extended fights"
        elif tank_count >= 2:
            return "Aggressive early game, force fights before enemy sustain comes online"
        else:
            return "High-risk aggressive play, end fights quickly before sustain disadvantage shows"
    
    def _get_priority_items(self, has_healer: bool, team_gods: List[str]) -> List[str]:
        """Get priority items based on team composition"""
        priority_items = []
        
        # Always high priority in assault
        priority_items.append("Amanita Charm")
        
        # Anti-heal if enemy has healer (simplified - would need enemy team info)
        if has_healer:  # If we have healer, enemy might too
            priority_items.extend(["Divine Ruin", "Brawler's Ruin"])
        
        # Sustain items
        priority_items.extend(["Bloodforge", "Bancroft's Talon", "Stone of Gaia"])
        
        # Aura items for tanks
        tank_count = sum(1 for god in team_gods if self._god_cache.get(god, {}).get('role') in ['Guardian', 'Tank'])
        if tank_count >= 1:
            priority_items.extend(["Sovereignty", "Heartward Amulet"])
        
        return priority_items[:6]  # Limit to top 6
    
    def _cache_analysis(self, composition_hash: str, team_gods: List[str], analysis: TeamAnalysis):
        """Cache team analysis for future use"""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
            INSERT OR REPLACE INTO team_compositions (
                composition_hash, god_names, overall_score, sustain_score,
                damage_score, cc_score, wave_clear_score, has_healer,
                physical_damage_count, magical_damage_count, tank_count,
                strengths, weaknesses, recommended_strategy, priority_items
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                composition_hash,
                json.dumps(team_gods),
                analysis.overall_score,
                analysis.sustain_score,
                analysis.damage_score,
                analysis.cc_score,
                analysis.wave_clear_score,
                analysis.has_healer,
                analysis.physical_damage_count,
                analysis.magical_damage_count,
                analysis.tank_count,
                json.dumps(analysis.strengths),
                json.dumps(analysis.weaknesses),
                analysis.recommended_strategy,
                json.dumps(analysis.priority_items)
            ))
            self.conn.commit()
        except Exception as e:
            self.logger.warning(f"Failed to cache analysis: {e}")
    
    def get_quick_recommendations(self, team_gods: List[str]) -> Dict[str, Any]:
        """
        Get quick recommendations for immediate use
        Optimized for minimal processing and fast response
        """
        analysis = self.analyze_team_composition(team_gods)
        
        return {
            "win_probability": f"{analysis.win_probability:.1%}",
            "key_strength": analysis.strengths[0] if analysis.strengths else "Balanced composition",
            "main_weakness": analysis.weaknesses[0] if analysis.weaknesses else "No major weaknesses",
            "strategy": analysis.recommended_strategy,
            "must_buy_items": analysis.priority_items[:3],
            "team_rating": f"{analysis.overall_score}/10",
            "healer_status": "Has healer" if analysis.has_healer else "No healer - buy sustain",
            "damage_balance": f"{analysis.physical_damage_count}P/{analysis.magical_damage_count}M"
        }
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

# Example usage and testing
if __name__ == "__main__":
    # Initialize advisor
    advisor = LightweightAssaultAdvisor()
    
    # Test team analysis
    test_team = ["Ra", "Ares", "Zeus", "Ah Muzen Cab", "Agni"]
    
    print("🔍 Analyzing team composition...")
    analysis = advisor.analyze_team_composition(test_team)
    
    print(f"\n📊 Team Analysis Results:")
    print(f"Overall Score: {analysis.overall_score}/10")
    print(f"Win Probability: {analysis.win_probability:.1%}")
    print(f"Has Healer: {analysis.has_healer}")
    print(f"Damage Split: {analysis.physical_damage_count}P/{analysis.magical_damage_count}M")
    print(f"Strategy: {analysis.recommended_strategy}")
    print(f"Priority Items: {', '.join(analysis.priority_items[:3])}")
    
    # Test quick recommendations
    print(f"\n⚡ Quick recommendations:")
    quick = advisor.get_quick_recommendations(test_team)
    for key, value in quick.items():
        print(f"{key}: {value}")
    
    advisor.close()