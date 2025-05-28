#!/usr/bin/env python3
"""
Enhanced SMITE 2 Items Scraper - Multiple Sources
Scrapes from smite2.live, SmiteSource, and other sources for comprehensive data
"""

import requests
import json
import sqlite3
import re
import time
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Set
import logging
from bs4 import BeautifulSoup
import asyncio
import aiohttp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EnhancedSmiteItem:
    """Enhanced SMITE item with comprehensive data"""
    name: str
    category: str
    tier: int
    cost: int
    stats: Dict[str, int]
    passive: str
    description: str
    assault_priority: int
    counters: List[str]
    image_url: str
    source: str
    item_id: Optional[str] = None
    build_path: List[str] = None
    tags: List[str] = None

class EnhancedItemsScraper:
    """Multi-source SMITE 2 items scraper"""
    
    def __init__(self):
        self.sources = {
            'smite2_live': 'https://smite2.live',
            'smitesource': 'https://smitesource.com',
            'smitefire': 'https://smitefire.com'
        }
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        self.data_dir = Path("enhanced_items")
        self.data_dir.mkdir(exist_ok=True)
        self.db_path = self.data_dir / "enhanced_items.db"
        
        self._init_database()
        
    def _init_database(self):
        """Initialize enhanced items database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS enhanced_items (
                    name TEXT PRIMARY KEY,
                    category TEXT,
                    tier INTEGER,
                    cost INTEGER,
                    stats TEXT,
                    passive TEXT,
                    description TEXT,
                    assault_priority INTEGER,
                    counters TEXT,
                    image_url TEXT,
                    source TEXT,
                    item_id TEXT,
                    build_path TEXT,
                    tags TEXT,
                    last_updated TEXT
                )
            """)
    
    async def scrape_smite2_live(self) -> List[EnhancedSmiteItem]:
        """Scrape items from smite2.live"""
        logger.info("🔍 Scraping smite2.live...")
        items = []
        
        try:
            # Try different API endpoints
            api_urls = [
                f"{self.sources['smite2_live']}/api/items",
                f"{self.sources['smite2_live']}/api/v1/items",
                f"{self.sources['smite2_live']}/items.json"
            ]
            
            async with aiohttp.ClientSession() as session:
                for url in api_urls:
                    try:
                        async with session.get(url, timeout=10) as response:
                            if response.status == 200:
                                data = await response.json()
                                items = self._parse_smite2_live_data(data)
                                if items:
                                    logger.info(f"✅ Found {len(items)} items from smite2.live API")
                                    return items
                    except Exception as e:
                        logger.debug(f"API endpoint {url} failed: {e}")
                        continue
                
                # If API fails, try scraping the page
                try:
                    async with session.get(f"{self.sources['smite2_live']}/items", timeout=15) as response:
                        if response.status == 200:
                            html = await response.text()
                            items = self._parse_smite2_live_html(html)
                            if items:
                                logger.info(f"✅ Scraped {len(items)} items from smite2.live HTML")
                                return items
                except Exception as e:
                    logger.warning(f"HTML scraping failed: {e}")
                    
        except Exception as e:
            logger.warning(f"⚠️ smite2.live scraping failed: {e}")
        
        return items
    
    def _parse_smite2_live_data(self, data) -> List[EnhancedSmiteItem]:
        """Parse items from smite2.live JSON data"""
        items = []
        
        # Handle different data structures
        if isinstance(data, dict):
            if 'items' in data:
                items_data = data['items']
            elif 'data' in data:
                items_data = data['data']
            else:
                items_data = data
        else:
            items_data = data
        
        if isinstance(items_data, list):
            for item_data in items_data:
                item = self._create_enhanced_item_from_smite2_live(item_data)
                if item:
                    items.append(item)
        
        return items
    
    def _parse_smite2_live_html(self, html: str) -> List[EnhancedSmiteItem]:
        """Parse items from smite2.live HTML"""
        items = []
        
        # Look for JSON data in script tags
        json_patterns = [
            r'window\.__INITIAL_STATE__\s*=\s*({.+?});',
            r'window\.__NUXT__\s*=\s*({.+?});',
            r'__NEXT_DATA__\s*=\s*({.+?})',
            r'items\s*:\s*(\[.+?\])',
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, html, re.DOTALL)
            for match in matches:
                try:
                    data = json.loads(match)
                    parsed_items = self._parse_smite2_live_data(data)
                    if parsed_items:
                        items.extend(parsed_items)
                        break
                except json.JSONDecodeError:
                    continue
        
        return items
    
    def _create_enhanced_item_from_smite2_live(self, item_data: dict) -> Optional[EnhancedSmiteItem]:
        """Create enhanced item from smite2.live data"""
        try:
            name = item_data.get('name', '').strip()
            if not name or len(name) < 2:
                return None
            
            # Extract comprehensive data
            tier = item_data.get('tier', 3)
            cost = item_data.get('cost', item_data.get('price', 1500))
            passive = item_data.get('passive', item_data.get('description', ''))
            item_id = item_data.get('id', item_data.get('itemId'))
            
            # Extract stats
            stats = self._extract_enhanced_stats(item_data)
            
            # Determine category and tags
            category = self._determine_enhanced_category(stats, item_data)
            tags = self._extract_tags(item_data, passive)
            
            # Build path
            build_path = self._extract_build_path(item_data)
            
            # Calculate Assault priority
            assault_priority = self._calculate_enhanced_assault_priority(name, stats, passive, tags)
            
            # Determine counters
            counters = self._determine_enhanced_counters(name, passive, tags)
            
            # Image URL
            image_url = self._get_image_url(item_data, 'smite2_live')
            
            return EnhancedSmiteItem(
                name=name,
                category=category,
                tier=tier,
                cost=cost,
                stats=stats,
                passive=passive,
                description=f"{category} item - {passive[:100]}..." if passive else f"{category} item",
                assault_priority=assault_priority,
                counters=counters,
                image_url=image_url,
                source='smite2_live',
                item_id=str(item_id) if item_id else None,
                build_path=build_path,
                tags=tags
            )
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to create item from smite2.live data: {e}")
            return None
    
    def _extract_enhanced_stats(self, item_data: dict) -> Dict[str, int]:
        """Extract stats with enhanced parsing"""
        stats = {}
        
        # Try different stat formats
        stats_sources = [
            item_data.get('stats', {}),
            item_data.get('attributes', {}),
            item_data.get('properties', {})
        ]
        
        for stats_source in stats_sources:
            if isinstance(stats_source, dict):
                for key, value in stats_source.items():
                    readable_key = self._convert_stat_name(key)
                    if readable_key and isinstance(value, (int, float, str)):
                        try:
                            stats[readable_key] = int(float(str(value)))
                        except ValueError:
                            pass
            elif isinstance(stats_source, list):
                for stat in stats_source:
                    if isinstance(stat, dict):
                        name = stat.get('name', stat.get('type', ''))
                        value = stat.get('value', stat.get('amount', 0))
                        readable_name = self._convert_stat_name(name)
                        if readable_name:
                            try:
                                stats[readable_name] = int(float(str(value)))
                            except ValueError:
                                pass
        
        return stats
    
    def _convert_stat_name(self, stat_name: str) -> str:
        """Enhanced stat name conversion"""
        if not stat_name:
            return ""
        
        conversions = {
            # Power
            'PhysicalPower': 'Physical Power',
            'MagicalPower': 'Magical Power',
            'power': 'Power',
            'physicalPower': 'Physical Power',
            'magicalPower': 'Magical Power',
            
            # Health/Mana
            'MaxHealth': 'Health',
            'MaxMana': 'Mana',
            'health': 'Health',
            'mana': 'Mana',
            'hp': 'Health',
            'mp': 'Mana',
            
            # Protections
            'PhysicalProtection': 'Physical Protection',
            'MagicalProtection': 'Magical Protection',
            'physicalProtection': 'Physical Protection',
            'magicalProtection': 'Magical Protection',
            'armor': 'Physical Protection',
            'magicResist': 'Magical Protection',
            
            # Other stats
            'MovementSpeed': 'Movement Speed',
            'AttackSpeed': 'Attack Speed',
            'CriticalStrikeChance': 'Critical Strike Chance',
            'HealthPerTime': 'Health Per 5',
            'ManaPerTime': 'Mana Per 5',
            'CooldownReduction': 'Cooldown Reduction',
            'Penetration': 'Penetration',
            'PhysicalPenetration': 'Physical Penetration',
            'MagicalPenetration': 'Magical Penetration',
            
            # Simplified names
            'movementSpeed': 'Movement Speed',
            'attackSpeed': 'Attack Speed',
            'critChance': 'Critical Strike Chance',
            'hp5': 'Health Per 5',
            'mp5': 'Mana Per 5',
            'cdr': 'Cooldown Reduction',
            'pen': 'Penetration'
        }
        
        return conversions.get(stat_name, stat_name.title().replace('_', ' '))
    
    def _determine_enhanced_category(self, stats: Dict[str, int], item_data: dict) -> str:
        """Enhanced category determination"""
        item_type = item_data.get('type', item_data.get('category', ''))
        
        if item_type.lower() in ['starter', 'blessing']:
            return "Starter"
        elif item_type.lower() in ['consumable', 'potion']:
            return "Consumable"
        elif item_type.lower() in ['relic', 'active']:
            return "Relic"
        
        # Analyze stats
        if any(stat in stats for stat in ['Physical Power', 'Power']) and 'Magical Power' not in stats:
            return "Physical"
        elif 'Magical Power' in stats:
            return "Magical"
        elif any(prot in stats for prot in ['Physical Protection', 'Magical Protection']):
            return "Defensive"
        else:
            return "Utility"
    
    def _extract_tags(self, item_data: dict, passive: str) -> List[str]:
        """Extract item tags for better categorization"""
        tags = []
        
        # From item data
        if 'tags' in item_data:
            tags.extend(item_data['tags'])
        
        # From passive analysis
        passive_lower = passive.lower()
        if any(word in passive_lower for word in ['heal', 'regeneration', 'restore']):
            tags.append('sustain')
        if any(word in passive_lower for word in ['antiheal', 'anti-heal', 'reduced healing']):
            tags.append('antiheal')
        if any(word in passive_lower for word in ['stealth', 'invisible', 'reveal']):
            tags.append('stealth')
        if any(word in passive_lower for word in ['critical', 'crit']):
            tags.append('critical')
        if any(word in passive_lower for word in ['penetration', 'pen']):
            tags.append('penetration')
        
        return list(set(tags))  # Remove duplicates
    
    def _extract_build_path(self, item_data: dict) -> List[str]:
        """Extract item build path"""
        build_path = []
        
        if 'recipe' in item_data:
            recipe = item_data['recipe']
            if isinstance(recipe, list):
                for component in recipe:
                    if isinstance(component, dict) and 'name' in component:
                        build_path.append(component['name'])
                    elif isinstance(component, str):
                        build_path.append(component)
        
        return build_path
    
    def _calculate_enhanced_assault_priority(self, name: str, stats: Dict, passive: str, tags: List[str]) -> int:
        """Enhanced Assault priority calculation"""
        priority = 5  # Base priority
        
        name_lower = name.lower()
        passive_lower = passive.lower()
        
        # Critical items for Assault
        if 'antiheal' in tags or any(word in name_lower for word in ['divine ruin', 'toxic blade', 'brawlers']):
            priority = 10  # Anti-heal is absolutely crucial
        elif any(word in name_lower for word in ['meditation', 'salvation']):
            priority = 9   # Sustain is very important
        elif 'sustain' in tags:
            priority = 8   # Other sustain items
        elif any(word in name_lower for word in ['mystical mail', 'spectral']):
            priority = 8   # Counter items
        elif 'Health' in stats and stats['Health'] > 300:
            priority = 7   # High health items good in Assault
        elif 'penetration' in tags:
            priority = 7   # Penetration important for damage
        elif any(word in passive_lower for word in ['crowd control', 'cc reduction']):
            priority = 6   # CC items useful
        elif stats.get('Physical Power', 0) > 60 or stats.get('Magical Power', 0) > 80:
            priority = 6   # High damage items
        
        return min(10, max(1, priority))
    
    def _determine_enhanced_counters(self, name: str, passive: str, tags: List[str]) -> List[str]:
        """Enhanced counter determination"""
        counters = []
        
        # From tags
        if 'antiheal' in tags:
            counters.append('healing')
        if 'stealth' in tags:
            counters.append('stealth')
        if 'critical' in tags:
            counters.append('critical_strikes')
        
        # From text analysis
        text = f"{name} {passive}".lower()
        
        if any(word in text for word in ['basic attack', 'auto attack', 'attack speed']):
            counters.append('basic_attacks')
        if any(word in text for word in ['crowd control', 'cc', 'stun', 'root', 'slow']):
            counters.append('crowd_control')
        if any(word in text for word in ['burst', 'ability damage']):
            counters.append('burst_damage')
        if any(word in text for word in ['tank', 'protection', 'damage reduction']):
            counters.append('damage')
        
        return list(set(counters))  # Remove duplicates
    
    def _get_image_url(self, item_data: dict, source: str) -> str:
        """Get item image URL"""
        image_fields = ['image', 'icon', 'imagePath', 'iconUrl', 'imageUrl']
        
        for field in image_fields:
            if field in item_data and item_data[field]:
                image_path = item_data[field]
                
                # Handle relative URLs
                if image_path.startswith('/'):
                    return f"{self.sources.get(source, '')}{image_path}"
                elif image_path.startswith('http'):
                    return image_path
                else:
                    # Construct URL based on source
                    if source == 'smite2_live':
                        return f"https://smite2.live/images/items/{image_path}"
                    elif source == 'smitesource':
                        return f"https://d2igbp6929t5ry.cloudfront.net/{image_path}"
        
        return ""
    
    def create_comprehensive_database(self) -> List[EnhancedSmiteItem]:
        """Create comprehensive items database from all sources"""
        logger.info("🔄 Creating comprehensive SMITE 2 items database...")
        
        all_items = []
        
        # Try smite2.live first (async)
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            smite2_items = loop.run_until_complete(self.scrape_smite2_live())
            all_items.extend(smite2_items)
            loop.close()
        except Exception as e:
            logger.warning(f"⚠️ smite2.live failed: {e}")
        
        # If we don't have enough items, add essential ones
        if len(all_items) < 20:
            essential_items = self._create_essential_smite2_items()
            all_items.extend(essential_items)
        
        # Remove duplicates by name
        unique_items = {}
        for item in all_items:
            if item.name not in unique_items:
                unique_items[item.name] = item
            else:
                # Keep the one with more data
                existing = unique_items[item.name]
                if len(item.stats) > len(existing.stats) or item.source == 'smite2_live':
                    unique_items[item.name] = item
        
        final_items = list(unique_items.values())
        logger.info(f"✅ Created database with {len(final_items)} unique items")
        
        return final_items
    
    def _create_essential_smite2_items(self) -> List[EnhancedSmiteItem]:
        """Create essential SMITE 2 items with accurate data"""
        logger.info("📦 Creating essential SMITE 2 items database...")
        
        essential_items = [
            # Anti-heal items (CRITICAL for Assault)
            EnhancedSmiteItem(
                name="Divine Ruin",
                category="Magical",
                tier=3,
                cost=2050,
                stats={"Magical Power": 80, "Magical Penetration": 15},
                passive="Enemies hit by your abilities have 40% reduced healing for 8 seconds",
                description="Essential anti-healing item for magical gods",
                assault_priority=5,  # Only becomes 10 when healers present
                counters=["healing"],
                image_url="https://smite2.live/images/items/divine_ruin.png",
                source="manual",
                tags=["antiheal", "penetration"]
            ),
            EnhancedSmiteItem(
                name="Toxic Blade",
                category="Physical",
                tier=3,
                cost=2050,
                stats={"Physical Power": 30, "Attack Speed": 25, "Physical Penetration": 15},
                passive="Enemies hit by your basic attacks have 40% reduced healing for 8 seconds",
                description="Essential anti-healing item for physical gods",
                assault_priority=5,  # Only becomes 10 when healers present
                counters=["healing"],
                image_url="https://smite2.live/images/items/toxic_blade.png",
                source="manual",
                tags=["antiheal", "attack_speed"]
            ),
            EnhancedSmiteItem(
                name="Brawler's Beat Stick",
                category="Physical",
                tier=3,
                cost=2300,
                stats={"Physical Power": 40, "Physical Penetration": 15},
                passive="Enemies hit by your abilities have 40% reduced healing for 8 seconds",
                description="Anti-healing item for physical ability gods",
                assault_priority=5,  # Only becomes 10 when healers present
                counters=["healing"],
                image_url="https://smite2.live/images/items/brawlers_beat_stick.png",
                source="manual",
                tags=["antiheal", "penetration"]
            ),
            
            # Sustain items (VERY IMPORTANT for Assault)
            EnhancedSmiteItem(
                name="Meditation Cloak",
                category="Relic",
                tier=1,
                cost=0,
                stats={"Mana": 300, "Mana Per 5": 7},
                passive="Active: Restore 75% mana and heal for 30% max health over 3 seconds",
                description="Essential sustain relic for Assault",
                assault_priority=9,
                counters=[],
                image_url="https://smite2.live/images/relics/meditation.png",
                source="manual",
                tags=["sustain", "mana"]
            ),
            
            # Core damage items
            EnhancedSmiteItem(
                name="Rod of Tahuti",
                category="Magical",
                tier=3,
                cost=3000,
                stats={"Magical Power": 120, "Mana": 300},
                passive="Increases Magical Power by 25%",
                description="Core magical power item",
                assault_priority=6,
                counters=[],
                image_url="https://smite2.live/images/items/rod_of_tahuti.png",
                source="manual",
                tags=["power"]
            ),
            EnhancedSmiteItem(
                name="Deathbringer",
                category="Physical",
                tier=3,
                cost=2800,
                stats={"Physical Power": 50, "Critical Strike Chance": 30},
                passive="Critical strikes deal +40% damage",
                description="Core critical strike item",
                assault_priority=6,
                counters=[],
                image_url="https://smite2.live/images/items/deathbringer.png",
                source="manual",
                tags=["critical", "power"]
            ),
            
            # Penetration items
            EnhancedSmiteItem(
                name="Obsidian Shard",
                category="Magical",
                tier=3,
                cost=2050,
                stats={"Magical Power": 70, "Magical Penetration": 20},
                passive="Your abilities gain +33% Magical Penetration",
                description="Essential magical penetration",
                assault_priority=7,
                counters=[],
                image_url="https://smite2.live/images/items/obsidian_shard.png",
                source="manual",
                tags=["penetration", "power"]
            ),
            EnhancedSmiteItem(
                name="Titan's Bane",
                category="Physical",
                tier=3,
                cost=2050,
                stats={"Physical Power": 40, "Physical Penetration": 20},
                passive="Your abilities gain +33% Physical Penetration",
                description="Essential physical penetration",
                assault_priority=7,
                counters=[],
                image_url="https://smite2.live/images/items/titans_bane.png",
                source="manual",
                tags=["penetration", "power"]
            ),
            
            # Counter items
            EnhancedSmiteItem(
                name="Spectral Armor",
                category="Defensive",
                tier=3,
                cost=2100,
                stats={"Health": 200, "Physical Protection": 60},
                passive="Critical strikes against you deal 50% reduced damage",
                description="Counter to critical strike builds",
                assault_priority=7,
                counters=["critical_strikes"],
                image_url="https://smite2.live/images/items/spectral_armor.png",
                source="manual",
                tags=["defensive", "counter"]
            ),
            EnhancedSmiteItem(
                name="Mystical Mail",
                category="Defensive",
                tier=3,
                cost=2100,
                stats={"Health": 300, "Physical Protection": 40},
                passive="Deals 40 magical damage per second to nearby enemies",
                description="Defensive item with damage aura",
                assault_priority=7,
                counters=["stealth"],
                image_url="https://smite2.live/images/items/mystical_mail.png",
                source="manual",
                tags=["defensive", "aura"]
            )
        ]
        
        return essential_items
    
    def save_enhanced_items(self, items: List[EnhancedSmiteItem]):
        """Save enhanced items to database"""
        with sqlite3.connect(self.db_path) as conn:
            for item in items:
                conn.execute("""
                    INSERT OR REPLACE INTO enhanced_items VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    item.name,
                    item.category,
                    item.tier,
                    item.cost,
                    json.dumps(item.stats),
                    item.passive,
                    item.description,
                    item.assault_priority,
                    json.dumps(item.counters),
                    item.image_url,
                    item.source,
                    item.item_id,
                    json.dumps(item.build_path or []),
                    json.dumps(item.tags or []),
                    "2025-01-01 00:00:00"
                ))
        
        logger.info(f"💾 Saved {len(items)} enhanced items to database")
    
    def get_assault_recommendations(self, enemy_team: List[str], ally_team: List[str] = None) -> List[EnhancedSmiteItem]:
        """Get smart Assault recommendations based on team compositions"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM enhanced_items ORDER BY assault_priority DESC, cost ASC
            """)
            
            all_items = []
            for row in cursor.fetchall():
                item = EnhancedSmiteItem(
                    name=row[0], category=row[1], tier=row[2], cost=row[3],
                    stats=json.loads(row[4]), passive=row[5], description=row[6],
                    assault_priority=row[7], counters=json.loads(row[8]), image_url=row[9],
                    source=row[10], item_id=row[11], build_path=json.loads(row[12]),
                    tags=json.loads(row[13])
                )
                all_items.append(item)
        
        recommendations = []
        
        # ASSAULT PRIORITY 1: SUSTAIN COUNTERS
        # Any form of healing/sustain is CRITICAL to counter in Assault
        primary_healers = ['aphrodite', 'ra']  # Main healers with significant healing
        minor_healers = ['neith', 'cupid', 'sobek']  # Gods with minor heal abilities
        lifesteal_gods = ['anubis', 'hades']  # Gods with built-in lifesteal
        # Note: Geb removed - his shield doesn't count as healing for anti-heal purposes
        
        has_primary_healers = any(god.lower() in primary_healers for god in enemy_team)
        has_minor_healers = any(god.lower() in minor_healers for god in enemy_team)
        has_lifesteal_gods = any(god.lower() in lifesteal_gods for god in enemy_team)
        has_any_sustain = has_primary_healers or has_minor_healers or has_lifesteal_gods
        
        if has_any_sustain:
            # CRITICAL: Anti-heal is MANDATORY in Assault vs any sustain
            antiheal_items = [item for item in all_items if 'antiheal' in (item.tags or [])]
            
            if has_primary_healers:
                # Primary healers = Priority 10 (MUST HAVE)
                for item in antiheal_items[:3]:
                    item.assault_priority = 10
                recommendations.extend(antiheal_items[:3])
            elif has_minor_healers or has_lifesteal_gods:
                # Minor sustain = Priority 8 (Very Important)
                for item in antiheal_items[:2]:
                    item.assault_priority = 8
                recommendations.extend(antiheal_items[:2])
        
        # ASSAULT PRIORITY 2: DAMAGE MITIGATION
        hunters = ['artemis', 'neith', 'apollo', 'anhur', 'cupid']
        burst_mages = ['zeus', 'poseidon', 'kukulkan', 'anubis']
        heavy_cc = ['ares', 'ymir']
        
        has_hunters = any(god.lower() in hunters for god in enemy_team)
        has_burst_mages = any(god.lower() in burst_mages for god in enemy_team)
        has_heavy_cc = any(god.lower() in heavy_cc for god in enemy_team)
        
        if has_hunters:
            # Hunters = Spectral Armor Priority 7 (Assault meta)
            spectral_items = [item for item in all_items if 'spectral' in item.name.lower()]
            for item in spectral_items:
                item.assault_priority = 7
            recommendations.extend(spectral_items[:1])
        
        # ASSAULT PRIORITY 3: SUSTAIN FOR YOUR TEAM (CRITICAL)
        meditation_items = [item for item in all_items if 'meditation' in item.name.lower()]
        for item in meditation_items:
            item.assault_priority = 9  # Meditation is MANDATORY in Assault
        recommendations.extend(meditation_items[:1])
        
        # ASSAULT PRIORITY 4: CC IMMUNITY
        if has_heavy_cc:
            beads_items = [item for item in all_items if 'purification' in item.name.lower()]
            for item in beads_items:
                item.assault_priority = 8  # Beads vs Ares/Ymir
            recommendations.extend(beads_items[:1])
        
        # Add penetration items (always valuable in Assault team fights)
        # But exclude anti-heal items if no healers present
        pen_items = [item for item in all_items if 'penetration' in (item.tags or [])]
        if not has_any_sustain:
            # Filter out anti-heal items when no healers
            pen_items = [item for item in pen_items if 'antiheal' not in (item.tags or [])]
        recommendations.extend(pen_items[:1])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for item in recommendations:
            if item.name not in seen:
                seen.add(item.name)
                unique_recommendations.append(item)
        
        # Sort by Assault priority (highest first)
        unique_recommendations.sort(key=lambda x: x.assault_priority, reverse=True)
        return unique_recommendations[:6]  # Top 6 recommendations for Assault

def main():
    """Test the enhanced scraper"""
    scraper = EnhancedItemsScraper()
    
    # Create comprehensive database
    items = scraper.create_comprehensive_database()
    scraper.save_enhanced_items(items)
    
    # Test recommendations
    print("\n🎯 Assault Recommendations vs Healing Team:")
    recommendations = scraper.get_assault_recommendations(['Aphrodite', 'Ra', 'Zeus', 'Ares', 'Neith'])
    for item in recommendations:
        tags_str = ', '.join(item.tags or [])
        print(f"  🔥 {item.name} ({item.category}) - {item.cost}g - Priority: {item.assault_priority}")
        print(f"     Tags: {tags_str}")
        print(f"     {item.passive[:80]}...")
        print()

if __name__ == "__main__":
    main()