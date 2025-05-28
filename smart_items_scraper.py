#!/usr/bin/env python3
"""
Smart SMITE Items Scraper - Uses SmiteSource API for accurate data
Extracts real item data from the embedded JSON in SmiteSource pages
"""

import requests
import json
import sqlite3
import re
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SmiteItem:
    """SMITE item with all relevant data"""
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

class SmartItemsScraper:
    """Efficient scraper using SmiteSource's embedded JSON data"""
    
    def __init__(self):
        self.base_url = "https://smitesource.com"
        self.items_url = f"{self.base_url}/items"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        self.data_dir = Path("smart_items")
        self.data_dir.mkdir(exist_ok=True)
        self.db_path = self.data_dir / "items.db"
        
        self._init_database()
        
    def _init_database(self):
        """Initialize items database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS items (
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
                    last_updated TEXT
                )
            """)
    
    def scrape_items_from_api(self) -> List[SmiteItem]:
        """Extract items from SmiteSource's embedded JSON"""
        logger.info("🔍 Extracting items from SmiteSource API...")
        
        try:
            response = self.session.get(self.items_url, timeout=15)
            response.raise_for_status()
            
            # Extract JSON data from the page
            content = response.text
            
            # Find the JSON data in the script tag
            json_match = re.search(r'self\.__next_f\.push\(\[1,"([^"]+)"\]\)', content)
            if not json_match:
                logger.warning("⚠️ Could not find JSON data in page")
                return self._create_essential_items()
            
            # Decode the JSON string
            json_str = json_match.group(1)
            # Unescape the JSON
            json_str = json_str.replace('\\"', '"').replace('\\\\', '\\')
            
            # Parse the JSON
            try:
                data = json.loads(json_str)
                return self._parse_items_data(data)
            except json.JSONDecodeError:
                logger.warning("⚠️ Failed to parse JSON data")
                return self._create_essential_items()
                
        except Exception as e:
            logger.error(f"❌ Failed to scrape items: {e}")
            return self._create_essential_items()
    
    def _parse_items_data(self, data) -> List[SmiteItem]:
        """Parse items from the JSON data structure"""
        items = []
        
        # The data structure is complex, let's extract items recursively
        def find_items(obj, path=""):
            if isinstance(obj, dict):
                # Look for item-like objects
                if 'name' in obj and 'tier' in obj and 'stats' in obj:
                    item = self._create_item_from_data(obj)
                    if item:
                        items.append(item)
                
                # Recurse into nested objects
                for key, value in obj.items():
                    find_items(value, f"{path}.{key}")
                    
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    find_items(item, f"{path}[{i}]")
        
        find_items(data)
        
        if not items:
            logger.warning("⚠️ No items found in JSON data, using fallback")
            return self._create_essential_items()
        
        logger.info(f"✅ Extracted {len(items)} items from API")
        return items
    
    def _create_item_from_data(self, item_data: dict) -> Optional[SmiteItem]:
        """Create SmiteItem from JSON data"""
        try:
            name = item_data.get('name', '')
            if not name or len(name) < 2:
                return None
            
            # Extract basic info
            tier = item_data.get('tier', 3)
            item_type = item_data.get('itemType', 'Item')
            passive = item_data.get('passive', '') or ''
            
            # Calculate cost from recipe
            cost = self._calculate_cost(item_data)
            
            # Extract stats
            stats = self._extract_stats(item_data.get('stats', []))
            
            # Determine category
            category = self._determine_category(stats, item_type, name)
            
            # Calculate Assault priority
            assault_priority = self._calculate_assault_priority(name, stats, passive)
            
            # Determine counters
            counters = self._determine_counters(name, passive)
            
            # Get image URL
            image_path = item_data.get('imagePath', '')
            image_url = f"https://d2igbp6929t5ry.cloudfront.net/{image_path}" if image_path else ""
            
            return SmiteItem(
                name=name,
                category=category,
                tier=tier,
                cost=cost,
                stats=stats,
                passive=passive,
                description=f"{category} item - {passive[:100]}..." if passive else f"{category} item",
                assault_priority=assault_priority,
                counters=counters,
                image_url=image_url
            )
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to create item from data: {e}")
            return None
    
    def _calculate_cost(self, item_data: dict) -> int:
        """Calculate item cost from recipe data"""
        recipe = item_data.get('recipe', [])
        if recipe and len(recipe) > 0:
            return recipe[0].get('goldCost', 1500)
        
        # Fallback based on tier
        tier = item_data.get('tier', 3)
        tier_costs = {1: 500, 2: 1000, 3: 2000, 4: 3000}
        return tier_costs.get(tier, 1500)
    
    def _extract_stats(self, stats_list: List[dict]) -> Dict[str, int]:
        """Extract stats from stats array"""
        stats = {}
        
        for stat in stats_list:
            stat_name = stat.get('statName', '')
            stat_value = stat.get('statValue', '0')
            
            # Convert stat names to readable format
            readable_name = self._convert_stat_name(stat_name)
            if readable_name:
                try:
                    stats[readable_name] = int(stat_value)
                except ValueError:
                    pass
        
        return stats
    
    def _convert_stat_name(self, stat_name: str) -> str:
        """Convert API stat names to readable format"""
        conversions = {
            'PhysicalPower': 'Physical Power',
            'MagicalPower': 'Magical Power',
            'MaxHealth': 'Health',
            'MaxMana': 'Mana',
            'PhysicalProtection': 'Physical Protection',
            'MagicalProtection': 'Magical Protection',
            'MovementSpeed': 'Movement Speed',
            'AttackSpeed': 'Attack Speed',
            'CriticalStrikeChance': 'Critical Strike Chance',
            'HealthPerTime': 'Health Per 5',
            'ManaPerTime': 'Mana Per 5',
            'CooldownReduction': 'Cooldown Reduction'
        }
        
        return conversions.get(stat_name, stat_name)
    
    def _determine_category(self, stats: Dict[str, int], item_type: str, name: str) -> str:
        """Determine item category"""
        if item_type == "Starter":
            return "Starter"
        
        if 'Physical Power' in stats:
            return "Physical"
        elif 'Magical Power' in stats:
            return "Magical"
        elif any(prot in stats for prot in ['Physical Protection', 'Magical Protection']):
            return "Defensive"
        else:
            return "Utility"
    
    def _calculate_assault_priority(self, name: str, stats: Dict, passive: str) -> int:
        """Calculate item priority for Assault mode (1-10)"""
        priority = 5  # Base priority
        
        name_lower = name.lower()
        passive_lower = passive.lower()
        
        # High priority items for Assault
        if any(word in name_lower for word in ['divine ruin', 'toxic blade', 'brawlers']):
            priority = 9  # Anti-heal is crucial
        elif any(word in name_lower for word in ['meditation', 'salvation']):
            priority = 8  # Sustain is important
        elif any(word in name_lower for word in ['mystical mail', 'spectral']):
            priority = 7  # Counter items
        elif any(word in passive_lower for word in ['healing', 'antiheal', 'anti-heal']):
            priority = 9  # Anti-heal passives
        elif 'Health' in stats and stats['Health'] > 200:
            priority = 7  # Tanky items good in Assault
        elif any(word in passive_lower for word in ['heal', 'regeneration']):
            priority = 6  # Sustain passives
        elif any(word in name_lower for word in ['penetration', 'obsidian', 'titans']):
            priority = 6  # Penetration important
        
        return min(10, max(1, priority))
    
    def _determine_counters(self, name: str, passive: str) -> List[str]:
        """Determine what this item counters"""
        counters = []
        
        text = f"{name} {passive}".lower()
        
        if any(word in text for word in ['healing', 'antiheal', 'anti-heal', 'reduced healing']):
            counters.append('healing')
        if any(word in text for word in ['stealth', 'invisible', 'reveal']):
            counters.append('stealth')
        if any(word in text for word in ['critical', 'crit']):
            counters.append('critical_strikes')
        if any(word in text for word in ['basic attack', 'auto attack']):
            counters.append('basic_attacks')
        if any(word in text for word in ['crowd control', 'cc', 'stun', 'root']):
            counters.append('crowd_control')
        
        return counters
    
    def _create_essential_items(self) -> List[SmiteItem]:
        """Create essential items with manual data as fallback"""
        logger.info("📦 Creating essential items database...")
        
        essential_items = [
            SmiteItem(
                name="Divine Ruin",
                category="Magical",
                tier=3,
                cost=2050,
                stats={"Magical Power": 80, "Magical Penetration": 15},
                passive="Enemies hit by your abilities have 40% reduced healing for 8 seconds",
                description="Anti-healing item for magical gods",
                assault_priority=9,
                counters=["healing"],
                image_url="https://d2igbp6929t5ry.cloudfront.net/Items/T3/Icon_T3_DivineRuin.png"
            ),
            SmiteItem(
                name="Toxic Blade",
                category="Physical",
                tier=3,
                cost=2050,
                stats={"Physical Power": 30, "Attack Speed": 25, "Penetration": 15},
                passive="Enemies hit by your basic attacks have 40% reduced healing for 8 seconds",
                description="Anti-healing item for physical gods",
                assault_priority=9,
                counters=["healing"],
                image_url="https://d2igbp6929t5ry.cloudfront.net/Items/T3/Icon_T3_ToxicBlade.png"
            ),
            SmiteItem(
                name="Brawler's Beat Stick",
                category="Physical",
                tier=3,
                cost=2300,
                stats={"Physical Power": 40, "Physical Penetration": 15},
                passive="Enemies hit by your abilities have 40% reduced healing for 8 seconds",
                description="Anti-healing item for physical ability gods",
                assault_priority=9,
                counters=["healing"],
                image_url="https://d2igbp6929t5ry.cloudfront.net/Items/T3/Icon_T3_BrawlersBeatStick.png"
            ),
            SmiteItem(
                name="Mystical Mail",
                category="Defensive",
                tier=3,
                cost=2100,
                stats={"Health": 300, "Physical Protection": 40},
                passive="Deals 40 magical damage per second to nearby enemies. Also reveals stealthed enemies",
                description="Defensive item that reveals stealth",
                assault_priority=7,
                counters=["stealth"],
                image_url="https://d2igbp6929t5ry.cloudfront.net/Items/T3/Icon_T3_MysticalMail.png"
            ),
            SmiteItem(
                name="Spectral Armor",
                category="Defensive",
                tier=3,
                cost=2100,
                stats={"Health": 200, "Physical Protection": 60},
                passive="Critical strikes against you deal 50% reduced damage",
                description="Counter to critical strike builds",
                assault_priority=6,
                counters=["critical_strikes"],
                image_url="https://d2igbp6929t5ry.cloudfront.net/Items/T3/Icon_T3_SpectralArmor.png"
            ),
            SmiteItem(
                name="Meditation Cloak",
                category="Utility",
                tier=1,
                cost=500,
                stats={"Mana": 300, "MP5": 7},
                passive="Active: Restore 75% mana and heal for 30% max health over 3 seconds",
                description="Essential sustain item for Assault",
                assault_priority=8,
                counters=[],
                image_url="https://d2igbp6929t5ry.cloudfront.net/Items/Relics/Icon_Relic_Meditation.png"
            ),
            SmiteItem(
                name="Rod of Tahuti",
                category="Magical",
                tier=3,
                cost=3000,
                stats={"Magical Power": 120, "Mana": 300},
                passive="Increases Magical Power by 25%",
                description="Core magical power item",
                assault_priority=6,
                counters=[],
                image_url="https://d2igbp6929t5ry.cloudfront.net/Items/T3/Icon_T3_RodOfTahuti.png"
            ),
            SmiteItem(
                name="Deathbringer",
                category="Physical",
                tier=3,
                cost=2800,
                stats={"Physical Power": 50, "Critical Strike Chance": 30},
                passive="Critical strikes deal +40% damage",
                description="Core critical strike item",
                assault_priority=6,
                counters=[],
                image_url="https://d2igbp6929t5ry.cloudfront.net/Items/T3/Icon_T3_Deathbringer.png"
            ),
            SmiteItem(
                name="Obsidian Shard",
                category="Magical",
                tier=3,
                cost=2050,
                stats={"Magical Power": 70, "Magical Penetration": 20},
                passive="Your abilities gain +33% Magical Penetration",
                description="Magical penetration item",
                assault_priority=6,
                counters=[],
                image_url="https://d2igbp6929t5ry.cloudfront.net/Items/T3/Icon_T3_ObsidianShard.png"
            ),
            SmiteItem(
                name="Titan's Bane",
                category="Physical",
                tier=3,
                cost=2050,
                stats={"Physical Power": 40, "Physical Penetration": 20},
                passive="Your abilities gain +33% Physical Penetration",
                description="Physical penetration item",
                assault_priority=6,
                counters=[],
                image_url="https://d2igbp6929t5ry.cloudfront.net/Items/T3/Icon_T3_TitansBane.png"
            )
        ]
        
        return essential_items
    
    def save_items(self, items: List[SmiteItem]):
        """Save items to database"""
        with sqlite3.connect(self.db_path) as conn:
            for item in items:
                conn.execute("""
                    INSERT OR REPLACE INTO items VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    "2025-01-01 00:00:00"
                ))
        
        logger.info(f"💾 Saved {len(items)} items to database")
    
    def get_items_by_priority(self, min_priority: int = 6) -> List[SmiteItem]:
        """Get items by Assault priority"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM items WHERE assault_priority >= ? ORDER BY assault_priority DESC
            """, (min_priority,))
            
            items = []
            for row in cursor.fetchall():
                items.append(SmiteItem(
                    name=row[0],
                    category=row[1],
                    tier=row[2],
                    cost=row[3],
                    stats=json.loads(row[4]),
                    passive=row[5],
                    description=row[6],
                    assault_priority=row[7],
                    counters=json.loads(row[8]),
                    image_url=row[9]
                ))
            
            return items
    
    def get_counter_items(self, counter_type: str) -> List[SmiteItem]:
        """Get items that counter specific things"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM items WHERE counters LIKE ? ORDER BY assault_priority DESC
            """, (f'%{counter_type}%',))
            
            items = []
            for row in cursor.fetchall():
                item_counters = json.loads(row[8])
                if counter_type in item_counters:
                    items.append(SmiteItem(
                        name=row[0],
                        category=row[1],
                        tier=row[2],
                        cost=row[3],
                        stats=json.loads(row[4]),
                        passive=row[5],
                        description=row[6],
                        assault_priority=row[7],
                        counters=item_counters,
                        image_url=row[9]
                    ))
            
            return items
    
    def get_recommended_items(self, enemy_team_has: List[str]) -> List[SmiteItem]:
        """Get recommended items based on enemy team composition"""
        recommendations = []
        
        # Check what to counter
        if any('heal' in god.lower() for god in enemy_team_has):
            recommendations.extend(self.get_counter_items('healing'))
        
        if any(god.lower() in ['loki', 'serqet'] for god in enemy_team_has):
            recommendations.extend(self.get_counter_items('stealth'))
        
        # Add high priority items
        high_priority = self.get_items_by_priority(8)
        recommendations.extend(high_priority)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for item in recommendations:
            if item.name not in seen:
                seen.add(item.name)
                unique_recommendations.append(item)
        
        return unique_recommendations[:5]  # Top 5 recommendations

def main():
    """Test the smart scraper"""
    scraper = SmartItemsScraper()
    
    # Scrape items
    items = scraper.scrape_items_from_api()
    scraper.save_items(items)
    
    # Test queries
    print("\n🔥 High Priority Assault Items:")
    high_priority = scraper.get_items_by_priority(8)
    for item in high_priority[:5]:
        print(f"  {item.name} (Priority: {item.assault_priority}) - {item.cost}g")
    
    print("\n🩸 Anti-Heal Items:")
    antiheal = scraper.get_counter_items('healing')
    for item in antiheal:
        print(f"  {item.name} - {item.passive[:50]}...")
    
    print("\n👁️ Anti-Stealth Items:")
    antistealth = scraper.get_counter_items('stealth')
    for item in antistealth:
        print(f"  {item.name} - {item.passive[:50]}...")
    
    print("\n🎯 Recommendations vs Healing Team:")
    recommendations = scraper.get_recommended_items(['Aphrodite', 'Ra', 'Hel'])
    for item in recommendations:
        print(f"  {item.name} ({item.category}) - {item.cost}g")

if __name__ == "__main__":
    main()