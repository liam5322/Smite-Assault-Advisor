"""
Intelligent build suggestion system with contextual recommendations
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ItemType(Enum):
    """Item categories for build suggestions"""
    STARTER = "starter"
    CORE = "core"
    SITUATIONAL = "situational"
    LUXURY = "luxury"
    RELIC = "relic"

class Priority(Enum):
    """Priority levels for build suggestions"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class ItemSuggestion:
    """Individual item suggestion with context"""
    name: str
    item_type: ItemType
    priority: Priority
    reason: str
    cost: int
    stats: List[str]
    alternatives: List[str]

@dataclass
class BuildSuggestion:
    """Complete build suggestion for a god"""
    god: str
    role: str
    start_items: List[ItemSuggestion]
    core_build: List[ItemSuggestion]
    situational_items: List[ItemSuggestion]
    relics: List[ItemSuggestion]
    tips: List[str]
    priority_order: List[str]
    total_cost: int

class BuildSuggester:
    """Intelligent build suggestion system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.item_database = self._load_item_database()
        self.build_templates = self._load_build_templates()
        self.counter_items = self._load_counter_items()
        
        logger.info(f"Build suggester initialized with {len(self.item_database)} items")
        
    def _load_item_database(self) -> Dict[str, Dict[str, Any]]:
        """Load comprehensive item database"""
        item_file = Path(__file__).parent.parent.parent / 'assets' / 'items.json'
        
        # Comprehensive SMITE 2 item database
        default_items = {
            # Starter Items
            'Conduit Gem': {
                'type': 'starter',
                'cost': 650,
                'stats': ['Magical Power', 'MP5', 'Magical Penetration'],
                'passive': 'Evolves into Archmage\'s Gem',
                'roles': ['Mage'],
                'tier': 1
            },
            'Death\'s Toll': {
                'type': 'starter',
                'cost': 650,
                'stats': ['Physical Power', 'Health', 'HP5'],
                'passive': 'Heal on basic attacks',
                'roles': ['Hunter', 'Assassin'],
                'tier': 1
            },
            'Warrior\'s Axe': {
                'type': 'starter',
                'cost': 650,
                'stats': ['Physical Power', 'Health', 'HP5'],
                'passive': 'Damage reduction and cleave',
                'roles': ['Warrior'],
                'tier': 1
            },
            'Guardian\'s Blessing': {
                'type': 'starter',
                'cost': 650,
                'stats': ['Health', 'MP5', 'HP5'],
                'passive': 'Damage mitigation',
                'roles': ['Tank'],
                'tier': 1
            },
            
            # Core Magical Items
            'Archmage\'s Gem': {
                'type': 'core',
                'cost': 2500,
                'stats': ['High Magical Power', 'Magical Penetration', 'MP5'],
                'passive': 'Spell proc effects',
                'roles': ['Mage'],
                'tier': 2
            },
            'Spear of Desolation': {
                'type': 'core',
                'cost': 2700,
                'stats': ['Magical Power', 'Magical Penetration'],
                'passive': 'Cooldown reduction on kills',
                'roles': ['Mage'],
                'tier': 2
            },
            'Soul Reaver': {
                'type': 'core',
                'cost': 2750,
                'stats': ['Magical Power', 'Health'],
                'passive': 'Max health damage',
                'roles': ['Mage'],
                'tier': 2
            },
            'Rod of Tahuti': {
                'type': 'luxury',
                'cost': 3000,
                'stats': ['Very High Magical Power'],
                'passive': 'Increased damage to low health enemies',
                'roles': ['Mage'],
                'tier': 3
            },
            
            # Core Physical Items
            'Devourer\'s Gauntlet': {
                'type': 'core',
                'cost': 2300,
                'stats': ['Physical Power', 'Lifesteal'],
                'passive': 'Stacking power and lifesteal',
                'roles': ['Hunter'],
                'tier': 2
            },
            'Executioner': {
                'type': 'core',
                'cost': 2300,
                'stats': ['Physical Power', 'Attack Speed'],
                'passive': 'Protection reduction',
                'roles': ['Hunter', 'Assassin'],
                'tier': 2
            },
            'Qin\'s Sais': {
                'type': 'core',
                'cost': 2600,
                'stats': ['Physical Power', 'Attack Speed'],
                'passive': 'Max health damage',
                'roles': ['Hunter', 'Assassin'],
                'tier': 2
            },
            'Deathbringer': {
                'type': 'luxury',
                'cost': 2800,
                'stats': ['Physical Power', 'Critical Chance'],
                'passive': 'Increased critical damage',
                'roles': ['Hunter', 'Assassin'],
                'tier': 3
            },
            
            # Defense Items
            'Breastplate of Valor': {
                'type': 'core',
                'cost': 2300,
                'stats': ['Physical Defense', 'Cooldown Reduction', 'Mana'],
                'passive': 'None',
                'roles': ['Tank', 'Warrior'],
                'tier': 2
            },
            'Genji\'s Guard': {
                'type': 'core',
                'cost': 2300,
                'stats': ['Magical Defense', 'Cooldown Reduction', 'HP5', 'MP5'],
                'passive': 'Cooldown reduction on taking magical damage',
                'roles': ['Tank', 'Warrior'],
                'tier': 2
            },
            'Sovereignty': {
                'type': 'core',
                'cost': 2150,
                'stats': ['Health', 'Physical Defense'],
                'passive': 'Aura - team physical defense',
                'roles': ['Tank'],
                'tier': 2
            },
            'Heartward Amulet': {
                'type': 'core',
                'cost': 2150,
                'stats': ['Health', 'Magical Defense'],
                'passive': 'Aura - team magical defense',
                'roles': ['Tank'],
                'tier': 2
            },
            
            # Counter Items
            'Divine Ruin': {
                'type': 'situational',
                'cost': 2300,
                'stats': ['Magical Power', 'Magical Penetration'],
                'passive': 'Antiheal on ability damage',
                'roles': ['Mage'],
                'tier': 2,
                'counters': ['healing']
            },
            'Brawler\'s Beat Stick': {
                'type': 'situational',
                'cost': 2350,
                'stats': ['Physical Power', 'Physical Penetration'],
                'passive': 'Antiheal on physical damage',
                'roles': ['Hunter', 'Assassin', 'Warrior'],
                'tier': 2,
                'counters': ['healing']
            },
            'Pestilence': {
                'type': 'situational',
                'cost': 2250,
                'stats': ['Health', 'Magical Defense'],
                'passive': 'Aura - antiheal',
                'roles': ['Tank'],
                'tier': 2,
                'counters': ['healing']
            },
            'Spectral Armor': {
                'type': 'situational',
                'cost': 2250,
                'stats': ['Health', 'Physical Defense'],
                'passive': 'Critical damage reduction',
                'roles': ['Tank', 'Warrior'],
                'tier': 2,
                'counters': ['critical']
            },
            'Nemean Lion': {
                'type': 'situational',
                'cost': 2200,
                'stats': ['Physical Defense', 'MP5'],
                'passive': 'Reflect basic attack damage',
                'roles': ['Tank'],
                'tier': 2,
                'counters': ['basic_attacks']
            },
            
            # Relics
            'Purification Beads': {
                'type': 'relic',
                'cost': 0,
                'stats': [],
                'passive': 'CC immunity',
                'roles': ['All'],
                'tier': 1,
                'counters': ['cc']
            },
            'Aegis Amulet': {
                'type': 'relic',
                'cost': 0,
                'stats': [],
                'passive': 'Damage immunity',
                'roles': ['All'],
                'tier': 1,
                'counters': ['burst']
            },
            'Meditation Cloak': {
                'type': 'relic',
                'cost': 0,
                'stats': [],
                'passive': 'Heal and mana restore',
                'roles': ['All'],
                'tier': 1,
                'counters': ['sustain']
            },
            'Blink Rune': {
                'type': 'relic',
                'cost': 0,
                'stats': [],
                'passive': 'Teleport',
                'roles': ['Tank', 'Assassin'],
                'tier': 1,
                'counters': ['positioning']
            }
        }
        
        if item_file.exists():
            try:
                with open(item_file, 'r') as f:
                    data = json.load(f)
                    return data.get('items', default_items)
            except Exception as e:
                logger.warning(f"Failed to load item database: {e}")
                
        return default_items
        
    def _load_build_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load build templates for each god/role"""
        # Comprehensive build templates
        return {
            # Mage builds
            'Zeus': {
                'start': ['Conduit Gem', 'Lost Artifact', 'Healing Potion', 'Mana Potion'],
                'core': ['Archmage\'s Gem', 'Spear of Desolation', 'Soul Reaver'],
                'situational': ['Divine Ruin', 'Obsidian Shard', 'Ethereal Staff'],
                'luxury': ['Rod of Tahuti', 'Soul Gem'],
                'boots': 'Shoes of the Magi',
                'relics': ['Purification Beads', 'Aegis Amulet']
            },
            'Poseidon': {
                'start': ['Conduit Gem', 'Lost Artifact', 'Healing Potion', 'Mana Potion'],
                'core': ['Archmage\'s Gem', 'Spear of Desolation', 'Soul Reaver'],
                'situational': ['Divine Ruin', 'Gem of Isolation', 'Ethereal Staff'],
                'luxury': ['Rod of Tahuti', 'Polynomicon'],
                'boots': 'Shoes of the Magi',
                'relics': ['Purification Beads', 'Aegis Amulet']
            },
            'Scylla': {
                'start': ['Conduit Gem', 'Lost Artifact', 'Healing Potion', 'Mana Potion'],
                'core': ['Archmage\'s Gem', 'Spear of Desolation', 'Soul Reaver'],
                'situational': ['Divine Ruin', 'Obsidian Shard', 'Ethereal Staff'],
                'luxury': ['Rod of Tahuti', 'Soul Gem'],
                'boots': 'Shoes of the Magi',
                'relics': ['Purification Beads', 'Aegis Amulet']
            },
            
            # Hunter builds
            'Apollo': {
                'start': ['Death\'s Toll', 'Short Sword', 'Healing Potion', 'Mana Potion'],
                'core': ['Devourer\'s Gauntlet', 'Executioner', 'Qin\'s Sais'],
                'situational': ['Brawler\'s Beat Stick', 'Titan\'s Bane', 'Odysseus\' Bow'],
                'luxury': ['Deathbringer', 'Silverbranch Bow'],
                'boots': 'Warrior Tabi',
                'relics': ['Purification Beads', 'Aegis Amulet']
            },
            'Artemis': {
                'start': ['Death\'s Toll', 'Short Sword', 'Healing Potion', 'Mana Potion'],
                'core': ['Devourer\'s Gauntlet', 'Executioner', 'Deathbringer'],
                'situational': ['Brawler\'s Beat Stick', 'Qin\'s Sais', 'Odysseus\' Bow'],
                'luxury': ['Silverbranch Bow', 'Titan\'s Bane'],
                'boots': 'Warrior Tabi',
                'relics': ['Purification Beads', 'Aegis Amulet']
            },
            
            # Tank builds
            'Ymir': {
                'start': ['Guardian\'s Blessing', 'Iron Mail', 'Healing Potion', 'Multi Potion'],
                'core': ['Sovereignty', 'Heartward Amulet', 'Breastplate of Valor'],
                'situational': ['Pestilence', 'Spectral Armor', 'Spirit Robe'],
                'luxury': ['Mantle of Discord', 'Ethereal Staff'],
                'boots': 'Shoes of Focus',
                'relics': ['Blink Rune', 'Meditation Cloak']
            },
            'Ares': {
                'start': ['Guardian\'s Blessing', 'Iron Mail', 'Healing Potion', 'Multi Potion'],
                'core': ['Sovereignty', 'Heartward Amulet', 'Void Stone'],
                'situational': ['Pestilence', 'Mystical Mail', 'Spirit Robe'],
                'luxury': ['Ethereal Staff', 'Soul Reaver'],
                'boots': 'Shoes of Focus',
                'relics': ['Blink Rune', 'Meditation Cloak']
            },
            
            # Support builds
            'Aphrodite': {
                'start': ['Conduit Gem', 'Lost Artifact', 'Healing Potion', 'Mana Potion'],
                'core': ['Archmage\'s Gem', 'Lotus Crown', 'Rod of Asclepius'],
                'situational': ['Divine Ruin', 'Ethereal Staff', 'Spirit Robe'],
                'luxury': ['Rod of Tahuti', 'Soul Gem'],
                'boots': 'Shoes of Focus',
                'relics': ['Meditation Cloak', 'Purification Beads']
            },
            'Hel': {
                'start': ['Conduit Gem', 'Lost Artifact', 'Healing Potion', 'Mana Potion'],
                'core': ['Archmage\'s Gem', 'Lotus Crown', 'Rod of Asclepius'],
                'situational': ['Divine Ruin', 'Ethereal Staff', 'Breastplate of Valor'],
                'luxury': ['Rod of Tahuti', 'Soul Gem'],
                'boots': 'Shoes of Focus',
                'relics': ['Meditation Cloak', 'Purification Beads']
            }
        }
        
    def _load_counter_items(self) -> Dict[str, List[str]]:
        """Load counter item recommendations"""
        return {
            'healing': ['Divine Ruin', 'Brawler\'s Beat Stick', 'Pestilence'],
            'critical': ['Spectral Armor', 'Nemean Lion'],
            'basic_attacks': ['Nemean Lion', 'Spectral Armor', 'Midgardian Mail'],
            'burst_damage': ['Aegis Amulet', 'Magi\'s Cloak', 'Spirit Robe'],
            'crowd_control': ['Purification Beads', 'Magi\'s Cloak', 'Spirit Robe'],
            'magical_damage': ['Genji\'s Guard', 'Heartward Amulet', 'Bulwark of Hope'],
            'physical_damage': ['Breastplate of Valor', 'Sovereignty', 'Midgardian Mail']
        }
        
    def suggest_build(self, god: str, enemy_team: List[str], ally_team: List[str] = None) -> BuildSuggestion:
        """Generate comprehensive build suggestion"""
        # Get base build template
        template = self.build_templates.get(god, self._get_generic_template(god))
        
        # Analyze enemy threats
        threats = self._analyze_threats(enemy_team)
        
        # Analyze ally synergies
        synergies = self._analyze_ally_synergies(ally_team or [])
        
        # Generate contextual suggestions
        suggestions = self._generate_suggestions(god, template, threats, synergies)
        
        return suggestions
        
    def _get_generic_template(self, god: str) -> Dict[str, List[str]]:
        """Get generic build template based on god role"""
        # This would normally query the god database for role
        # For now, return a basic template
        return {
            'start': ['Conduit Gem', 'Lost Artifact', 'Healing Potion'],
            'core': ['Archmage\'s Gem', 'Spear of Desolation', 'Soul Reaver'],
            'situational': ['Divine Ruin', 'Obsidian Shard'],
            'luxury': ['Rod of Tahuti'],
            'boots': 'Shoes of the Magi',
            'relics': ['Purification Beads', 'Aegis Amulet']
        }
        
    def _analyze_threats(self, enemy_team: List[str]) -> Dict[str, int]:
        """Analyze enemy team threats"""
        threats = {
            'healing': 0,
            'critical': 0,
            'burst_damage': 0,
            'crowd_control': 0,
            'basic_attacks': 0,
            'magical_damage': 0,
            'physical_damage': 0
        }
        
        # Threat analysis based on enemy gods
        healing_gods = ['Aphrodite', 'Chang\'e', 'Hel', 'Ra', 'Sylvanus', 'Terra', 'Yemoja', 'Baron Samedi']
        cc_heavy_gods = ['Ares', 'Kumbhakarna', 'Nox', 'Hun Batz', 'Cerberus', 'Ymir']
        crit_gods = ['Artemis', 'Jing Wei', 'Ne Zha']
        burst_gods = ['Zeus', 'Scylla', 'He Bo', 'Poseidon', 'Loki']
        
        for enemy in enemy_team:
            if enemy in healing_gods:
                threats['healing'] += 2 if enemy in ['Hel', 'Aphrodite', 'Chang\'e'] else 1
            if enemy in cc_heavy_gods:
                threats['crowd_control'] += 2 if enemy in ['Ares', 'Kumbhakarna'] else 1
            if enemy in crit_gods:
                threats['critical'] += 2
            if enemy in burst_gods:
                threats['burst_damage'] += 2 if enemy in ['Zeus', 'Scylla'] else 1
                
        return threats
        
    def _analyze_ally_synergies(self, ally_team: List[str]) -> Dict[str, int]:
        """Analyze ally team synergies"""
        synergies = {
            'aura_items': 0,
            'healing_boost': 0,
            'protection_sharing': 0
        }
        
        # Check for gods that benefit from auras
        aura_beneficiaries = ['Zeus', 'Poseidon', 'Artemis', 'Apollo']
        healing_gods = ['Aphrodite', 'Chang\'e', 'Hel', 'Ra']
        
        for ally in ally_team:
            if ally in aura_beneficiaries:
                synergies['aura_items'] += 1
            if ally in healing_gods:
                synergies['healing_boost'] += 1
                
        return synergies
        
    def _generate_suggestions(self, god: str, template: Dict[str, List[str]], 
                           threats: Dict[str, int], synergies: Dict[str, int]) -> BuildSuggestion:
        """Generate final build suggestions with priorities"""
        
        # Start with base template
        start_items = self._create_item_suggestions(template['start'], ItemType.STARTER, Priority.HIGH)
        core_build = self._create_item_suggestions(template['core'], ItemType.CORE, Priority.HIGH)
        
        # Add situational items based on threats
        situational_items = []
        tips = []
        
        # Antiheal priority
        if threats['healing'] >= 3:
            priority = Priority.CRITICAL
            tips.append("🚫 CRITICAL: Enemy has multiple healers - BUILD ANTIHEAL IMMEDIATELY")
        elif threats['healing'] >= 2:
            priority = Priority.HIGH
            tips.append("⚠️ Enemy has strong healing - antiheal recommended")
        elif threats['healing'] >= 1:
            priority = Priority.MEDIUM
            tips.append("💡 Consider antiheal for enemy healer")
        else:
            priority = None
            
        if priority:
            antiheal_items = self.counter_items['healing']
            for item in antiheal_items:
                if item in self.item_database:
                    item_data = self.item_database[item]
                    if god in ['Zeus', 'Poseidon', 'Scylla']:  # Mages
                        if item == 'Divine Ruin':
                            situational_items.append(ItemSuggestion(
                                name=item,
                                item_type=ItemType.SITUATIONAL,
                                priority=priority,
                                reason=f"Counter enemy healing ({threats['healing']} healers)",
                                cost=item_data['cost'],
                                stats=item_data['stats'],
                                alternatives=['Brawler\'s Beat Stick'] if priority == Priority.CRITICAL else []
                            ))
                            break
                            
        # CC immunity priority
        if threats['crowd_control'] >= 3:
            tips.append("🔮 MANDATORY: Purification Beads - enemy has heavy CC")
        elif threats['crowd_control'] >= 2:
            tips.append("🔮 Strongly recommend Purification Beads")
            
        # Critical counter
        if threats['critical'] >= 2:
            tips.append("🛡️ Consider Spectral Armor vs enemy critical damage")
            
        # Burst protection
        if threats['burst_damage'] >= 3:
            tips.append("🛡️ Aegis Amulet recommended vs high burst damage")
            
        # Generate relics
        relics = []
        if threats['crowd_control'] >= 1:
            relics.append(ItemSuggestion(
                name='Purification Beads',
                item_type=ItemType.RELIC,
                priority=Priority.CRITICAL if threats['crowd_control'] >= 2 else Priority.HIGH,
                reason="CC immunity",
                cost=0,
                stats=[],
                alternatives=[]
            ))
            
        if threats['burst_damage'] >= 2:
            relics.append(ItemSuggestion(
                name='Aegis Amulet',
                item_type=ItemType.RELIC,
                priority=Priority.HIGH,
                reason="Burst protection",
                cost=0,
                stats=[],
                alternatives=['Meditation Cloak']
            ))
        else:
            relics.append(ItemSuggestion(
                name='Meditation Cloak',
                item_type=ItemType.RELIC,
                priority=Priority.MEDIUM,
                reason="Sustain in Assault",
                cost=0,
                stats=[],
                alternatives=['Aegis Amulet']
            ))
            
        # Calculate total cost
        total_cost = sum(item.cost for item in start_items + core_build + situational_items)
        
        # Priority order
        priority_order = []
        if threats['healing'] >= 2:
            priority_order.append("1. Antiheal item")
        priority_order.extend([f"{i+1}. {item.name}" for i, item in enumerate(core_build)])
        
        return BuildSuggestion(
            god=god,
            role=self._get_god_role(god),
            start_items=start_items,
            core_build=core_build,
            situational_items=situational_items,
            relics=relics,
            tips=tips,
            priority_order=priority_order,
            total_cost=total_cost
        )
        
    def _create_item_suggestions(self, item_names: List[str], item_type: ItemType, 
                               priority: Priority) -> List[ItemSuggestion]:
        """Create ItemSuggestion objects from item names"""
        suggestions = []
        
        for item_name in item_names:
            if item_name in self.item_database:
                item_data = self.item_database[item_name]
                suggestions.append(ItemSuggestion(
                    name=item_name,
                    item_type=item_type,
                    priority=priority,
                    reason="Core build item",
                    cost=item_data['cost'],
                    stats=item_data['stats'],
                    alternatives=[]
                ))
                
        return suggestions
        
    def _get_god_role(self, god: str) -> str:
        """Get god's primary role"""
        # This would normally query the god database
        # For now, return a basic mapping
        role_mapping = {
            'Zeus': 'Mage',
            'Poseidon': 'Mage',
            'Scylla': 'Mage',
            'Apollo': 'Hunter',
            'Artemis': 'Hunter',
            'Ymir': 'Tank',
            'Ares': 'Tank',
            'Aphrodite': 'Support',
            'Hel': 'Support'
        }
        return role_mapping.get(god, 'Unknown')
        
    def get_counter_recommendations(self, threats: List[str]) -> List[ItemSuggestion]:
        """Get specific counter item recommendations"""
        recommendations = []
        
        for threat in threats:
            if threat in self.counter_items:
                for item_name in self.counter_items[threat]:
                    if item_name in self.item_database:
                        item_data = self.item_database[item_name]
                        recommendations.append(ItemSuggestion(
                            name=item_name,
                            item_type=ItemType.SITUATIONAL,
                            priority=Priority.HIGH,
                            reason=f"Counters {threat}",
                            cost=item_data['cost'],
                            stats=item_data['stats'],
                            alternatives=[]
                        ))
                        
        return recommendations