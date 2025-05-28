#!/usr/bin/env python3
"""
🌐 SMITE 2 Live Data Scraper
Efficient scraping of SmiteSource.com and Tracker.gg for essential data only
"""

import asyncio
import aiohttp
import json
import sqlite3
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LiveDataScraper:
    """Efficient scraper for SMITE 2 data - only gets what we need"""
    
    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path("live_data")
        self.data_dir.mkdir(exist_ok=True)
        
        self.db_path = self.data_dir / "live_data.db"
        self.session = None
        
        # Rate limiting
        self.last_request = {}
        self.min_delay = 2.0  # Seconds between requests to same domain
        
        self._init_database()
        logger.info("✅ Live data scraper initialized")
    
    def _init_database(self):
        """Initialize database for live data"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS live_gods (
                    name TEXT PRIMARY KEY,
                    role TEXT,
                    win_rate REAL,
                    pick_rate REAL,
                    tier TEXT,
                    last_updated TEXT,
                    source TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS live_items (
                    name TEXT PRIMARY KEY,
                    cost INTEGER,
                    tier TEXT,
                    effectiveness REAL,
                    last_updated TEXT,
                    source TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS meta_info (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    last_updated TEXT
                )
            """)
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if not self.session:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session
    
    async def _rate_limited_get(self, url: str) -> Optional[str]:
        """Rate-limited HTTP GET"""
        domain = url.split('/')[2]
        
        # Check rate limit
        if domain in self.last_request:
            elapsed = time.time() - self.last_request[domain]
            if elapsed < self.min_delay:
                await asyncio.sleep(self.min_delay - elapsed)
        
        try:
            session = await self._get_session()
            async with session.get(url, timeout=10) as response:
                self.last_request[domain] = time.time()
                
                if response.status == 200:
                    return await response.text()
                else:
                    logger.warning(f"HTTP {response.status} for {url}")
                    return None
                    
        except Exception as e:
            logger.error(f"Request failed for {url}: {e}")
            return None
    
    async def scrape_smitesource_gods(self) -> Dict[str, Any]:
        """Scrape god data from SmiteSource.com"""
        logger.info("🔍 Scraping SmiteSource god data...")
        
        # SmiteSource god tier list URL (example - adjust for actual site structure)
        url = "https://smitesource.com/gods"
        
        html = await self._rate_limited_get(url)
        if not html:
            logger.error("❌ Failed to get SmiteSource god data")
            return {}
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            gods_data = {}
            
            # Parse god data (this would need to be adjusted based on actual site structure)
            # For now, using mock data structure
            god_elements = soup.find_all('div', class_='god-card')  # Example selector
            
            for element in god_elements:
                try:
                    name = element.find('h3').text.strip()
                    role = element.find('.role').text.strip()
                    
                    # Extract win rate if available
                    win_rate_elem = element.find('.win-rate')
                    win_rate = float(win_rate_elem.text.replace('%', '')) / 100 if win_rate_elem else 0.5
                    
                    # Extract tier
                    tier_elem = element.find('.tier')
                    tier = tier_elem.text.strip() if tier_elem else 'B'
                    
                    gods_data[name.lower()] = {
                        'name': name,
                        'role': role,
                        'win_rate': win_rate,
                        'tier': tier,
                        'source': 'smitesource',
                        'last_updated': datetime.now().isoformat()
                    }
                    
                except Exception as e:
                    logger.warning(f"Failed to parse god element: {e}")
                    continue
            
            logger.info(f"✅ Scraped {len(gods_data)} gods from SmiteSource")
            return gods_data
            
        except Exception as e:
            logger.error(f"❌ SmiteSource parsing failed: {e}")
            return {}
    
    async def scrape_tracker_gg_stats(self) -> Dict[str, Any]:
        """Scrape statistics from Tracker.gg"""
        logger.info("🔍 Scraping Tracker.gg statistics...")
        
        # Tracker.gg SMITE stats URL (example)
        url = "https://tracker.gg/smite/insights"
        
        html = await self._rate_limited_get(url)
        if not html:
            logger.error("❌ Failed to get Tracker.gg data")
            return {}
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            stats_data = {}
            
            # Parse statistics (adjust selectors based on actual site)
            stat_elements = soup.find_all('div', class_='stat-card')
            
            for element in stat_elements:
                try:
                    god_name = element.find('.god-name').text.strip()
                    pick_rate_elem = element.find('.pick-rate')
                    win_rate_elem = element.find('.win-rate')
                    
                    if pick_rate_elem and win_rate_elem:
                        pick_rate = float(pick_rate_elem.text.replace('%', '')) / 100
                        win_rate = float(win_rate_elem.text.replace('%', '')) / 100
                        
                        stats_data[god_name.lower()] = {
                            'pick_rate': pick_rate,
                            'win_rate': win_rate,
                            'source': 'tracker_gg',
                            'last_updated': datetime.now().isoformat()
                        }
                        
                except Exception as e:
                    logger.warning(f"Failed to parse stat element: {e}")
                    continue
            
            logger.info(f"✅ Scraped stats for {len(stats_data)} gods from Tracker.gg")
            return stats_data
            
        except Exception as e:
            logger.error(f"❌ Tracker.gg parsing failed: {e}")
            return {}
    
    async def get_essential_gods_only(self) -> List[str]:
        """Get list of gods that are actually relevant for Assault"""
        # Focus on gods that are commonly picked in Assault
        essential_gods = [
            # High-impact guardians
            "Ares", "Ymir", "Sobek", "Kumbhakarna", "Geb",
            
            # Strong mages
            "Zeus", "Scylla", "Hel", "Ra", "Poseidon", "Kukulkan",
            
            # Reliable hunters
            "Neith", "Artemis", "Medusa", "Jing Wei", "Hachiman",
            
            # Effective assassins (few work in Assault)
            "Thor", "Hun Batz", "Fenrir",
            
            # Solid warriors
            "Chaac", "Hercules", "Tyr", "Sun Wukong"
        ]
        
        return essential_gods
    
    async def update_essential_data(self):
        """Update only essential god data efficiently"""
        logger.info("🔄 Updating essential god data...")
        
        # Get essential gods list
        essential_gods = await self.get_essential_gods_only()
        
        # Scrape data
        smitesource_data = await self.scrape_smitesource_gods()
        tracker_data = await self.scrape_tracker_gg_stats()
        
        # Merge and store only essential gods
        updated_count = 0
        
        with sqlite3.connect(self.db_path) as conn:
            for god_name in essential_gods:
                god_key = god_name.lower()
                
                # Combine data from sources
                god_data = {}
                
                if god_key in smitesource_data:
                    god_data.update(smitesource_data[god_key])
                
                if god_key in tracker_data:
                    god_data.update(tracker_data[god_key])
                
                # Only update if we have meaningful data
                if god_data and 'win_rate' in god_data:
                    conn.execute("""
                        INSERT OR REPLACE INTO live_gods 
                        (name, role, win_rate, pick_rate, tier, last_updated, source)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        god_data.get('name', god_name),
                        god_data.get('role', 'Unknown'),
                        god_data.get('win_rate', 0.5),
                        god_data.get('pick_rate', 0.1),
                        god_data.get('tier', 'B'),
                        datetime.now().isoformat(),
                        god_data.get('source', 'combined')
                    ))
                    updated_count += 1
        
        logger.info(f"✅ Updated {updated_count} essential gods")
        
        # Update meta info
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO meta_info (key, value, last_updated)
                VALUES (?, ?, ?)
            """, ('last_full_update', datetime.now().isoformat(), datetime.now().isoformat()))
    
    async def get_god_data(self, god_name: str) -> Optional[Dict[str, Any]]:
        """Get live data for specific god"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT name, role, win_rate, pick_rate, tier, last_updated, source
                FROM live_gods WHERE name = ? OR name = ?
            """, (god_name, god_name.title()))
            
            row = cursor.fetchone()
            if row:
                return {
                    'name': row[0],
                    'role': row[1],
                    'win_rate': row[2],
                    'pick_rate': row[3],
                    'tier': row[4],
                    'last_updated': row[5],
                    'source': row[6]
                }
        
        return None
    
    async def is_data_fresh(self, max_age_hours: int = 12) -> bool:
        """Check if data is fresh enough"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT value FROM meta_info WHERE key = 'last_full_update'")
            row = cursor.fetchone()
            
            if not row:
                return False
            
            last_update = datetime.fromisoformat(row[0])
            age = datetime.now() - last_update
            
            return age < timedelta(hours=max_age_hours)
    
    async def close(self):
        """Close session"""
        if self.session:
            await self.session.close()

async def test_live_scraper():
    """Test the live data scraper"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🌐 LIVE DATA SCRAPER TEST                                ║
