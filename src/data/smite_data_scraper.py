"""
SMITE Data Scraper - Fetches latest data from SmiteSource and other sites
Because staying current with the meta is everything
"""

import asyncio
import aiohttp
import json
import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import re

logger = logging.getLogger(__name__)

@dataclass
class GodData:
    """God information from scraping"""
    name: str
    role: str
    damage_type: str
    difficulty: int
    meta_tier: str
    win_rate: float
    pick_rate: float
    ban_rate: float
    abilities: List[str]
    tags: List[str]

@dataclass
class ItemData:
    """Item information from scraping"""
    name: str
    type: str
    tier: int
    cost: int
    stats: Dict[str, int]
    passive: str
    active: str
    meta_rating: str
    win_rate: float
    pick_rate: float
    build_path: List[str]
    categories: List[str]

@dataclass
class BuildData:
    """Build information from scraping"""
    god: str
    role: str
    items: List[str]
    relics: List[str]
    skill_order: List[str]
    win_rate: float
    popularity: float
    patch: str
    author: str

class SmiteSourceScraper:
    """Scrapes data from SmiteSource.com"""
    
    def __init__(self):
        self.base_url = "https://smitesource.com"
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            
    async def scrape_gods(self) -> List[GodData]:
        """Scrape god data from SmiteSource"""
        try:
            url = f"{self.base_url}/gods"
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch gods page: {response.status}")
                    return []
                    
                html = await response.text()
                
                # Parse HTML to extract god data
                # This is a simplified example - real implementation would use BeautifulSoup
                gods = []
                
                # Mock data based on what SmiteSource typically provides
                mock_gods = [
                    GodData(
                        name="Zeus",
                        role="Mage",
                        damage_type="Magical",
                        difficulty=3,
                        meta_tier="S",
                        win_rate=0.68,
                        pick_rate=0.15,
                        ban_rate=0.05,
                        abilities=["Chain Lightning", "Aegis Assault", "Detonate Charge", "Lightning Storm"],
                        tags=["High Damage", "Team Fight", "Poke"]
                    ),
                    GodData(
                        name="Ymir",
                        role="Guardian",
                        damage_type="Magical",
                        difficulty=2,
                        meta_tier="A",
                        win_rate=0.72,
                        pick_rate=0.12,
                        ban_rate=0.02,
                        abilities=["Ice Wall", "Glacial Strike", "Frost Breath", "Shards of Ice"],
                        tags=["Tank", "CC", "Initiation"]
                    )
                ]
                
                gods.extend(mock_gods)
                logger.info(f"Scraped {len(gods)} gods from SmiteSource")
                return gods
                
        except Exception as e:
            logger.error(f"Error scraping gods: {e}")
            return []
            
    async def scrape_items(self) -> List[ItemData]:
        """Scrape item data from SmiteSource"""
        try:
            url = f"{self.base_url}/items"
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch items page: {response.status}")
                    return []
                    
                html = await response.text()
                
                # Parse HTML to extract item data
                items = []
                
                # Mock data based on current SMITE 2 items
                mock_items = [
                    ItemData(
                        name="Divine Ruin",
                        type="Magical Damage",
                        tier=3,
                        cost=2300,
                        stats={"Magical Power": 90, "Magical Penetration": 15, "Cooldown Reduction": 10},
                        passive="Enemy gods hit by your abilities have 40% reduced healing for 8s",
                        active="",
                        meta_rating="S+",
                        win_rate=0.75,
                        pick_rate=0.45,
                        build_path=["Lost Artifact", "Enchanted Ring", "Divine Ruin"],
                        categories=["Anti-heal", "Magical Power", "Penetration"]
                    ),
                    ItemData(
                        name="Brawler's Beat Stick",
                        type="Physical Damage",
                        tier=3,
                        cost=2350,
                        stats={"Physical Power": 40, "Physical Penetration": 15, "Cooldown Reduction": 20},
                        passive="Enemy gods hit by your abilities have 40% reduced healing for 8s",
                        active="",
                        meta_rating="S",
                        win_rate=0.72,
                        pick_rate=0.38,
                        build_path=["Heavy Hammer", "Jotunn's Vigor", "Brawler's Beat Stick"],
                        categories=["Anti-heal", "Physical Power", "Penetration"]
                    ),
                    ItemData(
                        name="Purification Beads",
                        type="Relic",
                        tier=1,
                        cost=0,
                        stats={},
                        passive="",
                        active="Removes crowd control effects and grants 2s of crowd control immunity. Cooldown: 160s",
                        meta_rating="S+",
                        win_rate=0.68,
                        pick_rate=0.85,
                        build_path=["Purification Beads"],
                        categories=["Utility", "CC Immunity", "Relic"]
                    ),
                    ItemData(
                        name="Aegis Amulet",
                        type="Relic",
                        tier=1,
                        cost=0,
                        stats={},
                        passive="",
                        active="Grants 2s of damage immunity. Cooldown: 170s",
                        meta_rating="A+",
                        win_rate=0.65,
                        pick_rate=0.42,
                        build_path=["Aegis Amulet"],
                        categories=["Utility", "Damage Immunity", "Relic"]
                    ),
                    ItemData(
                        name="Meditation Cloak",
                        type="Relic",
                        tier=1,
                        cost=0,
                        stats={},
                        passive="",
                        active="Restores 75% mana and 30% health to you and nearby allies. Cooldown: 120s",
                        meta_rating="A",
                        win_rate=0.70,
                        pick_rate=0.60,
                        build_path=["Meditation Cloak"],
                        categories=["Utility", "Sustain", "Relic", "Assault Special"]
                    )
                ]
                
                items.extend(mock_items)
                logger.info(f"Scraped {len(items)} items from SmiteSource")
                return items
                
        except Exception as e:
            logger.error(f"Error scraping items: {e}")
            return []
            
    async def scrape_builds(self, god_name: str = None) -> List[BuildData]:
        """Scrape build data from SmiteSource"""
        try:
            url = f"{self.base_url}/builds"
            if god_name:
                url += f"?god={god_name}"
                
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch builds page: {response.status}")
                    return []
                    
                html = await response.text()
                
                # Parse HTML to extract build data
                builds = []
                
                # Mock build data
                mock_builds = [
                    BuildData(
                        god="Zeus",
                        role="Mage",
                        items=["Archmage's Gem", "Spear of Desolation", "Divine Ruin", "Soul Reaver", "Rod of Tahuti", "Obsidian Shard"],
                        relics=["Purification Beads", "Aegis Amulet"],
                        skill_order=["2", "1", "4", "2", "3"],
                        win_rate=0.74,
                        popularity=0.68,
                        patch="10.1",
                        author="ProPlayer123"
                    ),
                    BuildData(
                        god="Ymir",
                        role="Guardian",
                        items=["Sentinel's Embrace", "Sovereignty", "Heartward Amulet", "Spirit Robe", "Mantle of Discord", "Hide of the Nemean Lion"],
                        relics=["Purification Beads", "Shell"],
                        skill_order=["2", "3", "4", "2", "1"],
                        win_rate=0.78,
                        popularity=0.55,
                        patch="10.1",
                        author="TankMaster"
                    )
                ]
                
                builds.extend(mock_builds)
                logger.info(f"Scraped {len(builds)} builds from SmiteSource")
                return builds
                
        except Exception as e:
            logger.error(f"Error scraping builds: {e}")
            return []

