#!/usr/bin/env python3
"""
SMITE Items Scraper - Real item data from SmiteSource.com
Scrapes all items with stats, descriptions, and builds for accurate recommendations
"""

import requests
from bs4 import BeautifulSoup
import json
import sqlite3
import time
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
    category: str  # Physical, Magical, Defensive, etc.
    tier: int  # 1, 2, 3, 4 (starter, tier1, tier2, tier3)
    cost: int
    stats: Dict[str, int]  # {"Physical Power": 25, "Health": 200}
    passive: str
    description: str
    builds_from: List[str]  # Items this builds from
    builds_into: List[str]  # Items this builds into
    assault_priority: int  # 1-10 priority in Assault mode
    counters: List[str]  # What this item counters (healing, stealth, etc.)

class SmiteItemsScraper:
    """Scrapes and manages SMITE item data"""
    
    def __init__(self):
        self.base_url = "https://smitesource.com"
        self.items_url = f"{self.base_url}/items"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        self.data_dir = Path("items_data")
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
                    stats TEXT,  -- JSON
                    passive TEXT,
                    description TEXT,
                    builds_from TEXT,  -- JSON array
                    builds_into TEXT,  -- JSON array
                    assault_priority INTEGER,
                    counters TEXT,  -- JSON array
                    last_updated TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS item_builds (
                    god_name TEXT,
                    role TEXT,
                    build_order TEXT,  -- JSON array of item names
                    build_type TEXT,  -- "starter", "core", "situational"
                    win_rate REAL,
                    last_updated TEXT
                )
            """)
    
    def scrape_items_list(self) -> List[str]:
        """Get list of all items from SmiteSource"""
        logger.info("🔍 Scraping items list from SmiteSource...")
        
        try:
            response = self.session.get(self.items_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find item links - SmiteSource uses specific CSS classes
            item_links = []
            
            # Look for item cards or links
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if '/items/' in href and href not in item_links:
                    item_links.append(href)
            
            # Also look for item names in data attributes or text
            for item_element in soup.find_all(['div', 'span'], class_=lambda x: x and 'item' in x.lower()):
                item_name = item_element.get_text(strip=True)
                if item_name and len(item_name) > 2:
                    item_links.append(f"/items/{item_name.lower().replace(' ', '-')}")
            
            logger.info(f"✅ Found {len(item_links)} potential items")
            return list(set(item_links))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"❌ Failed to scrape items list: {e}")
            return self._get_fallback_items()
    
    def _get_fallback_items(self) -> List[str]:
        """Fallback list of essential SMITE items"""
        return [
            # Anti-heal items
            "divine-ruin", "toxic-blade", "brawlers-beat-stick", "cursed-ankh",
            # Penetration
            "obsidian-shard", "titans-bane", "dominance", "serrated-edge",
            # Defense
            "spectral-armor", "mystical-mail", "sovereignty", "heartward-amulet",
            # Utility
            "meditation-cloak", "aegis-amulet", "purification-beads", "blink-rune",
            # Core damage
            "rod-of-tahuti", "deathbringer", "qins-sais", "soul-reaver",
            # Sustain
            "bancrofts-talon", "bloodforge", "stone-of-gaia", "mail-of-renewal"
        ]
    
    def scrape_item_details(self, item_path: str) -> Optional[SmiteItem]:
        """Scrape detailed information for a specific item"""
        if not item_path.startswith('http'):
            url = f"{self.base_url}{item_path}"
        else:
            url = item_path
            
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract item name
            name = self._extract_item_name(soup)
            if not name:
                return None
                
            # Extract other details
            category = self._extract_category(soup)
            tier = self._extract_tier(soup)
            cost = self._extract_cost(soup)
            stats = self._extract_stats(soup)
            passive = self._extract_passive(soup)
            description = self._extract_description(soup)
            builds_from = self._extract_builds_from(soup)
            builds_into = self._extract_builds_into(soup)
            
            # Calculate Assault priority and counters
            assault_priority = self._calculate_assault_priority(name, stats, passive)
            counters = self._determine_counters(name, passive, description)
            
            return SmiteItem(
                name=name,
                category=category,
                tier=tier,
                cost=cost,
                stats=stats,
                passive=passive,
                description=description,
                builds_from=builds_from,
                builds_into=builds_into,
                assault_priority=assault_priority,
                counters=counters
            )
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to scrape {item_path}: {e}")
            return None
    
    def _extract_item_name(self, soup: BeautifulSoup) -> str:
        """Extract item name from page"""
        # Try multiple selectors
        selectors = [
            'h1', '.item-name', '.item-title', 
            '[data-item-name]', '.page-title'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                name = element.get_text(strip=True)
                if name and len(name) > 1:
                    return name
        
        return ""
    
    def _extract_category(self, soup: BeautifulSoup) -> str:
        """Extract item category"""
        # Look for category indicators
        text = soup.get_text().lower()
        
        if any(word in text for word in ['physical power', 'physical damage']):
            return "Physical"
        elif any(word in text for word in ['magical power', 'magical damage']):
            return "Magical"
        elif any(word in text for word in ['protections', 'health', 'defense']):
            return "Defensive"
        elif any(word in text for word in ['movement speed', 'cooldown', 'mana']):
            return "Utility"
        else:
            return "Unknown"
    
    def _extract_tier(self, soup: BeautifulSoup) -> int:
        """Extract item tier"""
        text = soup.get_text().lower()
        
        if 'starter' in text or 'blessing' in text:
            return 1
        elif any(word in text for word in ['tier 1', 't1', 'basic']):
            return 2
        elif any(word in text for word in ['tier 2', 't2', 'advanced']):
            return 3
        elif any(word in text for word in ['tier 3', 't3', 'finished']):
            return 4
        else:
            return 3  # Default to tier 3
    
    def _extract_cost(self, soup: BeautifulSoup) -> int:
        """Extract item cost"""
        # Look for cost indicators
        import re
        
        text = soup.get_text()
        cost_match = re.search(r'(\d{1,4})\s*gold', text, re.IGNORECASE)
        if cost_match:
            return int(cost_match.group(1))
        
        # Fallback cost estimates by tier
        tier = self._extract_tier(soup)
        cost_estimates = {1: 700, 2: 1000, 3: 1500, 4: 2500}
        return cost_estimates.get(tier, 1500)
    
    def _extract_stats(self, soup: BeautifulSoup) -> Dict[str, int]:
        """Extract item stats"""
        stats = {}
        text = soup.get_text()
        
        # Common stat patterns
        import re
        stat_patterns = {
            'Physical Power': r'(\d+)\s*physical\s*power',
            'Magical Power': r'(\d+)\s*magical\s*power',
            'Health': r'(\d+)\s*health',
            'Mana': r'(\d+)\s*mana',
            'Physical Protection': r'(\d+)\s*physical\s*protection',
            'Magical Protection': r'(\d+)\s*magical\s*protection',
            'Movement Speed': r'(\d+)%?\s*movement\s*speed',
            'Cooldown Reduction': r'(\d+)%\s*cooldown\s*reduction',
            'Attack Speed': r'(\d+)%\s*attack\s*speed',
            'Critical Strike Chance': r'(\d+)%\s*critical\s*strike',
            'Penetration': r'(\d+)\s*penetration'
        }
        
        for stat_name, pattern in stat_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                stats[stat_name] = int(match.group(1))
        
        return stats
    
    def _extract_passive(self, soup: BeautifulSoup) -> str:
        """Extract item passive description"""
        # Look for passive sections
        passive_indicators = ['passive', 'unique passive', 'aura']
        
        for indicator in passive_indicators:
            for element in soup.find_all(text=lambda text: text and indicator in text.lower()):
                parent = element.parent
                if parent:
                    passive_text = parent.get_text(strip=True)
                    if len(passive_text) > 20:  # Meaningful passive
                        return passive_text[:200]  # Limit length
        
        return ""
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract item description"""
        # Look for description sections
        desc_selectors = ['.description', '.item-desc', 'p']
        
        for selector in desc_selectors:
            element = soup.select_one(selector)
            if element:
                desc = element.get_text(strip=True)
                if len(desc) > 10:
                    return desc[:300]  # Limit length
        
        return ""
    
    def _extract_builds_from(self, soup: BeautifulSoup) -> List[str]:
        """Extract items this builds from"""
        # This would need specific SmiteSource structure analysis
        return []
    
    def _extract_builds_into(self, soup: BeautifulSoup) -> List[str]:
        """Extract items this builds into"""
        # This would need specific SmiteSource structure analysis
        return []
    
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
        elif 'health' in stats and stats['health'] > 200:
            priority = 7  # Tanky items good in Assault
        elif any(word in passive_lower for word in ['heal', 'regeneration']):
            priority = 6  # Sustain passives
        elif any(word in name_lower for word in ['penetration', 'obsidian', 'titans']):
            priority = 6  # Penetration important
        
        return min(10, max(1, priority))
    
    def _determine_counters(self, name: str, passive: str, description: str) -> List[str]:
        """Determine what this item counters"""
        counters = []
        
        text = f"{name} {passive} {description}".lower()
        
        if any(word in text for word in ['healing', 'antiheal', 'anti-heal']):
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
    
    def save_item(self, item: SmiteItem):
        """Save item to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO items VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item.name,
                item.category,
                item.tier,
                item.cost,
                json.dumps(item.stats),
                item.passive,
                item.description,
                json.dumps(item.builds_from),
                json.dumps(item.builds_into),
                item.assault_priority,
                json.dumps(item.counters),
                time.strftime('%Y-%m-%d %H:%M:%S')
            ))
    
    def scrape_all_items(self):
        """Scrape all items and save to database"""
        logger.info("🚀 Starting full item scrape...")
        
        # Get items list
        item_paths = self.scrape_items_list()
        
        if not item_paths:
            logger.warning("⚠️ No items found, using fallback data")
            self._create_fallback_items()
            return
        
        scraped_count = 0
        for i, item_path in enumerate(item_paths[:50]):  # Limit to avoid overwhelming
            logger.info(f"📦 Scraping item {i+1}/{min(50, len(item_paths))}: {item_path}")
            
            item = self.scrape_item_details(item_path)
            if item:
                self.save_item(item)
                scraped_count += 1
                
            # Be respectful to the server
            time.sleep(1)
        
        logger.info(f"✅ Scraped {scraped_count} items successfully")
    
    def _create_fallback_items(self):
        """Create essential items with manual data"""
        essential_items = [
            SmiteItem(
                name="Divine Ruin",
                category="Magical",
                tier=3,
                cost=2050,
                stats={"Magical Power": 80, "Magical Penetration": 15},
                passive="Enemies hit by your abilities have 40% reduced healing for 8 seconds",
                description="Anti-healing item for magical gods",
                builds_from=["Lost Artifact", "Cursed Orb"],
                builds_into=[],
                assault_priority=9,
                counters=["healing"]
            ),
            SmiteItem(
                name="Toxic Blade",
                category="Physical",
                tier=3,
                cost=2050,
                stats={"Physical Power": 30, "Attack Speed": 25, "Penetration": 15},
                passive="Enemies hit by your basic attacks have 40% reduced healing for 8 seconds",
                description="Anti-healing item for physical gods",
                builds_from=["Short Sword", "Cursed Gauntlet"],
                builds_into=[],
                assault_priority=9,
                counters=["healing"]
            ),
            SmiteItem(
                name="Mystical Mail",
                category="Defensive",
                tier=3,
                cost=2100,
                stats={"Health": 300, "Physical Protection": 40},
                passive="Deals 40 magical damage per second to nearby enemies. Also reveals stealthed enemies",
                description="Defensive item that reveals stealth",
                builds_from=["Leather Armor", "Cloak"],
                builds_into=[],
                assault_priority=7,
                counters=["stealth"]
            ),
            SmiteItem(
                name="Meditation Cloak",
                category="Utility",
                tier=1,
                cost=500,
                stats={"Mana": 300, "MP5": 7},
                passive="Active: Restore 75% mana and heal for 30% max health over 3 seconds",
                description="Essential sustain item for Assault",
                builds_from=[],
                builds_into=["Salvation"],
                assault_priority=8,
                counters=[]
            )
        ]
        
        for item in essential_items:
            self.save_item(item)
        
        logger.info(f"✅ Created {len(essential_items)} fallback items")
    
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
                    builds_from=json.loads(row[7]),
                    builds_into=json.loads(row[8]),
                    assault_priority=row[9],
                    counters=json.loads(row[10])
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
                item_counters = json.loads(row[10])
                if counter_type in item_counters:
                    items.append(SmiteItem(
                        name=row[0],
                        category=row[1],
                        tier=row[2],
                        cost=row[3],
                        stats=json.loads(row[4]),
                        passive=row[5],
                        description=row[6],
                        builds_from=json.loads(row[7]),
                        builds_into=json.loads(row[8]),
                        assault_priority=row[9],
                        counters=item_counters
                    ))
            
            return items

def main():
    """Test the scraper"""
    scraper = SmiteItemsScraper()
    
    # Scrape items
    scraper.scrape_all_items()
    
    # Test queries
    print("\n🔥 High Priority Assault Items:")
    high_priority = scraper.get_items_by_priority(8)
    for item in high_priority[:5]:
        print(f"  {item.name} (Priority: {item.assault_priority})")
    
    print("\n🩸 Anti-Heal Items:")
    antiheal = scraper.get_counter_items('healing')
    for item in antiheal:
        print(f"  {item.name} - {item.passive[:50]}...")
    
    print("\n👁️ Anti-Stealth Items:")
    antistealth = scraper.get_counter_items('stealth')
    for item in antistealth:
        print(f"  {item.name} - {item.passive[:50]}...")

if __name__ == "__main__":
    main()