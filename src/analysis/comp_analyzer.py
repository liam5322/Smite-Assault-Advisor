"""
Advanced team composition analysis with meta-aware calculations
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import Counter
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class GodStats:
    """God statistics for analysis"""
    name: str
    role: str
    damage_type: str
    cc_score: int
    clear_score: int
    sustain_score: int
    mobility_score: int
    team_fight_score: int
    late_game_score: int
    difficulty: int
    meta_tier: str

@dataclass
class TeamAnalysis:
    """Comprehensive team analysis results"""
    overall_score: float
    role_distribution: Dict[str, int]
    damage_split: Dict[str, int]
    cc_potential: int
    clear_potential: int
    sustain_potential: int
    team_fight_score: int
    late_game_scaling: int
    weaknesses: List[str]
    strengths: List[str]

class CompAnalyzer:
    """Advanced team composition analyzer with meta awareness"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.god_data = self._load_god_database()
        self.meta_weights = self._load_meta_weights()
        self.synergy_matrix = self._load_synergy_matrix()
        
        logger.info(f"Composition analyzer initialized with {len(self.god_data)} gods")
        
    def _load_god_database(self) -> Dict[str, GodStats]:
        """Load comprehensive god database"""
        god_file = Path(__file__).parent.parent.parent / 'assets' / 'gods.json'
        
        # Comprehensive god database for SMITE 2 Assault
        default_data = {
            # Tanks/Guardians
            'Ymir': GodStats('Ymir', 'Tank', 'Magical', 9, 6, 4, 2, 8, 6, 3, 'A'),
            'Ares': GodStats('Ares', 'Tank', 'Magical', 10, 4, 3, 3, 9, 7, 4, 'S'),
            'Athena': GodStats('Athena', 'Tank', 'Magical', 8, 5, 5, 7, 8, 6, 5, 'A'),
            'Geb': GodStats('Geb', 'Tank', 'Magical', 7, 6, 6, 4, 7, 5, 3, 'B'),
            'Khepri': GodStats('Khepri', 'Tank', 'Magical', 6, 4, 8, 3, 6, 5, 4, 'A'),
            'Sobek': GodStats('Sobek', 'Tank', 'Magical', 8, 5, 5, 4, 7, 6, 3, 'B'),
            'Bacchus': GodStats('Bacchus', 'Tank', 'Magical', 9, 5, 6, 3, 8, 7, 4, 'A'),
            'Kumbhakarna': GodStats('Kumbhakarna', 'Tank', 'Magical', 10, 3, 7, 2, 7, 6, 3, 'B'),
            
            # Warriors
            'Chaac': GodStats('Chaac', 'Warrior', 'Physical', 5, 7, 8, 5, 6, 6, 2, 'B'),
            'Hercules': GodStats('Hercules', 'Warrior', 'Physical', 7, 6, 9, 4, 7, 7, 3, 'A'),
            'Sun Wukong': GodStats('Sun Wukong', 'Warrior', 'Physical', 6, 6, 6, 8, 6, 6, 4, 'A'),
            'Tyr': GodStats('Tyr', 'Warrior', 'Physical', 8, 6, 5, 6, 7, 6, 5, 'B'),
            'Bellona': GodStats('Bellona', 'Warrior', 'Physical', 6, 8, 6, 5, 8, 7, 4, 'A'),
            'Amaterasu': GodStats('Amaterasu', 'Warrior', 'Physical', 4, 7, 5, 6, 8, 8, 4, 'S'),
            'King Arthur': GodStats('King Arthur', 'Warrior', 'Physical', 7, 7, 6, 5, 8, 7, 6, 'A'),
            'Mulan': GodStats('Mulan', 'Warrior', 'Physical', 6, 7, 5, 6, 7, 7, 5, 'B'),
            
            # Mages
            'Zeus': GodStats('Zeus', 'Mage', 'Magical', 3, 9, 2, 2, 9, 8, 3, 'S'),
            'Poseidon': GodStats('Poseidon', 'Mage', 'Magical', 5, 8, 3, 6, 8, 7, 4, 'A'),
            'Scylla': GodStats('Scylla', 'Mage', 'Magical', 4, 7, 3, 7, 8, 9, 5, 'S'),
            'Kukulkan': GodStats('Kukulkan', 'Mage', 'Magical', 4, 8, 4, 5, 7, 8, 3, 'A'),
            'Anubis': GodStats('Anubis', 'Mage', 'Magical', 6, 9, 7, 2, 9, 8, 4, 'B'),
            'Ra': GodStats('Ra', 'Mage', 'Magical', 3, 8, 8, 5, 7, 7, 3, 'A'),
            'Thoth': GodStats('Thoth', 'Mage', 'Magical', 3, 8, 3, 6, 8, 8, 5, 'A'),
            'Merlin': GodStats('Merlin', 'Mage', 'Magical', 5, 9, 4, 4, 9, 8, 7, 'S'),
            'Agni': GodStats('Agni', 'Mage', 'Magical', 4, 8, 3, 6, 8, 7, 4, 'A'),
            'He Bo': GodStats('He Bo', 'Mage', 'Magical', 3, 7, 3, 5, 9, 7, 4, 'B'),
            
            # Hunters
            'Apollo': GodStats('Apollo', 'Hunter', 'Physical', 4, 8, 4, 8, 7, 8, 3, 'A'),
            'Artemis': GodStats('Artemis', 'Hunter', 'Physical', 5, 7, 3, 3, 8, 9, 3, 'A'),
            'Neith': GodStats('Neith', 'Hunter', 'Physical', 6, 7, 4, 6, 7, 7, 2, 'B'),
            'Rama': GodStats('Rama', 'Hunter', 'Physical', 3, 8, 3, 5, 8, 8, 4, 'A'),
            'Anhur': GodStats('Anhur', 'Hunter', 'Physical', 6, 7, 3, 5, 7, 7, 4, 'B'),
            'Hou Yi': GodStats('Hou Yi', 'Hunter', 'Physical', 5, 7, 3, 4, 8, 8, 4, 'A'),
            'Jing Wei': GodStats('Jing Wei', 'Hunter', 'Physical', 3, 8, 4, 9, 7, 8, 5, 'A'),
            'Cernunnos': GodStats('Cernunnos', 'Hunter', 'Physical', 4, 8, 4, 5, 8, 8, 4, 'S'),
            'Hachiman': GodStats('Hachiman', 'Hunter', 'Physical', 4, 8, 5, 6, 8, 8, 3, 'A'),
            
            # Assassins
            'Loki': GodStats('Loki', 'Assassin', 'Physical', 2, 6, 2, 8, 6, 7, 3, 'C'),
            'Thor': GodStats('Thor', 'Assassin', 'Physical', 7, 6, 4, 9, 7, 6, 4, 'A'),
            'Fenrir': GodStats('Fenrir', 'Assassin', 'Physical', 6, 5, 4, 7, 7, 6, 3, 'B'),
            'Hun Batz': GodStats('Hun Batz', 'Assassin', 'Physical', 8, 5, 3, 8, 8, 6, 4, 'A'),
            'Susano': GodStats('Susano', 'Assassin', 'Physical', 5, 6, 3, 9, 7, 6, 5, 'A'),
            'Kali': GodStats('Kali', 'Assassin', 'Physical', 2, 4, 5, 6, 6, 9, 5, 'B'),
            'Serqet': GodStats('Serqet', 'Assassin', 'Physical', 6, 5, 3, 8, 7, 7, 6, 'A'),
            'Da Ji': GodStats('Da Ji', 'Assassin', 'Physical', 7, 5, 3, 7, 7, 6, 4, 'B'),
            
            # Supports/Healers
            'Aphrodite': GodStats('Aphrodite', 'Support', 'Magical', 4, 5, 10, 4, 6, 7, 4, 'A'),
            'Chang\'e': GodStats('Chang\'e', 'Support', 'Magical', 3, 7, 9, 7, 6, 7, 4, 'A'),
            'Hel': GodStats('Hel', 'Support', 'Magical', 4, 6, 10, 5, 7, 8, 6, 'S'),
            'Sylvanus': GodStats('Sylvanus', 'Support', 'Magical', 7, 5, 8, 3, 6, 6, 4, 'B'),
            'Terra': GodStats('Terra', 'Support', 'Magical', 8, 5, 7, 4, 7, 6, 5, 'A'),
            'Yemoja': GodStats('Yemoja', 'Support', 'Magical', 6, 4, 9, 5, 7, 7, 7, 'S'),
            'Baron Samedi': GodStats('Baron Samedi', 'Support', 'Magical', 6, 6, 8, 4, 7, 7, 5, 'A'),
        }
        
        if god_file.exists():
            try:
                with open(god_file, 'r') as f:
                    data = json.load(f)
                    # Convert dict data to GodStats objects
                    god_stats = {}
                    for name, stats in data.get('god_data', {}).items():
                        god_stats[name] = GodStats(**stats)
                    return god_stats if god_stats else default_data
            except Exception as e:
                logger.warning(f"Failed to load god database: {e}")
                
        return default_data
        
    def _load_meta_weights(self) -> Dict[str, float]:
        """Load current meta weights for different aspects"""
        return {
            'cc_importance': 1.3,      # CC is very important in Assault
            'sustain_importance': 1.5,  # Healing is crucial
            'clear_importance': 1.1,    # Wave clear matters
            'team_fight_importance': 1.4, # Team fights are everything
            'late_game_importance': 1.2,  # Games go long
            'role_balance_importance': 1.3, # Balanced comps win
            'damage_split_importance': 1.1  # Physical/magical balance
        }
        
    def _load_synergy_matrix(self) -> Dict[Tuple[str, str], float]:
        """Load god synergy matrix"""
        # Simplified synergy matrix - in practice, this would be much larger
        return {
            ('Ares', 'Zeus'): 1.3,      # Ares ult + Zeus combo
            ('Ares', 'Poseidon'): 1.2,  # Ares ult + Poseidon combo
            ('Hel', 'Zeus'): 1.2,       # Hel heal + Zeus damage
            ('Aphrodite', 'Artemis'): 1.2, # Aphrodite link + Artemis
            ('Kumbhakarna', 'Scylla'): 1.3, # Kumbha setup + Scylla burst
            ('Athena', 'Thor'): 1.2,    # Global presence
            ('Ymir', 'Anubis'): 1.2,    # Ymir wall + Anubis combo
        }
        
    def analyze_matchup(self, team1: List[str], team2: List[str]) -> Dict[str, Any]:
        """Perform comprehensive matchup analysis"""
        # Analyze both teams
        team1_analysis = self._analyze_team(team1)
        team2_analysis = self._analyze_team(team2)
        
        # Calculate win probability
        win_probability = self._calculate_win_probability(team1_analysis, team2_analysis)
        
        # Generate comparative analysis
        comparison = self._compare_teams(team1_analysis, team2_analysis)
        
        return {
            'team1_score': team1_analysis.overall_score,
            'team2_score': team2_analysis.overall_score,
            'win_probability': win_probability,
            'team1_strengths': comparison['team1_strengths'],
            'team1_weaknesses': comparison['team1_weaknesses'],
            'team2_strengths': comparison['team2_strengths'],
            'team2_weaknesses': comparison['team2_weaknesses'],
            'key_factors': comparison['key_factors'],
            'detailed_analysis': {
                'team1': team1_analysis,
                'team2': team2_analysis
            }
        }
        
    def _analyze_team(self, team: List[str]) -> TeamAnalysis:
        """Perform detailed analysis of a single team"""
        if not team:
            return TeamAnalysis(0, {}, {}, 0, 0, 0, 0, 0, [], [])
            
        # Get god stats
        god_stats = [self.god_data.get(god) for god in team if god in self.god_data]
        god_stats = [g for g in god_stats if g is not None]
        
        if not god_stats:
            return TeamAnalysis(0, {}, {}, 0, 0, 0, 0, 0, [], [])
            
        # Calculate role distribution
        role_dist = Counter(god.role for god in god_stats)
        
        # Calculate damage split
        damage_split = Counter(god.damage_type for god in god_stats)
        
        # Calculate aggregate scores
        cc_potential = sum(god.cc_score for god in god_stats)
        clear_potential = sum(god.clear_score for god in god_stats)
        sustain_potential = sum(god.sustain_score for god in god_stats)
        team_fight_score = sum(god.team_fight_score for god in god_stats)
        late_game_scaling = sum(god.late_game_score for god in god_stats)
        
        # Calculate synergies
        synergy_bonus = self._calculate_synergies(team)
        
        # Calculate overall score
        overall_score = self._calculate_team_score(
            role_dist, damage_split, cc_potential, clear_potential,
            sustain_potential, team_fight_score, late_game_scaling, synergy_bonus
        )
        
        # Identify strengths and weaknesses
        strengths, weaknesses = self._identify_team_traits(
            role_dist, damage_split, cc_potential, clear_potential,
            sustain_potential, team_fight_score, late_game_scaling, god_stats
        )
        
        return TeamAnalysis(
            overall_score=overall_score,
            role_distribution=dict(role_dist),
            damage_split=dict(damage_split),
            cc_potential=cc_potential,
            clear_potential=clear_potential,
            sustain_potential=sustain_potential,
            team_fight_score=team_fight_score,
            late_game_scaling=late_game_scaling,
            strengths=strengths,
            weaknesses=weaknesses
        )
        
    def _calculate_synergies(self, team: List[str]) -> float:
        """Calculate team synergy bonus"""
        synergy_score = 0.0
        
        # Check all god pairs for synergies
        for i, god1 in enumerate(team):
            for god2 in team[i+1:]:
                # Check both directions
                synergy = self.synergy_matrix.get((god1, god2), 0)
                if synergy == 0:
                    synergy = self.synergy_matrix.get((god2, god1), 0)
                synergy_score += synergy
                
        return synergy_score
        
    def _calculate_team_score(self, role_dist: Counter, damage_split: Counter,
                            cc_potential: int, clear_potential: int,
                            sustain_potential: int, team_fight_score: int,
                            late_game_scaling: int, synergy_bonus: float) -> float:
        """Calculate overall team score using meta weights"""
        base_score = 50.0  # Starting score
        
        # Role balance scoring
        ideal_roles = {'Tank': 1, 'Warrior': 1, 'Mage': 1, 'Hunter': 1, 'Support': 1}
        role_balance_score = 0
        for role, ideal_count in ideal_roles.items():
            actual_count = role_dist.get(role, 0)
            if actual_count == ideal_count:
                role_balance_score += 10
            elif actual_count == 0:
                role_balance_score -= 15  # Missing role penalty
            else:
                role_balance_score += 5   # Partial credit
                
        # Damage split scoring (ideal: 2-3 physical, 2-3 magical)
        physical_count = damage_split.get('Physical', 0)
        magical_count = damage_split.get('Magical', 0)
        
        damage_balance_score = 0
        if 2 <= physical_count <= 3 and 2 <= magical_count <= 3:
            damage_balance_score = 10
        elif physical_count == 0 or magical_count == 0:
            damage_balance_score = -10  # All one damage type
        else:
            damage_balance_score = 5
            
        # Capability scoring
        cc_score = min(cc_potential * 0.8, 25)  # Cap at 25
        clear_score = min(clear_potential * 0.6, 20)
        sustain_score = min(sustain_potential * 1.0, 30)  # Sustain is very important
        team_fight_score_weighted = min(team_fight_score * 0.7, 25)
        late_game_score = min(late_game_scaling * 0.5, 15)
        
        # Apply meta weights
        weights = self.meta_weights
        final_score = (
            base_score +
            role_balance_score * weights['role_balance_importance'] +
            damage_balance_score * weights['damage_split_importance'] +
            cc_score * weights['cc_importance'] +
            clear_score * weights['clear_importance'] +
            sustain_score * weights['sustain_importance'] +
            team_fight_score_weighted * weights['team_fight_importance'] +
            late_game_score * weights['late_game_importance'] +
            synergy_bonus * 5  # Synergy bonus
        )
        
        return max(0, min(100, final_score))  # Clamp between 0-100
        
    def _identify_team_traits(self, role_dist: Counter, damage_split: Counter,
                            cc_potential: int, clear_potential: int,
                            sustain_potential: int, team_fight_score: int,
                            late_game_scaling: int, god_stats: List[GodStats]) -> Tuple[List[str], List[str]]:
        """Identify team strengths and weaknesses"""
        strengths = []
        weaknesses = []
        
        # Role analysis
        if role_dist.get('Tank', 0) >= 2:
            strengths.append("Strong frontline presence")
        elif role_dist.get('Tank', 0) == 0:
            weaknesses.append("No tank - vulnerable to dive")
            
        if role_dist.get('Support', 0) >= 1:
            strengths.append("Healing/sustain support")
        elif sustain_potential < 10:
            weaknesses.append("Limited sustain options")
            
        # Damage analysis
        physical_count = damage_split.get('Physical', 0)
        magical_count = damage_split.get('Magical', 0)
        
        if physical_count >= 4:
            weaknesses.append("Heavy physical - enemy can stack physical defense")
        elif magical_count >= 4:
            weaknesses.append("Heavy magical - enemy can stack magical defense")
        elif 2 <= physical_count <= 3:
            strengths.append("Balanced damage types")
            
        # Capability analysis
        if cc_potential >= 35:
            strengths.append("Excellent crowd control")
        elif cc_potential <= 15:
            weaknesses.append("Limited crowd control")
            
        if sustain_potential >= 25:
            strengths.append("Strong healing/sustain")
        elif sustain_potential <= 8:
            weaknesses.append("Poor sustain - vulnerable to poke")
            
        if team_fight_score >= 35:
            strengths.append("Dominant team fighting")
        elif team_fight_score <= 20:
            weaknesses.append("Weak team fight presence")
            
        if late_game_scaling >= 35:
            strengths.append("Excellent late game scaling")
        elif late_game_scaling <= 20:
            weaknesses.append("Falls off late game")
            
        if clear_potential >= 35:
            strengths.append("Superior wave clear")
        elif clear_potential <= 20:
            weaknesses.append("Poor wave clear")
            
        # Meta tier analysis
        s_tier_count = sum(1 for god in god_stats if god.meta_tier == 'S')
        if s_tier_count >= 2:
            strengths.append(f"{s_tier_count} S-tier gods")
            
        c_tier_count = sum(1 for god in god_stats if god.meta_tier == 'C')
        if c_tier_count >= 2:
            weaknesses.append(f"{c_tier_count} off-meta picks")
            
        return strengths, weaknesses
        
    def _calculate_win_probability(self, team1: TeamAnalysis, team2: TeamAnalysis) -> float:
        """Calculate win probability for team1 vs team2"""
        score_diff = team1.overall_score - team2.overall_score
        
        # Convert score difference to probability using sigmoid function
        # This creates a smooth curve where small differences = ~50%, large differences = extreme probabilities
        probability = 1 / (1 + math.exp(-score_diff / 10))
        
        # Clamp to reasonable bounds (10% - 90%)
        return max(0.1, min(0.9, probability))
        
    def _compare_teams(self, team1: TeamAnalysis, team2: TeamAnalysis) -> Dict[str, List[str]]:
        """Generate comparative analysis between teams"""
        comparison = {
            'team1_strengths': [],
            'team1_weaknesses': [],
            'team2_strengths': [],
            'team2_weaknesses': [],
            'key_factors': []
        }
        
        # Compare capabilities
        if team1.cc_potential > team2.cc_potential + 10:
            comparison['team1_strengths'].append("Superior crowd control")
            comparison['key_factors'].append("Team 1 wins fights with CC chains")
        elif team2.cc_potential > team1.cc_potential + 10:
            comparison['team2_strengths'].append("Superior crowd control")
            comparison['key_factors'].append("Team 2 wins fights with CC chains")
            
        if team1.sustain_potential > team2.sustain_potential + 8:
            comparison['team1_strengths'].append("Much better sustain")
            comparison['key_factors'].append("Team 1 outlasts in extended fights")
        elif team2.sustain_potential > team1.sustain_potential + 8:
            comparison['team2_strengths'].append("Much better sustain")
            comparison['key_factors'].append("Team 2 outlasts in extended fights")
            
        if team1.team_fight_score > team2.team_fight_score + 8:
            comparison['team1_strengths'].append("Stronger team fighting")
        elif team2.team_fight_score > team1.team_fight_score + 8:
            comparison['team2_strengths'].append("Stronger team fighting")
            
        if team1.late_game_scaling > team2.late_game_scaling + 8:
            comparison['team1_strengths'].append("Better late game scaling")
            comparison['key_factors'].append("Team 1 gets stronger as game progresses")
        elif team2.late_game_scaling > team1.late_game_scaling + 8:
            comparison['team2_strengths'].append("Better late game scaling")
            comparison['key_factors'].append("Team 2 gets stronger as game progresses")
            
        # Add team-specific weaknesses from analysis
        comparison['team1_weaknesses'].extend(team1.weaknesses)
        comparison['team2_weaknesses'].extend(team2.weaknesses)
        
        # Add team-specific strengths from analysis
        comparison['team1_strengths'].extend(team1.strengths)
        comparison['team2_strengths'].extend(team2.strengths)
        
        return comparison

import math  # Add this import at the top