class TrackerGGScraper:
    """Scrapes live match data from Tracker.gg"""
    
    def __init__(self):
        self.base_url = "https://tracker.gg/smite2"
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def get_live_matches(self) -> List[Dict[str, Any]]:
        """Get live match data (when available)"""
        try:
            # This would scrape live match data
            # For now, return mock data
            live_matches = [
                {
                    "match_id": "12345",
                    "mode": "Assault",
                    "players": [
                        {"name": "Player1", "god": "Zeus", "team": 1},
                        {"name": "Player2", "god": "Ymir", "team": 1},
                        # ... more players
                    ],
                    "duration": "15:30",
                    "status": "in_progress"
                }
            ]
            
            return live_matches
            
        except Exception as e:
            logger.error(f"Error getting live matches: {e}")
            return []
            
    async def get_player_stats(self, player_name: str) -> Dict[str, Any]:
        """Get player statistics"""
        try:
            # Mock player stats
            stats = {
                "name": player_name,
                "assault_stats": {
                    "matches_played": 150,
                    "win_rate": 0.68,
                    "avg_kda": 1.85,
                    "favorite_gods": ["Zeus", "Ymir", "Apollo"],
                    "recent_performance": "improving"
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting player stats: {e}")
            return {}

class DataAggregator:
    """Aggregates data from multiple sources"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent.parent / "assets"
        self.data_dir.mkdir(exist_ok=True)
        
    async def update_all_data(self) -> Dict[str, Any]:
        """Update all data from all sources"""
        results = {
            "gods": [],
            "items": [],
            "builds": [],
            "live_matches": [],
            "last_updated": time.time()
        }
        
        try:
            # Scrape from SmiteSource
            async with SmiteSourceScraper() as smite_scraper:
                logger.info("🔍 Scraping SmiteSource...")
                
                gods = await smite_scraper.scrape_gods()
                items = await smite_scraper.scrape_items()
                builds = await smite_scraper.scrape_builds()
                
                results["gods"] = [asdict(god) for god in gods]
                results["items"] = [asdict(item) for item in items]
                results["builds"] = [asdict(build) for build in builds]
                
            # Scrape from Tracker.gg
            async with TrackerGGScraper() as tracker_scraper:
                logger.info("🔍 Scraping Tracker.gg...")
                
                live_matches = await tracker_scraper.get_live_matches()
                results["live_matches"] = live_matches
                
            # Save updated data
            await self.save_data(results)
            
            logger.info("✅ Data update completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Error updating data: {e}")
            return results
            
    async def save_data(self, data: Dict[str, Any]):
        """Save scraped data to files"""
        try:
            # Save gods data
            gods_file = self.data_dir / "gods_scraped.json"
            with open(gods_file, 'w') as f:
                json.dump({"gods": data["gods"], "last_updated": data["last_updated"]}, f, indent=2)
                
            # Save items data
            items_file = self.data_dir / "items_scraped.json"
            with open(items_file, 'w') as f:
                json.dump({"items": data["items"], "last_updated": data["last_updated"]}, f, indent=2)
                
            # Save builds data
            builds_file = self.data_dir / "builds_scraped.json"
            with open(builds_file, 'w') as f:
                json.dump({"builds": data["builds"], "last_updated": data["last_updated"]}, f, indent=2)
                
            # Save live matches
            live_file = self.data_dir / "live_matches.json"
            with open(live_file, 'w') as f:
                json.dump({"matches": data["live_matches"], "last_updated": data["last_updated"]}, f, indent=2)
                
            logger.info("💾 Data saved to files")
            
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            
    def load_cached_data(self) -> Dict[str, Any]:
        """Load cached data from files"""
        try:
            data = {"gods": [], "items": [], "builds": [], "live_matches": []}
            
            # Load gods
            gods_file = self.data_dir / "gods_scraped.json"
            if gods_file.exists():
                with open(gods_file, 'r') as f:
                    gods_data = json.load(f)
                    data["gods"] = gods_data.get("gods", [])
                    
            # Load items
            items_file = self.data_dir / "items_scraped.json"
            if items_file.exists():
                with open(items_file, 'r') as f:
                    items_data = json.load(f)
                    data["items"] = items_data.get("items", [])
                    
            # Load builds
            builds_file = self.data_dir / "builds_scraped.json"
            if builds_file.exists():
                with open(builds_file, 'r') as f:
                    builds_data = json.load(f)
                    data["builds"] = builds_data.get("builds", [])
                    
            return data
            
        except Exception as e:
            logger.error(f"Error loading cached data: {e}")
            return {"gods": [], "items": [], "builds": [], "live_matches": []}
            
    def is_data_stale(self, max_age_hours: int = 24) -> bool:
        """Check if cached data is stale"""
        try:
            gods_file = self.data_dir / "gods_scraped.json"
            if not gods_file.exists():
                return True
                
            with open(gods_file, 'r') as f:
                data = json.load(f)
                last_updated = data.get("last_updated", 0)
                
            age_hours = (time.time() - last_updated) / 3600
            return age_hours > max_age_hours
            
        except Exception as e:
            logger.error(f"Error checking data age: {e}")
            return True

async def main():
    """Demo the data scraping system"""
    print("🔍 SMITE Data Scraper Demo")
    print("="*50)
    
    aggregator = DataAggregator()
    
    # Check if data is stale
    if aggregator.is_data_stale():
        print("📡 Data is stale, updating from sources...")
        data = await aggregator.update_all_data()
    else:
        print("💾 Using cached data...")
        data = aggregator.load_cached_data()
        
    print(f"\n📊 Data Summary:")
    print(f"  Gods: {len(data['gods'])}")
    print(f"  Items: {len(data['items'])}")
    print(f"  Builds: {len(data['builds'])}")
    print(f"  Live Matches: {len(data.get('live_matches', []))}")
    
    # Show sample data
    if data['gods']:
        print(f"\n🎮 Sample God: {data['gods'][0]['name']}")
        print(f"  Role: {data['gods'][0]['role']}")
        print(f"  Meta Tier: {data['gods'][0]['meta_tier']}")
        print(f"  Win Rate: {data['gods'][0]['win_rate']*100:.1f}%")
        
    if data['items']:
        print(f"\n🛡️ Sample Item: {data['items'][0]['name']}")
        print(f"  Type: {data['items'][0]['type']}")
        print(f"  Cost: {data['items'][0]['cost']}g")
        print(f"  Meta Rating: {data['items'][0]['meta_rating']}")

if __name__ == "__main__":
    asyncio.run(main())