║                  Efficient SMITE 2 Data Collection                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    scraper = LiveDataScraper()
    
    # Test data freshness
    print("📅 CHECKING DATA FRESHNESS")
    print("="*50)
    
    is_fresh = await scraper.is_data_fresh()
    print(f"Data is fresh: {is_fresh}")
    
    if not is_fresh:
        print("🔄 Data needs updating...")
        
        # Test essential gods list
        essential_gods = await scraper.get_essential_gods_only()
        print(f"Essential gods to track: {len(essential_gods)}")
        print(f"Examples: {essential_gods[:5]}")
        
        # Note: Actual scraping would happen here
        # For demo, we'll simulate it
        print("🌐 Would scrape SmiteSource.com and Tracker.gg...")
        print("📊 Would update database with essential data only...")
        
        # Simulate update
        with sqlite3.connect(scraper.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO meta_info (key, value, last_updated)
                VALUES (?, ?, ?)
            """, ('last_full_update', datetime.now().isoformat(), datetime.now().isoformat()))
        
        print("✅ Simulated data update complete")
    
    # Test god data retrieval
    print(f"\n🎭 TESTING GOD DATA RETRIEVAL")
    print("="*50)
    
    test_god = "Zeus"
    god_data = await scraper.get_god_data(test_god)
    
    if god_data:
        print(f"✅ Found data for {test_god}:")
        print(f"   Role: {god_data['role']}")
        print(f"   Win Rate: {god_data['win_rate']*100:.1f}%")
        print(f"   Source: {god_data['source']}")
    else:
        print(f"❌ No data found for {test_god}")
    
    await scraper.close()
    print("\n✅ Live scraper test complete!")

if __name__ == "__main__":
    asyncio.run(test_live_scraper())