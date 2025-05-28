#!/usr/bin/env python3
"""
SMITE 2 Comprehensive Data Population Script
Adds all gods and items from the provided SMITE 2 data to the database.
"""

import sqlite3
import json
import re
from typing import Dict, List, Any, Optional

class SMITE2DataPopulator:
    def __init__(self, db_path: str = "assets/smite2_comprehensive.db"):
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """Connect to the database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        
    def disconnect(self):
        """Disconnect from the database"""
        if self.conn:
            self.conn.close()
            
    def clear_existing_data(self):
        """Clear existing gods and items data"""
        cursor = self.conn.cursor()
        
        # Clear in order due to foreign key constraints
        cursor.execute("DELETE FROM abilities")
        cursor.execute("DELETE FROM aspects")
        cursor.execute("DELETE FROM assault_matchups")
        cursor.execute("DELETE FROM gods")
        cursor.execute("DELETE FROM items")
        
        self.conn.commit()
        print("Cleared existing data")
        
    def parse_tier(self, tier_str: str) -> str:
        """Parse tier string to standard format"""
        tier_map = {
            'S+': 'S+', 'S': 'S', 'A': 'A', 'B': 'B', 'C': 'C', 'D': 'D'
        }
        return tier_map.get(tier_str.strip(), 'B')
        
    def parse_role(self, role_str: str) -> str:
        """Parse role string to primary role"""
        role_map = {
            'Warrior': 'Warrior',
            'Mage': 'Mage', 
            'Hunter': 'Hunter',
            'Assassin': 'Assassin',
            'Guardian': 'Guardian',
            'Support': 'Guardian'
        }
        
        # Handle hybrid roles like "Mage/Support"
        if '/' in role_str:
            primary = role_str.split('/')[0].strip()
        else:
            primary = role_str.strip()
            
        return role_map.get(primary, 'Mage')
        
    def calculate_scores(self, god_data: Dict) -> Dict[str, int]:
        """Calculate assault scores based on god data"""
        tier = god_data.get('assault_tier', 'B')
        role = god_data.get('primary_role', 'Mage')
        
        # Base scores by tier
        tier_base = {
            'S+': 9, 'S': 8, 'A': 7, 'B': 6, 'C': 5, 'D': 4
        }
        base = tier_base.get(tier, 6)
        
        # Role-specific adjustments
        scores = {
            'sustain_score': base,
            'team_fight_score': base,
            'poke_score': base,
            'wave_clear_score': base,
            'cc_score': base,
            'mobility_score': base,
            'late_game_score': base
        }
        
        # Adjust based on role
        if role == 'Guardian':
            scores['cc_score'] = min(10, base + 2)
            scores['sustain_score'] = min(10, base + 1)
            scores['mobility_score'] = max(1, base - 1)
        elif role == 'Mage':
            scores['poke_score'] = min(10, base + 2)
            scores['wave_clear_score'] = min(10, base + 1)
            scores['late_game_score'] = min(10, base + 1)
        elif role == 'Hunter':
            scores['late_game_score'] = min(10, base + 2)
            scores['poke_score'] = min(10, base + 1)
        elif role == 'Assassin':
            scores['mobility_score'] = min(10, base + 2)
            scores['sustain_score'] = max(1, base - 1)
        elif role == 'Warrior':
            scores['sustain_score'] = min(10, base + 1)
            scores['team_fight_score'] = min(10, base + 1)
            
        # Special adjustments for known gods
        name = god_data.get('name', '')
        if 'Aphrodite' in name or 'Ra' in name or 'Hel' in name:
            scores['sustain_score'] = 10
        if 'Anubis' in name or 'Zeus' in name or 'Merlin' in name:
            scores['poke_score'] = 10
            scores['team_fight_score'] = 9
        if 'Athena' in name or 'Ymir' in name or 'Geb' in name:
            scores['cc_score'] = 10
            
        return scores
        
    def add_god(self, god_data: Dict) -> int:
        """Add a god to the database"""
        cursor = self.conn.cursor()
        
        # Calculate scores
        scores = self.calculate_scores(god_data)
        
        # Prepare data
        assault_roles = json.dumps(god_data.get('assault_roles', [god_data.get('primary_role', 'Mage')]))
        assault_strengths = json.dumps(god_data.get('assault_strengths', []))
        assault_weaknesses = json.dumps(god_data.get('assault_weaknesses', []))
        recommended_items = json.dumps(god_data.get('recommended_items', []))
        counters = json.dumps(god_data.get('counters', []))
        synergies = json.dumps(god_data.get('synergies', []))
        assault_build_priority = json.dumps(god_data.get('assault_build_priority', []))
        
        cursor.execute("""
            INSERT INTO gods (
                name, pantheon, damage_type, primary_role, assault_tier,
                sustain_score, team_fight_score, poke_score, wave_clear_score,
                cc_score, mobility_score, late_game_score,
                assault_roles, assault_strengths, assault_weaknesses,
                recommended_items, counters, synergies, assault_build_priority
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            god_data['name'],
            god_data.get('pantheon', 'Unknown'),
            god_data.get('damage_type', 'Magical'),
            god_data['primary_role'],
            god_data['assault_tier'],
            scores['sustain_score'],
            scores['team_fight_score'],
            scores['poke_score'],
            scores['wave_clear_score'],
            scores['cc_score'],
            scores['mobility_score'],
            scores['late_game_score'],
            assault_roles,
            assault_strengths,
            assault_weaknesses,
            recommended_items,
            counters,
            synergies,
            assault_build_priority
        ))
        
        god_id = cursor.lastrowid
        
        # Add abilities
        for ability in god_data.get('abilities', []):
            self.add_ability(god_id, ability)
            
        return god_id
        
    def add_ability(self, god_id: int, ability_data: Dict):
        """Add an ability to the database"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO abilities (
                god_id, ability_type, name, description,
                damage_base, damage_scaling, cc_type, cc_duration,
                cooldown, cost, range_value, radius, cone_angle,
                duration, max_charges, channel_duration, additional_properties
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            god_id,
            ability_data.get('ability_type', 'ability_1'),
            ability_data.get('name', ''),
            ability_data.get('description', ''),
            ability_data.get('damage_base'),
            ability_data.get('damage_scaling'),
            ability_data.get('cc_type'),
            ability_data.get('cc_duration'),
            ability_data.get('cooldown'),
            ability_data.get('cost'),
            ability_data.get('range_value'),
            ability_data.get('radius'),
            ability_data.get('cone_angle'),
            ability_data.get('duration'),
            ability_data.get('max_charges'),
            ability_data.get('channel_duration'),
            json.dumps(ability_data.get('additional_properties', {}))
        ))
        
    def add_item(self, item_data: Dict):
        """Add an item to the database"""
        cursor = self.conn.cursor()
        
        # Determine assault priority
        assault_priority = self.determine_assault_priority(item_data)
        assault_utility = self.determine_assault_utility(item_data)
        
        cursor.execute("""
            INSERT INTO items (
                name, tier, cost, category,
                strength, intelligence, health, mana,
                physical_protection, magical_protection, attack_speed,
                physical_lifesteal, magical_lifesteal, hp5, mp5,
                cooldown_reduction, critical_chance,
                penetration_flat, penetration_percent,
                passive_name, passive_description,
                active_name, active_description, active_cooldown,
                assault_priority, assault_utility,
                recommended_for, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item_data['name'],
            item_data.get('tier', 3),
            item_data.get('cost', 0),
            item_data.get('category', 'utility'),
            item_data.get('strength', 0),
            item_data.get('intelligence', 0),
            item_data.get('health', 0),
            item_data.get('mana', 0),
            item_data.get('physical_protection', 0),
            item_data.get('magical_protection', 0),
            item_data.get('attack_speed', 0),
            item_data.get('physical_lifesteal', 0),
            item_data.get('magical_lifesteal', 0),
            item_data.get('hp5', 0),
            item_data.get('mp5', 0),
            item_data.get('cooldown_reduction', 0),
            item_data.get('critical_chance', 0),
            item_data.get('penetration_flat', 0),
            item_data.get('penetration_percent', 0),
            item_data.get('passive_name'),
            item_data.get('passive_description'),
            item_data.get('active_name'),
            item_data.get('active_description'),
            item_data.get('active_cooldown'),
            assault_priority,
            assault_utility,
            json.dumps(item_data.get('recommended_for', [])),
            item_data.get('notes', '')
        ))
        
    def determine_assault_priority(self, item_data: Dict) -> str:
        """Determine assault priority for an item"""
        name = item_data['name'].lower()
        category = item_data.get('category', '').lower()
        
        # Highest priority items
        if any(x in name for x in ['meditation', 'divine ruin', 'pestilence', 'contagion']):
            return 'Highest'
        if 'anti-heal' in item_data.get('notes', '').lower():
            return 'Mandatory vs healers'
        if category in ['sustain', 'defense'] or any(x in name for x in ['lifesteal', 'protection', 'health']):
            return 'High'
        if category in ['utility', 'situational']:
            return 'Situational'
        return 'Medium'
        
    def determine_assault_utility(self, item_data: Dict) -> str:
        """Determine assault utility for an item"""
        name = item_data['name'].lower()
        
        if any(x in name for x in ['heal', 'sustain', 'lifesteal']):
            return 'Sustain and healing'
        if any(x in name for x in ['protection', 'armor', 'guard']):
            return 'Defense and survivability'
        if any(x in name for x in ['power', 'damage', 'penetration']):
            return 'Damage and penetration'
        if any(x in name for x in ['cooldown', 'mana']):
            return 'Cooldown and mana management'
        return 'General utility'

    def populate_gods_data(self):
        """Populate all gods data"""
        gods_data = self.get_gods_data()
        
        for god_data in gods_data:
            try:
                god_id = self.add_god(god_data)
                print(f"Added god: {god_data['name']} (ID: {god_id})")
            except Exception as e:
                print(f"Error adding god {god_data['name']}: {e}")
                
        self.conn.commit()
        
    def populate_items_data(self):
        """Populate all items data"""
        items_data = self.get_items_data()
        
        for item_data in items_data:
            try:
                self.add_item(item_data)
                print(f"Added item: {item_data['name']}")
            except Exception as e:
                print(f"Error adding item {item_data['name']}: {e}")
                
        self.conn.commit()

    def get_gods_data(self) -> List[Dict]:
        """Get comprehensive gods data"""
        return [
            # Achilles
            {
                'name': 'Achilles',
                'pantheon': 'Greek',
                'damage_type': 'Physical',
                'primary_role': 'Warrior',
                'assault_tier': 'B',
                'assault_strengths': ['Execute potential', 'Good sustain', 'Stance switching'],
                'assault_weaknesses': ['Needs CC setup', 'Vulnerable without healing'],
                'synergies': ['Athena', 'Ymir', 'Aphrodite'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Gift of the Gods',
                        'description': 'Gains extra protections or power depending on stance.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Shield of Achilles',
                        'description': 'Cone attack, bonus damage in center.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Radiant Glory',
                        'description': 'Heals and gains protections.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Combat Dodge',
                        'description': 'Dashes and strikes twice.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Fatal Strike',
                        'description': 'Executes low-health enemies.'
                    }
                ]
            },
            
            # Agni
            {
                'name': 'Agni',
                'pantheon': 'Hindu',
                'damage_type': 'Magical',
                'primary_role': 'Mage',
                'assault_tier': 'A',
                'assault_strengths': ['Great poke', 'AoE damage', 'Stun potential'],
                'assault_weaknesses': ['Needs CC setup', 'Mana hungry'],
                'synergies': ['Ares', 'Athena', 'Baron Samedi'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Combustion',
                        'description': 'Stacking basics empower next ability.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Noxious Fumes',
                        'description': 'Creates gas, stuns if ignited.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Flame Wave',
                        'description': 'Line fire attack.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Path of Flames',
                        'description': 'Dash leaving a burning trail.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Rain Fire',
                        'description': 'Calls down meteors for AoE damage.'
                    }
                ]
            },
            
            # Aladdin
            {
                'name': 'Aladdin',
                'pantheon': 'Arabian',
                'damage_type': 'Magical',
                'primary_role': 'Mage',
                'assault_tier': 'B',
                'assault_strengths': ['Burst potential', 'Mobility', 'Untargetable ult'],
                'assault_weaknesses': ['Needs setup', 'Requires protection'],
                'synergies': ['Athena', 'Geb', 'Baron Samedi'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Three Wishes',
                        'description': 'Rotating bonus effects.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Kufic Invocation',
                        'description': 'Magic burst in a small area.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': "Sultan's Grace",
                        'description': 'Defensive buff, short dash.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Agile Run',
                        'description': 'Mobility and empowered attack.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Into The Lamp',
                        'description': 'Becomes untargetable, then bursts out.'
                    }
                ]
            },
            
            # Amaterasu
            {
                'name': 'Amaterasu',
                'pantheon': 'Japanese',
                'damage_type': 'Physical',
                'primary_role': 'Warrior',
                'assault_tier': 'B',
                'assault_strengths': ['Aura utility', 'Team buffs', 'Sustain'],
                'assault_weaknesses': ['Not as tanky as top guardians', 'Needs team coordination'],
                'synergies': ['Ra', 'Aphrodite', 'Cupid'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Illuminating Strike',
                        'description': 'Hit enemies take more damage from allies.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Divine Presence',
                        'description': "Aura buffs allies' speed or power."
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Heavenly Reflection',
                        'description': 'Charges a mirror for damage and block.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Glorious Charge',
                        'description': 'Dash and silence.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Dazzling Offensive',
                        'description': 'Multi-hit dash and stun.'
                    }
                ]
            },
            
            # Anhur
            {
                'name': 'Anhur',
                'pantheon': 'Egyptian',
                'damage_type': 'Physical',
                'primary_role': 'Hunter',
                'assault_tier': 'A',
                'assault_strengths': ['Strong poke', 'Anti-tank', 'Good CC'],
                'assault_weaknesses': ['Needs CC teammates', 'Positioning dependent'],
                'synergies': ['Ymir', 'Athena', 'Cupid'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Enfeeble',
                        'description': 'Reduces enemy protections.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Shifting Sands',
                        'description': 'Creates a sand zone, buffs Anhur.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Impale',
                        'description': 'Line knockback.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Disperse',
                        'description': 'Leap and AoE knockup.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Desert Fury',
                        'description': 'Rapid-fire spear throw.'
                    }
                ]
            },
            
            # Anubis
            {
                'name': 'Anubis',
                'pantheon': 'Egyptian',
                'damage_type': 'Magical',
                'primary_role': 'Mage',
                'assault_tier': 'S',
                'assault_strengths': ['Insane damage', 'Built-in sustain', 'Strong with CC'],
                'assault_weaknesses': ['Immobile during channels', 'Needs protection'],
                'synergies': ['Athena', 'Ymir', 'Baron Samedi'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Sorrow',
                        'description': 'Bonus lifesteal and healing.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Plague of Locusts',
                        'description': 'Channel cone damage.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Mummify',
                        'description': 'Stun skillshot.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Grasping Hands',
                        'description': 'AoE slow and DoT.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Death Gaze',
                        'description': 'Channel beam for high damage.'
                    }
                ]
            },
            
            # Aphrodite
            {
                'name': 'Aphrodite',
                'pantheon': 'Greek',
                'damage_type': 'Magical',
                'primary_role': 'Mage',
                'assault_tier': 'A',
                'assault_strengths': ['Best healer', 'Team utility', 'Invulnerability ult'],
                'assault_weaknesses': ['Squishy', 'Needs positioning'],
                'synergies': ['Bellona', 'Achilles', 'Anubis'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Center of Attention',
                        'description': 'Buffs for nearby allies.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Kiss',
                        'description': 'Links to ally for buffs, stuns enemies.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Back Off!',
                        'description': 'AoE knockback and slow.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Love Birds',
                        'description': 'Line heal and DoT.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Undying Love',
                        'description': 'Short invulnerability for self and linked ally.'
                    }
                ]
            },
            
            # Ares
            {
                'name': 'Ares',
                'pantheon': 'Greek',
                'damage_type': 'Magical',
                'primary_role': 'Guardian',
                'assault_tier': 'A',
                'assault_strengths': ['Game-changing ult', 'Great in tight spaces', 'Aura items synergy'],
                'assault_weaknesses': ['Countered by beads', 'Limited mobility'],
                'synergies': ['Anubis', 'Agni', 'Cupid'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Blessed Presence',
                        'description': 'Buffs from aura items.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Shackles',
                        'description': 'Chains slow and damage.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Bolster Defenses',
                        'description': 'Buffs protections for self/allies.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Searing Flesh',
                        'description': 'Cone fire DoT.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'No Escape',
                        'description': 'Pulls all enemies in range (beads check).'
                    }
                ]
            },
            
            # Artemis
            {
                'name': 'Artemis',
                'pantheon': 'Greek',
                'damage_type': 'Physical',
                'primary_role': 'Hunter',
                'assault_tier': 'B',
                'assault_strengths': ['High damage', 'Crit potential', 'CC ult'],
                'assault_weaknesses': ['Vulnerable if focused', 'Needs peel'],
                'synergies': ['Ymir', 'Athena', 'Cupid'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Still Target',
                        'description': 'Bonus crit chance.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': "Transgressor's Fate",
                        'description': 'Trap that roots.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Vengeful Assault',
                        'description': 'Attack speed buff.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Suppress the Insolent',
                        'description': 'Line poke and slow.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Calydonian Boar',
                        'description': 'Summons a boar to stun enemies.'
                    }
                ]
            },
            
            # Athena
            {
                'name': 'Athena',
                'pantheon': 'Greek',
                'damage_type': 'Magical',
                'primary_role': 'Guardian',
                'assault_tier': 'S',
                'assault_strengths': ['Top-tier CC', 'Global presence', 'Always valuable'],
                'assault_weaknesses': ['Cooldown dependent', 'Needs follow-up'],
                'synergies': ['Anubis', 'Zeus', 'Aphrodite'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Reach',
                        'description': 'Empowered ranged basic after ability.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Preemptive Strike',
                        'description': 'Dash and taunt.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Confound',
                        'description': 'AoE taunt.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Shield Wall',
                        'description': 'Delayed AoE damage.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Defender of Olympus',
                        'description': 'Global dash to ally, shield and AoE.'
                    }
                ]
            },
            
            # Awilix
            {
                'name': 'Awilix',
                'pantheon': 'Mayan',
                'damage_type': 'Physical',
                'primary_role': 'Assassin',
                'assault_tier': 'B',
                'assault_strengths': ['Unique pull mechanic', 'Good mobility', 'Punishes positioning'],
                'assault_weaknesses': ['Needs setup for ult', 'Squishy'],
                'synergies': ['Athena', 'Thor', 'Ymir'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Initiative',
                        'description': 'Bonus crit after ability.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Summon Suku',
                        'description': 'Mount for speed/dash.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Feather Step',
                        'description': 'Leap and AoE.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Moonlight Charge',
                        'description': 'Line knockup.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Gravity Surge',
                        'description': 'Pulls airborne enemies.'
                    }
                ]
            },
            
            # Bacchus
            {
                'name': 'Bacchus',
                'pantheon': 'Roman',
                'damage_type': 'Magical',
                'primary_role': 'Guardian',
                'assault_tier': 'B',
                'assault_strengths': ['Solid CC', 'Good tanking', 'AoE potential'],
                'assault_weaknesses': ['Less oppressive than top tanks', 'Meter management'],
                'synergies': ['Anubis', 'Agni', 'Cupid'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Drunk-O-Meter',
                        'description': 'Buffs when drunk.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Chug',
                        'description': 'Drink to build meter.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Belly Flop',
                        'description': 'Leap and knockup.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Belch of the Gods',
                        'description': 'Cone DoT and stun.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Intoxicate',
                        'description': 'AoE damage and intoxication.'
                    }
                ]
            },
            
            # Baron Samedi
            {
                'name': 'Baron Samedi',
                'pantheon': 'Voodoo',
                'damage_type': 'Magical',
                'primary_role': 'Mage',
                'assault_tier': 'A',
                'assault_strengths': ['AoE control', 'Healing', 'Strong in grouped fights'],
                'assault_weaknesses': ['Needs positioning', 'Ult can be interrupted'],
                'synergies': ['Anubis', 'Agni', 'Aphrodite'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Hysteria',
                        'description': 'Debuffs enemies hit.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Vivid Gaze',
                        'description': 'Cross-shaped AoE.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Consign Spirits',
                        'description': 'AoE heal and damage.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Wrap It Up',
                        'description': 'Root and slow.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Life of the Party',
                        'description': 'Pulls and damages in a cone.'
                    }
                ]
            },
            
            # Bellona
            {
                'name': 'Bellona',
                'pantheon': 'Roman',
                'damage_type': 'Physical',
                'primary_role': 'Warrior',
                'assault_tier': 'A',
                'assault_strengths': ['Sustain', 'CC', 'Team buffs'],
                'assault_weaknesses': ['Needs healing support', 'Cooldown dependent'],
                'synergies': ['Aphrodite', 'Ra', 'Cupid'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Master of War',
                        'description': 'Bonus protections per enemy.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Shield Bash',
                        'description': 'Dash and slow.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Bludgeon',
                        'description': 'AoE sweep, then slam.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Scourge',
                        'description': 'Line attack, disarms.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': "Eagle's Rally",
                        'description': 'Leap, plant flag for buffs and knockup.'
                    }
                ]
            },
            
            # Cabrakan
            {
                'name': 'Cabrakan',
                'pantheon': 'Mayan',
                'damage_type': 'Magical',
                'primary_role': 'Guardian',
                'assault_tier': 'B',
                'assault_strengths': ['Strong zoning', 'Wall utility', 'AoE stuns'],
                'assault_weaknesses': ['Countered by mobility', 'Positioning dependent'],
                'synergies': ['Anubis', 'Agni', 'Cupid'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Shadow Zone',
                        'description': 'Damage reduction near Cabrakan.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Seismic Crush',
                        'description': 'Speed buff and stun.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Refraction Shield',
                        'description': 'Shield and AoE stun.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Tremors',
                        'description': 'Channel AoE slow/damage.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Tectonic Shift',
                        'description': 'Creates impassable walls.'
                    }
                ]
            },
            
            # Cerberus
            {
                'name': 'Cerberus',
                'pantheon': 'Greek',
                'damage_type': 'Magical',
                'primary_role': 'Guardian',
                'assault_tier': 'B',
                'assault_strengths': ['Anti-heal', 'AoE control', 'Sustain conversion'],
                'assault_weaknesses': ['Less CC than top guardians', 'Needs follow-up'],
                'synergies': ['Baron Samedi', 'Anubis', 'Aphrodite'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Spirit of Death',
                        'description': 'Converts enemy healing to self-heal.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Paralyzing Spit',
                        'description': 'Cone attack, multiple projectiles.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Ghastly Breath',
                        'description': 'Cone DoT and anti-heal.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Soul Expulsion',
                        'description': 'AoE damage and healing orbs.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Stygian Torment',
                        'description': 'Pulls enemies to self.'
                    }
                ]
            },
            
            # Cernunnos
            {
                'name': 'Cernunnos',
                'pantheon': 'Celtic',
                'damage_type': 'Physical',
                'primary_role': 'Hunter',
                'assault_tier': 'B',
                'assault_strengths': ['Versatile ADC', 'Good CC', 'Seasonal effects'],
                'assault_weaknesses': ['Needs setup', 'Positioning dependent'],
                'synergies': ['Athena', 'Ymir', 'Cupid'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Shifter of Seasons',
                        'description': 'Basic attacks change effects.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Bramble Blast',
                        'description': 'AoE root and DoT.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Horn Charge',
                        'description': 'Dash and knockback.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'The Wild Hunt',
                        'description': 'AoE polymorph.'
                    }
                ]
            },
            
            # Chaac
            {
                'name': 'Chaac',
                'pantheon': 'Mayan',
                'damage_type': 'Physical',
                'primary_role': 'Warrior',
                'assault_tier': 'B',
                'assault_strengths': ['Sustain', 'AoE silence', 'Self-heal'],
                'assault_weaknesses': ['Less damage than top warriors', 'Needs follow-up'],
                'synergies': ['Aphrodite', 'Ra', 'Athena'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Overflow',
                        'description': 'Free ability after 5 basics.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Thunder Strike',
                        'description': 'Throws axe for AoE.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Torrent',
                        'description': 'Spin attack.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Rain Dance',
                        'description': 'AoE slow and heal.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Storm Call',
                        'description': 'AoE silence and damage.'
                    }
                ]
            },
            
            # Cupid
            {
                'name': 'Cupid',
                'pantheon': 'Roman',
                'damage_type': 'Physical',
                'primary_role': 'Hunter',
                'assault_tier': 'A',
                'assault_strengths': ['Healing', 'AoE CC', 'Strong in grouped fights'],
                'assault_weaknesses': ['Squishy', 'Needs protection'],
                'synergies': ['Ares', 'Ymir', 'Aphrodite'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Lovestruck',
                        'description': 'Stacks empower abilities.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Heart Bomb',
                        'description': 'Single target DoT and stun.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Share the Love',
                        'description': 'Drops heals.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Flutter',
                        'description': 'Dash and attack speed buff.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Fields of Love',
                        'description': 'AoE mesmerize and damage.'
                    }
                ]
            },
            
            # Danzaburou
            {
                'name': 'Danzaburou',
                'pantheon': 'Japanese',
                'damage_type': 'Physical',
                'primary_role': 'Hunter',
                'assault_tier': 'B',
                'assault_strengths': ['Trickster abilities', 'Good mobility', 'Unique mechanics'],
                'assault_weaknesses': ['Needs setup', 'Positioning dependent'],
                'synergies': ['Athena', 'Ymir', 'Cupid'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Dubious Savings',
                        'description': 'Bonus gold from kills.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': "Fool's Gold",
                        'description': 'AoE damage and slow.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Alluring Spirits',
                        'description': 'Decoy bombs.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Tanuki Trickery',
                        'description': 'Stealth and movement.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Uproarious Rocket',
                        'description': 'Rides a rocket, damaging and knocking up.'
                    }
                ]
            },
            
            # Fenrir
            {
                'name': 'Fenrir',
                'pantheon': 'Norse',
                'damage_type': 'Physical',
                'primary_role': 'Assassin',
                'assault_tier': 'B',
                'assault_strengths': ['Pick potential', 'Good mobility', 'Rune system'],
                'assault_weaknesses': ['Needs setup', 'Vulnerable to CC'],
                'synergies': ['Athena', 'Ymir', 'Aphrodite'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Unbound Runes',
                        'description': 'Abilities empowered after 5 basics.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Unchained',
                        'description': 'Leap and stun.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Seething Howl',
                        'description': 'Buffs power and lifesteal.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Brutalize',
                        'description': 'Pounces and claws repeatedly.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Ragnarok',
                        'description': 'Grows huge, can grab and carry enemies.'
                    }
                ]
            },
            
            # Geb
            {
                'name': 'Geb',
                'pantheon': 'Egyptian',
                'damage_type': 'Magical',
                'primary_role': 'Guardian',
                'assault_tier': 'S',
                'assault_strengths': ['Top-tier CC', 'Shield utility', 'Always useful'],
                'assault_weaknesses': ['Cooldown dependent', 'Needs follow-up'],
                'synergies': ['Anubis', 'Zeus', 'Aphrodite'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Hard as Rock',
                        'description': 'Crit damage reduction.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Roll Out',
                        'description': 'Transforms and rolls, knocking up.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Shock Wave',
                        'description': 'AoE knockup.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Stone Shield',
                        'description': 'Shields and cleanses an ally.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Cataclysm',
                        'description': 'AoE stun.'
                    }
                ]
            },
            
            # Guan Yu
            {
                'name': 'Guan Yu',
                'pantheon': 'Chinese',
                'damage_type': 'Physical',
                'primary_role': 'Warrior',
                'assault_tier': 'B',
                'assault_strengths': ['Sustain', 'AoE healing', 'Cooldown reduction passive'],
                'assault_weaknesses': ['Less damage than top picks', 'Needs follow-up'],
                'synergies': ['Aphrodite', 'Ra', 'Athena'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Painless',
                        'description': 'Reduces cooldowns as he takes damage.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Conviction',
                        'description': 'AoE heal.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': "Warrior's Will",
                        'description': 'Dash and slow.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Taolu Assault',
                        'description': 'Channel damage and protections.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Cavalry Charge',
                        'description': 'Rides horse, knocks up and slows.'
                    }
                ]
            },
            
            # Hades
            {
                'name': 'Hades',
                'pantheon': 'Greek',
                'damage_type': 'Magical',
                'primary_role': 'Mage',
                'assault_tier': 'B',
                'assault_strengths': ['AoE control', 'Sustain', 'Blight system'],
                'assault_weaknesses': ['Needs setup', 'Ult can be escaped'],
                'synergies': ['Athena', 'Ymir', 'Aphrodite'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Blight',
                        'description': 'Debuffs enemies hit by abilities.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Death from Below',
                        'description': 'Dash and AoE.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Shroud of Darkness',
                        'description': 'Silence cone.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Devour Souls',
                        'description': 'Explodes blighted enemies for heal/damage.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Pillar of Agony',
                        'description': 'Channel AoE pull and damage.'
                    }
                ]
            },
            
            # Hecate
            {
                'name': 'Hecate',
                'pantheon': 'Greek',
                'damage_type': 'Magical',
                'primary_role': 'Mage',
                'assault_tier': 'B',
                'assault_strengths': ['Strong AoE', 'Sustain', 'Unique mechanics'],
                'assault_weaknesses': ['Less burst than top mages', 'Needs positioning'],
                'synergies': ['Athena', 'Ymir', 'Baron Samedi'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Mythic Ritual',
                        'description': 'Bonus effects after casting.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Triplicate Form',
                        'description': 'Fires three projectiles.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Spell Eater',
                        'description': 'Heals based on ability damage.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Repel Magic',
                        'description': 'AoE knockback.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Open The Gates',
                        'description': 'Large AoE, debuffs enemies.'
                    }
                ]
            },
            
            # Hercules
            {
                'name': 'Hercules',
                'pantheon': 'Roman',
                'damage_type': 'Physical',
                'primary_role': 'Warrior',
                'assault_tier': 'B',
                'assault_strengths': ['Displacement', 'Sustain', 'Boulder combo'],
                'assault_weaknesses': ['Needs setup', 'Positioning dependent'],
                'synergies': ['Aphrodite', 'Ra', 'Athena'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Strength',
                        'description': 'Bonus power as he takes damage.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Driving Strike',
                        'description': 'Dash and knockback.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Earthbreaker',
                        'description': 'Pulls enemies.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Mitigate Wounds',
                        'description': 'Heal over time.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Excavate',
                        'description': 'Throws boulder for AoE damage.'
                    }
                ]
            },
            
            # Hua Mulan
            {
                'name': 'Hua Mulan',
                'pantheon': 'Chinese',
                'damage_type': 'Physical',
                'primary_role': 'Warrior',
                'assault_tier': 'B',
                'assault_strengths': ['Versatile', 'Evolving abilities', 'Multi-weapon'],
                'assault_weaknesses': ['Needs time to evolve', 'Complex mechanics'],
                'synergies': ['Aphrodite', 'Ra', 'Athena'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Discipline',
                        'description': 'Abilities evolve with use.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Cross Strike',
                        'description': 'Double slash.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Spear Thrust',
                        'description': 'Dash and poke.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Grapple',
                        'description': 'Pulls and roots.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Divine Mastery',
                        'description': 'Multi-weapon combo.'
                    }
                ]
            },
            
            # Hun Batz
            {
                'name': 'Hun Batz',
                'pantheon': 'Mayan',
                'damage_type': 'Physical',
                'primary_role': 'Assassin',
                'assault_tier': 'B',
                'assault_strengths': ['AoE fear', 'Good mobility', 'Team fight potential'],
                'assault_weaknesses': ['Needs setup', 'Squishy'],
                'synergies': ['Athena', 'Ymir', 'Baron Samedi'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Infused Strikes',
                        'description': 'Bonus crit chance after abilities.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Somersault',
                        'description': 'Leap and slow.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Overhand Smash',
                        'description': 'AoE damage.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Sacred Monkey',
                        'description': 'Bounces between enemies.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Fear No Evil',
                        'description': 'AoE fear.'
                    }
                ]
            },
            
            # Izanami
            {
                'name': 'Izanami',
                'pantheon': 'Japanese',
                'damage_type': 'Physical',
                'primary_role': 'Hunter',
                'assault_tier': 'B',
                'assault_strengths': ['Great poke', 'Stealth', 'AoE silence'],
                'assault_weaknesses': ['Squishy', 'Needs peel'],
                'synergies': ['Athena', 'Ymir', 'Cupid'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Death Draws Nigh',
                        'description': 'Bonus power as allies die.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Sickle Storm',
                        'description': 'Empowered basics.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Spectral Projection',
                        'description': 'Line poke and slow.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Fade Away',
                        'description': 'Stealth and speed.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Dark Portal',
                        'description': 'AoE silence and damage.'
                    }
                ]
            },
            
            # Jing Wei
            {
                'name': 'Jing Wei',
                'pantheon': 'Chinese',
                'damage_type': 'Physical',
                'primary_role': 'Hunter',
                'assault_tier': 'B',
                'assault_strengths': ['High mobility', 'Fast respawn', 'Good escape'],
                'assault_weaknesses': ['Less damage than top ADCs', 'Positioning dependent'],
                'synergies': ['Athena', 'Ymir', 'Cupid'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Rapid Reincarnation',
                        'description': 'Fast respawn.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Persistent Gust',
                        'description': 'AoE knockup and speed.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Explosive Bolts',
                        'description': 'Empowered basics.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Agility',
                        'description': 'Dash.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Air Strike',
                        'description': 'Flying line ult.'
                    }
                ]
            },
            
            # Kali
            {
                'name': 'Kali',
                'pantheon': 'Hindu',
                'damage_type': 'Physical',
                'primary_role': 'Assassin',
                'assault_tier': 'B',
                'assault_strengths': ['Strong duelist', 'Invulnerability ult', 'Target system'],
                'assault_weaknesses': ['Needs setup', 'Squishy'],
                'synergies': ['Athena', 'Ymir', 'Aphrodite'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Marked for Death',
                        'description': 'Bonus gold and healing from target.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Nimble Strike',
                        'description': 'Leap and heal.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Lash',
                        'description': 'DoT and healing.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Incense',
                        'description': 'AoE stun and power buff.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Destruction',
                        'description': 'Temporary invulnerability and lifesteal.'
                    }
                ]
            },
            
            # Khepri
            {
                'name': 'Khepri',
                'pantheon': 'Egyptian',
                'damage_type': 'Magical',
                'primary_role': 'Guardian',
                'assault_tier': 'B',
                'assault_strengths': ['Powerful revive', 'Good utility', 'Team protection'],
                'assault_weaknesses': ['Less CC than top guardians', 'Ult cooldown dependent'],
                'synergies': ['Anubis', 'Zeus', 'Aphrodite'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Fortitude',
                        'description': 'Shields allies on death.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Abduct',
                        'description': 'Dash and grab.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Rising Dawn',
                        'description': 'AoE cleanse and protection.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Solar Flare',
                        'description': 'AoE root.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': "Scarab's Blessing",
                        'description': 'Revives an ally.'
                    }
                ]
            },
            
            # Kukulkan
            {
                'name': 'Kukulkan',
                'pantheon': 'Mayan',
                'damage_type': 'Magical',
                'primary_role': 'Mage',
                'assault_tier': 'A',
                'assault_strengths': ['Massive poke', 'AoE damage', 'Mana scaling'],
                'assault_weaknesses': ['No escape', 'Positioning dependent'],
                'synergies': ['Athena', 'Ymir', 'Baron Samedi'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Power of the Wind Jewel',
                        'description': 'Bonus power for mana.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Zephyr',
                        'description': 'Burst poke.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Slipstream',
                        'description': 'Speed buff.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Whirlwind',
                        'description': 'AoE DoT.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Spirit of the Nine Winds',
                        'description': 'Long-range AoE nuke.'
                    }
                ]
            },
            
            # Loki
            {
                'name': 'Loki',
                'pantheon': 'Norse',
                'damage_type': 'Physical',
                'primary_role': 'Assassin',
                'assault_tier': 'B',
                'assault_strengths': ['Strong pick potential', 'Stealth', 'Burst damage'],
                'assault_weaknesses': ['Squishy', 'Needs setup'],
                'synergies': ['Athena', 'Ymir', 'Aphrodite'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Behind You',
                        'description': 'Bonus damage from behind.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Vanish',
                        'description': 'Stealth and DoT.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Agonizing Visions',
                        'description': 'AoE slow.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Flurry Strike',
                        'description': 'Burst combo.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Assassinate',
                        'description': 'Teleport and stun.'
                    }
                ]
            },
            
            # Medusa
            {
                'name': 'Medusa',
                'pantheon': 'Greek',
                'damage_type': 'Physical',
                'primary_role': 'Hunter',
                'assault_tier': 'A',
                'assault_strengths': ['High damage', 'Anti-heal', 'AoE stun'],
                'assault_weaknesses': ['Positioning dependent', 'Needs peel'],
                'synergies': ['Athena', 'Ymir', 'Cupid'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Sidewinder',
                        'description': 'No movement penalty when side strafing.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Viper Shot',
                        'description': 'Empowered basics.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Acid Spray',
                        'description': 'Line poke and splash.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Lacerate',
                        'description': 'Dash and anti-heal.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Petrify',
                        'description': 'AoE stun and damage.'
                    }
                ]
            },
            
            # Merlin
            {
                'name': 'Merlin',
                'pantheon': 'Arthurian',
                'damage_type': 'Magical',
                'primary_role': 'Mage',
                'assault_tier': 'S',
                'assault_strengths': ['Insane AoE', 'Flexibility', 'Multiple stances'],
                'assault_weaknesses': ['Complex', 'Mana hungry'],
                'synergies': ['Athena', 'Ymir', 'Baron Samedi'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Overload',
                        'description': 'Bonus power after stance switch.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Elemental Mastery',
                        'description': 'Switch between fire, ice, and arcane.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Blizzard',
                        'description': 'AoE slow.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Vortex',
                        'description': 'AoE pull.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Dragonfire',
                        'description': 'AoE DoT.'
                    }
                ]
            },
            
            # Mordred
            {
                'name': 'Mordred',
                'pantheon': 'Arthurian',
                'damage_type': 'Physical',
                'primary_role': 'Warrior',
                'assault_tier': 'B',
                'assault_strengths': ['Sustain', 'Burst potential', 'Kill scaling'],
                'assault_weaknesses': ['Needs setup', 'Positioning dependent'],
                'synergies': ['Aphrodite', 'Ra', 'Athena'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Wrath of the Forsaken',
                        'description': 'Bonus power after kills.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Heart Slash',
                        'description': 'Line poke and heal.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Severing Slice',
                        'description': 'AoE slow.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Bloodrage',
                        'description': 'Self-buff and lifesteal.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Cruel Strikes',
                        'description': 'Multi-hit combo.'
                    }
                ]
            },
            
            # Neith
            {
                'name': 'Neith',
                'pantheon': 'Egyptian',
                'damage_type': 'Physical',
                'primary_role': 'Hunter',
                'assault_tier': 'A',
                'assault_strengths': ['Global pressure', 'Strong poke', 'Weave system'],
                'assault_weaknesses': ['Positioning dependent', 'Needs follow-up'],
                'synergies': ['Athena', 'Ymir', 'Cupid'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Broken Weave',
                        'description': 'Roots spawn weaves for bonus effects.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Spirit Arrow',
                        'description': 'Line root.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Unravel',
                        'description': 'AoE heal and damage.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Back Flip',
                        'description': 'Leap and slow.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'World Weaver',
                        'description': 'Global snipe and root.'
                    }
                ]
            },
            
            # Nemesis
            {
                'name': 'Nemesis',
                'pantheon': 'Greek',
                'damage_type': 'Physical',
                'primary_role': 'Assassin',
                'assault_tier': 'B',
                'assault_strengths': ['Anti-tank', 'Shield reflect', 'Stat steal'],
                'assault_weaknesses': ['Needs setup', 'Squishy'],
                'synergies': ['Athena', 'Ymir', 'Aphrodite'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Scales of Fate',
                        'description': 'Bonus power after ability use.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Swift Vengeance',
                        'description': 'Dash and slash.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Slice and Dice',
                        'description': 'AoE damage.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Retribution',
                        'description': 'Shield and reflect.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Divine Judgement',
                        'description': 'Steals enemy power and protections.'
                    }
                ]
            },
            
            # Nu Wa
            {
                'name': 'Nu Wa',
                'pantheon': 'Chinese',
                'damage_type': 'Magical',
                'primary_role': 'Mage',
                'assault_tier': 'B',
                'assault_strengths': ['Global damage', 'Minion utility', 'Stealth'],
                'assault_weaknesses': ['Less burst than top mages', 'Minion dependent'],
                'synergies': ['Athena', 'Ymir', 'Baron Samedi'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Elemental Crystal',
                        'description': 'Bonus power after ability use.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Mysterious Fog',
                        'description': 'Stealth and DoT.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Clay Soldiers',
                        'description': 'Summon minions.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Shining Metal',
                        'description': 'AoE stun.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Fire Shards',
                        'description': 'Global AoE damage.'
                    }
                ]
            },
            
            # Odin
            {
                'name': 'Odin',
                'pantheon': 'Norse',
                'damage_type': 'Physical',
                'primary_role': 'Warrior',
                'assault_tier': 'A',
                'assault_strengths': ['Anti-heal', 'Zoning', 'Strong in grouped fights'],
                'assault_weaknesses': ['Ult can trap allies', 'Cooldown dependent'],
                'synergies': ['Anubis', 'Zeus', 'Aphrodite'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Path to Valhalla',
                        'description': 'Bonus power after ability use.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Lunge',
                        'description': 'Leap and AoE.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Raven Shout',
                        'description': 'Shield and explosion.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': "Gungnir's Might",
                        'description': 'Line poke and slow.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Ring of Spears',
                        'description': 'Creates a ring, blocks escape and healing.'
                    }
                ]
            },
            
            # Pele
            {
                'name': 'Pele',
                'pantheon': 'Polynesian',
                'damage_type': 'Physical',
                'primary_role': 'Assassin',
                'assault_tier': 'B',
                'assault_strengths': ['Burst potential', 'Mobility', 'DoT damage'],
                'assault_weaknesses': ['Squishy', 'Needs setup'],
                'synergies': ['Athena', 'Ymir', 'Aphrodite'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Everlasting Flame',
                        'description': 'Bonus power after ability use.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Pyroclast',
                        'description': 'Line poke.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Eruption',
                        'description': 'AoE damage and slow.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Magma Rush',
                        'description': 'Dash and DoT.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Volcanic Lightning',
                        'description': 'Multi-hit dash.'
                    }
                ]
            },
            
            # Poseidon
            {
                'name': 'Poseidon',
                'pantheon': 'Greek',
                'damage_type': 'Magical',
                'primary_role': 'Mage',
                'assault_tier': 'A',
                'assault_strengths': ['Huge AoE', 'Zoning', 'Tide meter system'],
                'assault_weaknesses': ['Positioning dependent', 'Ult telegraphed'],
                'synergies': ['Athena', 'Ymir', 'Baron Samedi'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Changing Tides',
                        'description': 'Movement speed and damage scale with tide meter.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Tidal Surge',
                        'description': 'Line push.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Trident',
                        'description': 'Speed and split basics.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Whirlpool',
                        'description': 'AoE pull.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Release the Kraken!',
                        'description': 'AoE nuke and stun.'
                    }
                ]
            },
            
            # Ra
            {
                'name': 'Ra',
                'pantheon': 'Egyptian',
                'damage_type': 'Magical',
                'primary_role': 'Mage',
                'assault_tier': 'A',
                'assault_strengths': ['Sustain', 'Poke', 'Always useful'],
                'assault_weaknesses': ['Skillshot dependent', 'Positioning important'],
                'synergies': ['Aphrodite', 'Bellona', 'Athena'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Speed of Light',
                        'description': 'Bonus speed after ability use.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Celestial Beam',
                        'description': 'Line poke and heal.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Divine Light',
                        'description': 'AoE slow and blind.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Solar Blessing',
                        'description': 'AoE heal and damage.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Searing Pain',
                        'description': 'Long-range snipe.'
                    }
                ]
            },
            
            # Rama
            {
                'name': 'Rama',
                'pantheon': 'Hindu',
                'damage_type': 'Physical',
                'primary_role': 'Hunter',
                'assault_tier': 'B',
                'assault_strengths': ['Global pressure', 'Astral arrows', 'Good mobility'],
                'assault_weaknesses': ['Less burst than top ADCs', 'Arrow management'],
                'synergies': ['Athena', 'Ymir', 'Cupid'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Astral Quiver',
                        'description': 'Bonus effects from astral arrows.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Astral Strike',
                        'description': 'Empowered basics.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Pick Me Up',
                        'description': 'Attack speed buff.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Rolling Assault',
                        'description': 'Dash and slow.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Astral Barrage',
                        'description': 'Global snipe.'
                    }
                ]
            },
            
            # Sobek
            {
                'name': 'Sobek',
                'pantheon': 'Egyptian',
                'damage_type': 'Magical',
                'primary_role': 'Guardian',
                'assault_tier': 'A',
                'assault_strengths': ['Displacement', 'Anti-heal', 'Strong in grouped fights'],
                'assault_weaknesses': ['Positioning dependent', 'Needs follow-up'],
                'synergies': ['Anubis', 'Zeus', 'Aphrodite'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Blessing of the Nile',
                        'description': 'Bonus protections after abilities.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Charge Prey',
                        'description': 'Dash and throw.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Tail Whip',
                        'description': 'AoE knockback.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Sickening Strike',
                        'description': 'Line poke and anti-heal.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Lurking in the Waters',
                        'description': 'Submerge, then burst AoE.'
                    }
                ]
            },
            
            # Sol
            {
                'name': 'Sol',
                'pantheon': 'Norse',
                'damage_type': 'Magical',
                'primary_role': 'Mage',
                'assault_tier': 'B',
                'assault_strengths': ['High mobility', 'Poke', 'Stealth'],
                'assault_weaknesses': ['Less burst than top mages', 'Positioning dependent'],
                'synergies': ['Athena', 'Ymir', 'Baron Samedi'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Unstable Manifestation',
                        'description': 'Bonus power after ability use.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Radiance',
                        'description': 'AoE heal and damage.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Stellar Burst',
                        'description': 'Line poke and slow.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Disapparate',
                        'description': 'Stealth and speed.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Supernova',
                        'description': 'Multi-hit AoE.'
                    }
                ]
            },
            
            # Susano
            {
                'name': 'Susano',
                'pantheon': 'Japanese',
                'damage_type': 'Physical',
                'primary_role': 'Assassin',
                'assault_tier': 'A',
                'assault_strengths': ['Mobility', 'AoE damage', 'Strong in grouped fights'],
                'assault_weaknesses': ['Squishy', 'Needs positioning'],
                'synergies': ['Athena', 'Ymir', 'Baron Samedi'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': "Storm's Edge",
                        'description': 'Bonus effects after ability use.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Storm Kata',
                        'description': 'Multi-hit combo.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Wind Siphon',
                        'description': 'Pulls enemies.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Jet Stream',
                        'description': 'Teleport and dash.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Typhoon',
                        'description': 'Channel AoE pull and damage.'
                    }
                ]
            },
            
            # Thanatos
            {
                'name': 'Thanatos',
                'pantheon': 'Greek',
                'damage_type': 'Physical',
                'primary_role': 'Assassin',
                'assault_tier': 'B',
                'assault_strengths': ['Execute threat', 'Early game power', 'Sustain on kills'],
                'assault_weaknesses': ['Squishy', 'Falls off late'],
                'synergies': ['Athena', 'Ymir', 'Aphrodite'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Harvester of Souls',
                        'description': 'Heals on kill.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Death Scythe',
                        'description': 'Line poke and heal.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Scent of Death',
                        'description': 'Speed and execute buff.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Soul Reap',
                        'description': 'Cone silence.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Hovering Death',
                        'description': 'Execute ult.'
                    }
                ]
            },
            
            # The Morrigan
            {
                'name': 'The Morrigan',
                'pantheon': 'Celtic',
                'damage_type': 'Magical',
                'primary_role': 'Mage',
                'assault_tier': 'B',
                'assault_strengths': ['Flexible', 'Transform utility', 'Stealth'],
                'assault_weaknesses': ['Needs setup', 'Complex mechanics'],
                'synergies': ['Athena', 'Ymir', 'Baron Samedi'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Doomsayer',
                        'description': 'Bonus damage after abilities.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Deadly Aspects',
                        'description': 'Double hit.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Dark Omen',
                        'description': 'AoE mark and damage.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Confusion',
                        'description': 'Stealth and decoy.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Changeling',
                        'description': 'Transforms into any enemy god.'
                    }
                ]
            },
            
            # Thor
            {
                'name': 'Thor',
                'pantheon': 'Norse',
                'damage_type': 'Physical',
                'primary_role': 'Assassin',
                'assault_tier': 'A',
                'assault_strengths': ['Global pressure', 'AoE damage', 'Strong in grouped fights'],
                'assault_weaknesses': ['Positioning dependent', 'Ult telegraphed'],
                'synergies': ['Athena', 'Ymir', 'Baron Samedi'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': "Warrior's Madness",
                        'description': 'Bonus power after ability use.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': "Mjolnir's Attunement",
                        'description': 'Line poke and return.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Tectonic Rift',
                        'description': 'Line stun.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Berserker Barrage',
                        'description': 'AoE spin.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Anvil of Dawn',
                        'description': 'Global leap and AoE stun.'
                    }
                ]
            },
            
            # Ullr
            {
                'name': 'Ullr',
                'pantheon': 'Norse',
                'damage_type': 'Physical',
                'primary_role': 'Hunter',
                'assault_tier': 'A',
                'assault_strengths': ['Versatile ADC', 'Strong poke', 'Stance switching'],
                'assault_weaknesses': ['Complex mechanics', 'Positioning dependent'],
                'synergies': ['Athena', 'Ymir', 'Cupid'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Weapon Master',
                        'description': 'Switch between bow and axe.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Bladed Arrow/Thrown Axe',
                        'description': 'Line poke or stun.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Expose Weakness/Invigorate',
                        'description': 'Self-buff.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Hail of Arrows/Glory Bound',
                        'description': 'AoE poke or leap.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Wield Axes/Bow',
                        'description': 'Stance switch.'
                    }
                ]
            },
            
            # Vulcan
            {
                'name': 'Vulcan',
                'pantheon': 'Roman',
                'damage_type': 'Magical',
                'primary_role': 'Mage',
                'assault_tier': 'B',
                'assault_strengths': ['Strong poke', 'Turret utility', 'Long range'],
                'assault_weaknesses': ['Less burst than top mages', 'Positioning dependent'],
                'synergies': ['Athena', 'Ymir', 'Baron Samedi'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Master Craftsman',
                        'description': 'Bonus power after ability use.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Backfire',
                        'description': 'Line poke.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Inferno Cannon',
                        'description': 'Deploys turret.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Magma Bomb',
                        'description': 'AoE knockback.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Earthshaker',
                        'description': 'Long-range AoE nuke.'
                    }
                ]
            },
            
            # Yemoja
            {
                'name': 'Yemoja',
                'pantheon': 'Yoruba',
                'damage_type': 'Magical',
                'primary_role': 'Guardian',
                'assault_tier': 'S',
                'assault_strengths': ['Top-tier healing', 'Zoning', 'Always valuable'],
                'assault_weaknesses': ['Omi management', 'Positioning dependent'],
                'synergies': ['Anubis', 'Zeus', 'Aphrodite'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Omi',
                        'description': 'Uses Omi instead of mana for abilities.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Bouncing Bubble',
                        'description': 'AoE slow and heal.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Mending Waters',
                        'description': 'Heals and shields.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Riptide',
                        'description': 'Creates portals for movement.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': "River's Rebuke",
                        'description': 'Creates impassable walls.'
                    }
                ]
            },
            
            # Ymir
            {
                'name': 'Ymir',
                'pantheon': 'Norse',
                'damage_type': 'Magical',
                'primary_role': 'Guardian',
                'assault_tier': 'S',
                'assault_strengths': ['Best CC', 'Zoning', 'Wall utility'],
                'assault_weaknesses': ['Positioning dependent', 'Slow'],
                'synergies': ['Anubis', 'Zeus', 'Cupid'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Frostbite',
                        'description': 'Bonus damage after abilities.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Ice Wall',
                        'description': 'Creates wall.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Glacial Strike',
                        'description': 'AoE slow and damage.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Frost Breath',
                        'description': 'Cone stun.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Shards of Ice',
                        'description': 'Channel AoE nuke.'
                    }
                ]
            },
            
            # Zeus
            {
                'name': 'Zeus',
                'pantheon': 'Greek',
                'damage_type': 'Magical',
                'primary_role': 'Mage',
                'assault_tier': 'S',
                'assault_strengths': ['Top-tier AoE', 'Burst damage', 'Oppressive in Assault'],
                'assault_weaknesses': ['No escape', 'Positioning dependent'],
                'synergies': ['Athena', 'Ymir', 'Baron Samedi'],
                'abilities': [
                    {
                        'ability_type': 'passive',
                        'name': 'Overcharge',
                        'description': 'Abilities stack charges for detonation.'
                    },
                    {
                        'ability_type': 'ability_1',
                        'name': 'Chain Lightning',
                        'description': 'Bounces between enemies.'
                    },
                    {
                        'ability_type': 'ability_2',
                        'name': 'Aegis Assault',
                        'description': 'Shield deploy, applies charges.'
                    },
                    {
                        'ability_type': 'ability_3',
                        'name': 'Detonate Charge',
                        'description': 'Explodes charges for burst.'
                    },
                    {
                        'ability_type': 'ability_4',
                        'name': 'Lightning Storm',
                        'description': 'Large AoE nuke.'
                    }
                ]
            }
        ]

    def get_items_data(self) -> List[Dict]:
        """Get comprehensive items data"""
        return [
            # Starter Items
            {
                'name': "Death's Toll",
                'tier': 1,
                'cost': 700,
                'category': 'starter',
                'strength': 15,
                'health': 100,
                'notes': 'Basic attacks restore health/mana',
                'recommended_for': ['Hunter', 'Warrior']
            },
            {
                'name': "Warrior's Axe",
                'tier': 1,
                'cost': 700,
                'category': 'starter',
                'strength': 20,
                'health': 75,
                'notes': 'Bonus damage and healing on hit',
                'recommended_for': ['Warrior', 'Assassin']
            },
            {
                'name': 'Vampiric Shroud',
                'tier': 1,
                'cost': 700,
                'category': 'starter',
                'intelligence': 25,
                'health': 75,
                'notes': 'Ability hits restore health/mana',
                'recommended_for': ['Mage', 'Guardian']
            },
            {
                'name': "Bumba's Dagger",
                'tier': 1,
                'cost': 700,
                'category': 'starter',
                'strength': 15,
                'notes': 'Bonus damage to minions/jungle, healing on kill',
                'recommended_for': ['Assassin', 'Warrior']
            },
            {
                'name': 'Bluestone Pendant',
                'tier': 1,
                'cost': 700,
                'category': 'starter',
                'strength': 20,
                'mana': 100,
                'notes': 'Abilities deal bonus DoT, restores mana',
                'recommended_for': ['Warrior', 'Assassin']
            },
            {
                'name': 'Conduit Gem',
                'tier': 1,
                'cost': 700,
                'category': 'starter',
                'intelligence': 30,
                'notes': 'Abilities stack, bonus burst after 3 abilities',
                'recommended_for': ['Mage']
            },
            {
                'name': "Sentinel's Gift",
                'tier': 1,
                'cost': 700,
                'category': 'starter',
                'health': 125,
                'notes': 'Bonus gold and health/mana on assists',
                'recommended_for': ['Guardian']
            },
            {
                'name': 'Tainted Steel',
                'tier': 1,
                'cost': 700,
                'category': 'starter',
                'strength': 15,
                'health': 100,
                'notes': 'Reduces enemy healing when hit',
                'recommended_for': ['Warrior', 'Assassin']
            },
            {
                'name': 'Manikin Scepter',
                'tier': 1,
                'cost': 700,
                'category': 'starter',
                'strength': 20,
                'notes': 'Bonus damage to minions, DoT on hit',
                'recommended_for': ['Hunter', 'Assassin']
            },
            
            # Physical Power Items
            {
                'name': "Hydra's Lament",
                'tier': 3,
                'cost': 2400,
                'category': 'physical_power',
                'strength': 60,
                'cooldown_reduction': 20,
                'passive_name': 'Hydra',
                'passive_description': 'Next basic after ability deals bonus damage',
                'recommended_for': ['Assassin', 'Warrior']
            },
            {
                'name': "Jotunn's Wrath",
                'tier': 3,
                'cost': 2300,
                'category': 'physical_power',
                'strength': 55,
                'cooldown_reduction': 20,
                'penetration_flat': 10,
                'recommended_for': ['Assassin', 'Warrior']
            },
            {
                'name': 'The Crusher',
                'tier': 3,
                'cost': 2300,
                'category': 'physical_power',
                'strength': 45,
                'attack_speed': 15,
                'passive_name': 'Crush',
                'passive_description': 'Ability hit DoT',
                'recommended_for': ['Hunter', 'Assassin']
            },
            {
                'name': 'Heartseeker',
                'tier': 3,
                'cost': 2800,
                'category': 'physical_power',
                'strength': 65,
                'penetration_flat': 15,
                'passive_name': 'Heartseeker',
                'passive_description': 'Bonus ability damage (scales enemy HP)',
                'recommended_for': ['Assassin', 'Hunter']
            },
            {
                'name': 'Transcendence',
                'tier': 3,
                'cost': 2600,
                'category': 'physical_power',
                'strength': 35,
                'mana': 300,
                'passive_name': 'Transcendence',
                'passive_description': 'Stacking power from mana',
                'recommended_for': ['Hunter', 'Warrior']
            },
            {
                'name': 'Bloodforge',
                'tier': 3,
                'cost': 2700,
                'category': 'physical_power',
                'strength': 75,
                'physical_lifesteal': 15,
                'passive_name': 'Bloodforge',
                'passive_description': 'Shield on kill',
                'recommended_for': ['Hunter', 'Assassin']
            },
            {
                'name': "Devourer's Gauntlet",
                'tier': 3,
                'cost': 2500,
                'category': 'physical_power',
                'strength': 30,
                'physical_lifesteal': 10,
                'passive_name': 'Devourer',
                'passive_description': 'Stacking lifesteal and power',
                'recommended_for': ['Hunter']
            },
            {
                'name': "Qin's Sais",
                'tier': 3,
                'cost': 2600,
                'category': 'physical_power',
                'strength': 40,
                'attack_speed': 25,
                'passive_name': "Qin's Sais",
                'passive_description': 'Bonus %HP damage on hit',
                'recommended_for': ['Hunter', 'Assassin']
            },
            {
                'name': "Odysseus' Bow",
                'tier': 3,
                'cost': 2400,
                'category': 'physical_power',
                'attack_speed': 40,
                'passive_name': 'Chain Lightning',
                'passive_description': 'Chain lightning on hit',
                'recommended_for': ['Hunter']
            },
            {
                'name': 'The Executioner',
                'tier': 3,
                'cost': 2300,
                'category': 'physical_power',
                'strength': 30,
                'attack_speed': 25,
                'passive_name': 'Executioner',
                'passive_description': 'Reduces enemy protections on hit',
                'recommended_for': ['Hunter']
            },
            {
                'name': "Atalanta's Bow",
                'tier': 3,
                'cost': 2500,
                'category': 'physical_power',
                'strength': 40,
                'attack_speed': 20,
                'passive_name': 'Atalanta',
                'passive_description': 'Movement speed on hit',
                'recommended_for': ['Hunter']
            },
            {
                'name': 'Silverbranch Bow',
                'tier': 3,
                'cost': 2400,
                'category': 'physical_power',
                'strength': 30,
                'attack_speed': 30,
                'passive_name': 'Silverbranch',
                'passive_description': 'Converts overcapped AS to power',
                'recommended_for': ['Hunter']
            },
            {
                'name': "Shifter's Shield",
                'tier': 3,
                'cost': 2400,
                'category': 'hybrid',
                'strength': 40,
                'physical_protection': 20,
                'magical_protection': 20,
                'passive_name': 'Shifter',
                'passive_description': 'Stats shift based on health',
                'recommended_for': ['Warrior', 'Assassin']
            },
            {
                'name': "Gladiator's Shield",
                'tier': 3,
                'cost': 2300,
                'category': 'hybrid',
                'strength': 30,
                'cooldown_reduction': 10,
                'physical_protection': 30,
                'passive_name': 'Gladiator',
                'passive_description': 'Bonus ability damage and sustain',
                'recommended_for': ['Warrior']
            },
            {
                'name': 'Runeforged Hammer',
                'tier': 3,
                'cost': 2400,
                'category': 'physical_power',
                'strength': 40,
                'health': 200,
                'passive_name': 'Runeforged',
                'passive_description': 'Bonus damage to CC\'d enemies',
                'recommended_for': ['Warrior', 'Assassin']
            },
            
            # Magical Power Items
            {
                'name': 'Book of Thoth',
                'tier': 3,
                'cost': 2800,
                'category': 'magical_power',
                'intelligence': 70,
                'mana': 125,
                'passive_name': 'Thoth',
                'passive_description': 'Stacking power from mana',
                'recommended_for': ['Mage']
            },
            {
                'name': "Chronos' Pendant",
                'tier': 3,
                'cost': 2600,
                'category': 'magical_power',
                'intelligence': 80,
                'cooldown_reduction': 20,
                'mana': 100,
                'recommended_for': ['Mage', 'Guardian']
            },
            {
                'name': 'Spear of Desolation',
                'tier': 3,
                'cost': 2700,
                'category': 'magical_power',
                'intelligence': 95,
                'penetration_flat': 15,
                'cooldown_reduction': 10,
                'recommended_for': ['Mage']
            },
            {
                'name': 'Rod of Tahuti',
                'tier': 3,
                'cost': 3000,
                'category': 'magical_power',
                'intelligence': 120,
                'passive_name': 'Tahuti',
                'passive_description': 'Bonus damage to low-HP enemies',
                'recommended_for': ['Mage']
            },
            {
                'name': 'Spear of the Magus',
                'tier': 3,
                'cost': 2500,
                'category': 'magical_power',
                'intelligence': 70,
                'penetration_flat': 10,
                'passive_name': 'Magus',
                'passive_description': 'Applies debuff for increased magic damage',
                'recommended_for': ['Mage']
            },
            {
                'name': 'Soul Reaver',
                'tier': 3,
                'cost': 2700,
                'category': 'magical_power',
                'intelligence': 80,
                'mana': 150,
                'passive_name': 'Soul Reaver',
                'passive_description': 'Bonus %HP damage on ability hit',
                'recommended_for': ['Mage']
            },
            {
                'name': 'Gem of Isolation',
                'tier': 3,
                'cost': 2500,
                'category': 'magical_power',
                'intelligence': 70,
                'health': 200,
                'passive_name': 'Isolation',
                'passive_description': 'Slows enemies hit by abilities',
                'recommended_for': ['Mage', 'Guardian']
            },
            {
                'name': "Bancroft's Talon",
                'tier': 3,
                'cost': 2500,
                'category': 'magical_power',
                'intelligence': 65,
                'magical_lifesteal': 12,
                'passive_name': 'Bancroft',
                'passive_description': 'More power at low health',
                'recommended_for': ['Mage']
            },
            {
                'name': "Typhon's Fang",
                'tier': 3,
                'cost': 2500,
                'category': 'magical_power',
                'intelligence': 70,
                'magical_lifesteal': 15,
                'passive_name': 'Typhon',
                'passive_description': 'Increases healing from lifesteal',
                'recommended_for': ['Mage']
            },
            {
                'name': 'Divine Ruin',
                'tier': 3,
                'cost': 2300,
                'category': 'magical_power',
                'intelligence': 75,
                'penetration_flat': 12,
                'passive_name': 'Divine Ruin',
                'passive_description': 'Applies anti-heal on ability hit',
                'recommended_for': ['Mage']
            },
            {
                'name': 'Ethereal Staff',
                'tier': 3,
                'cost': 2600,
                'category': 'magical_power',
                'intelligence': 60,
                'health': 300,
                'passive_name': 'Ethereal',
                'passive_description': 'Steals %HP on ability hit',
                'recommended_for': ['Mage', 'Guardian']
            },
            {
                'name': "Warlock's Staff",
                'tier': 3,
                'cost': 2500,
                'category': 'magical_power',
                'intelligence': 55,
                'health': 125,
                'passive_name': 'Warlock',
                'passive_description': 'Stacking health/power',
                'recommended_for': ['Mage', 'Guardian']
            },
            {
                'name': 'Polynomicon',
                'tier': 3,
                'cost': 2400,
                'category': 'magical_power',
                'intelligence': 75,
                'magical_lifesteal': 12,
                'passive_name': 'Polynomicon',
                'passive_description': 'Empowered basic after ability',
                'recommended_for': ['Mage']
            },
            
            # Defensive Items
            {
                'name': 'Breastplate of Valor',
                'tier': 3,
                'cost': 2300,
                'category': 'defense',
                'physical_protection': 65,
                'cooldown_reduction': 20,
                'mana': 300,
                'recommended_for': ['Guardian', 'Warrior']
            },
            {
                'name': 'Sovereignty',
                'tier': 3,
                'cost': 2200,
                'category': 'defense',
                'physical_protection': 60,
                'passive_name': 'Sovereignty',
                'passive_description': 'Aura protections for allies',
                'recommended_for': ['Guardian']
            },
            {
                'name': 'Pestilence',
                'tier': 3,
                'cost': 2200,
                'category': 'defense',
                'magical_protection': 60,
                'health': 200,
                'passive_name': 'Pestilence',
                'passive_description': 'Anti-heal aura',
                'recommended_for': ['Guardian', 'Warrior']
            },
            {
                'name': 'Bulwark of Hope',
                'tier': 3,
                'cost': 2400,
                'category': 'defense',
                'magical_protection': 60,
                'health': 200,
                'passive_name': 'Bulwark',
                'passive_description': 'Shield at low health',
                'recommended_for': ['Guardian', 'Warrior']
            },
            {
                'name': "Genji's Guard",
                'tier': 3,
                'cost': 2300,
                'category': 'defense',
                'magical_protection': 65,
                'cooldown_reduction': 20,
                'mana': 300,
                'recommended_for': ['Guardian', 'Warrior']
            },
            {
                'name': 'Spectral Armor',
                'tier': 3,
                'cost': 2200,
                'category': 'defense',
                'physical_protection': 60,
                'health': 200,
                'passive_name': 'Spectral',
                'passive_description': 'Reduces crit damage taken',
                'recommended_for': ['Guardian', 'Warrior']
            },
            {
                'name': 'Midgardian Mail',
                'tier': 3,
                'cost': 2300,
                'category': 'defense',
                'physical_protection': 55,
                'health': 300,
                'passive_name': 'Midgardian',
                'passive_description': 'Slows attackers',
                'recommended_for': ['Guardian', 'Warrior']
            },
            {
                'name': 'Mystical Mail',
                'tier': 3,
                'cost': 2500,
                'category': 'defense',
                'physical_protection': 50,
                'health': 300,
                'passive_name': 'Mystical',
                'passive_description': 'AoE damage aura',
                'recommended_for': ['Guardian', 'Warrior']
            },
            {
                'name': 'Mantle of Discord',
                'tier': 3,
                'cost': 2900,
                'category': 'defense',
                'physical_protection': 60,
                'magical_protection': 60,
                'passive_name': 'Discord',
                'passive_description': 'CC immunity at low HP',
                'recommended_for': ['Guardian', 'Warrior']
            },
            {
                'name': 'Spirit Robe',
                'tier': 3,
                'cost': 2500,
                'category': 'defense',
                'physical_protection': 40,
                'magical_protection': 40,
                'cooldown_reduction': 20,
                'passive_name': 'Spirit Robe',
                'passive_description': 'CC reduction and damage mitigation',
                'recommended_for': ['Guardian', 'Warrior']
            },
            {
                'name': 'Stone of Gaia',
                'tier': 3,
                'cost': 2300,
                'category': 'defense',
                'health': 400,
                'hp5': 25,
                'passive_name': 'Gaia',
                'passive_description': 'Heals when knocked up',
                'recommended_for': ['Guardian', 'Warrior']
            },
            {
                'name': 'Void Stone',
                'tier': 3,
                'cost': 2400,
                'category': 'defense',
                'magical_protection': 60,
                'intelligence': 40,
                'passive_name': 'Void Stone',
                'passive_description': 'Reduces enemy magical protections',
                'recommended_for': ['Guardian', 'Mage']
            },
            {
                'name': "Emperor's Armor",
                'tier': 3,
                'cost': 2200,
                'category': 'defense',
                'physical_protection': 55,
                'health': 200,
                'passive_name': 'Emperor',
                'passive_description': 'Slows enemy tower attack speed',
                'recommended_for': ['Guardian']
            },
            {
                'name': 'Mail of Renewal',
                'tier': 3,
                'cost': 2300,
                'category': 'defense',
                'health': 300,
                'hp5': 20,
                'passive_name': 'Renewal',
                'passive_description': 'Heals on assist',
                'recommended_for': ['Guardian', 'Warrior']
            },
            
            # Hybrid & Utility Items
            {
                'name': 'Relic Dagger',
                'tier': 3,
                'cost': 2300,
                'category': 'utility',
                'health': 300,
                'cooldown_reduction': 20,
                'passive_name': 'Relic Dagger',
                'passive_description': 'Reduces relic cooldowns',
                'recommended_for': ['Guardian', 'Warrior']
            },
            {
                'name': 'Winged Blade',
                'tier': 3,
                'cost': 2200,
                'category': 'utility',
                'health': 300,
                'passive_name': 'Winged Blade',
                'passive_description': 'Movement speed, immune to slows',
                'recommended_for': ['Guardian', 'Warrior']
            },
            {
                'name': 'Stone of Binding',
                'tier': 3,
                'cost': 2200,
                'category': 'utility',
                'physical_protection': 30,
                'magical_protection': 30,
                'passive_name': 'Binding',
                'passive_description': 'Applies protection shred on CC',
                'recommended_for': ['Guardian']
            },
            {
                'name': 'Hide of the Urchin',
                'tier': 3,
                'cost': 2500,
                'category': 'defense',
                'physical_protection': 45,
                'magical_protection': 45,
                'health': 250,
                'passive_name': 'Urchin',
                'passive_description': 'Stacks for more protections',
                'recommended_for': ['Guardian', 'Warrior']
            },
            {
                'name': 'Pridwen',
                'tier': 3,
                'cost': 2600,
                'category': 'defense',
                'physical_protection': 30,
                'magical_protection': 30,
                'cooldown_reduction': 20,
                'passive_name': 'Pridwen',
                'passive_description': 'Shield after using ult',
                'recommended_for': ['Guardian', 'Warrior']
            },
            {
                'name': 'Lotus Crown',
                'tier': 3,
                'cost': 2400,
                'category': 'utility',
                'intelligence': 60,
                'physical_protection': 30,
                'magical_protection': 30,
                'passive_name': 'Lotus Crown',
                'passive_description': 'Buffs allies on heal/shield',
                'recommended_for': ['Guardian', 'Mage']
            },
            {
                'name': 'Celestial Legion Helm',
                'tier': 3,
                'cost': 2400,
                'category': 'defense',
                'magical_protection': 60,
                'health': 200,
                'passive_name': 'Celestial',
                'passive_description': 'Blocks basic attacks',
                'recommended_for': ['Guardian', 'Warrior']
            },
            {
                'name': 'The Sledge',
                'tier': 3,
                'cost': 2500,
                'category': 'hybrid',
                'strength': 30,
                'health': 350,
                'physical_protection': 25,
                'passive_name': 'Sledge',
                'passive_description': 'Sustain and protections',
                'recommended_for': ['Warrior']
            }
        ]

    def run(self):
        """Run the complete data population"""
        try:
            self.connect()
            
            print("Starting SMITE 2 data population...")
            
            # Clear existing data
            self.clear_existing_data()
            
            # Populate gods
            print("\nPopulating gods data...")
            self.populate_gods_data()
            
            # Populate items
            print("\nPopulating items data...")
            self.populate_items_data()
            
            # Update metadata
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO metadata (key, value) 
                VALUES ('last_updated', datetime('now'))
            """)
            cursor.execute("""
                INSERT OR REPLACE INTO metadata (key, value) 
                VALUES ('data_version', '2.0_comprehensive')
            """)
            
            self.conn.commit()
            
            # Print summary
            cursor.execute("SELECT COUNT(*) FROM gods")
            god_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM items")
            item_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM abilities")
            ability_count = cursor.fetchone()[0]
            
            print(f"\n✅ Data population complete!")
            print(f"📊 Summary:")
            print(f"   - Gods: {god_count}")
            print(f"   - Items: {item_count}")
            print(f"   - Abilities: {ability_count}")
            
        except Exception as e:
            print(f"❌ Error during data population: {e}")
            if self.conn:
                self.conn.rollback()
        finally:
            self.disconnect()

if __name__ == "__main__":
    populator = SMITE2DataPopulator()
    populator.run()