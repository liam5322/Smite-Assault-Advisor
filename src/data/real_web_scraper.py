#!/usr/bin/env python3
"""
🔍 Real Web Scraper for SMITE Data
Actual implementation for scraping SmiteSource.com and other sites
"""

import asyncio
import aiohttp
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

logger = logging.getLogger(__name__)

class RealSmiteSourceScraper:
    """Real scraper for SmiteSource.com"""
    
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.base_url = "https://smitesource.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.rate_limit_delay = 1.0  # Respectful rate limiting
    
    async def _get_page(self, url: str) -> Optional[BeautifulSoup]:
        """Get and parse a web page"""
        try:
            await asyncio.sleep(self.rate_limit_delay)  # Rate limiting
            
            async with self.session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    html = await response.text()
                    return BeautifulSoup(html, 'html.parser')
                else:
                    logger.warning(f"HTTP {response.status} for {url}")
                    return None
                    
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None
    
    async def scrape_items_list(self) -> List[Dict[str, Any]]:
        """Scrape the items list page"""
        logger.info("🔍 Scraping SmiteSource items list...")
        
        items_url = f"{self.base_url}/items"
        soup = await self._get_page(items_url)
        
        if not soup:
            logger.error("Failed to load items page")
            return []
        
        items = []
        
        try:
            # Look for item cards or links
            item_elements = soup.find_all(['div', 'a'], class_=re.compile(r'item|card'))
            
            for element in item_elements:
                item_data = await self._extract_item_data(element)
                if item_data:
                    items.append(item_data)
            
            logger.info(f"✅ Found {len(items)} items")
            return items
            
        except Exception as e:
            logger.error(f"Error parsing items page: {e}")
            return []
    
    async def _extract_item_data(self, element) -> Optional[Dict[str, Any]]:
        """Extract item data from an element"""
        try:
            # Extract item name
            name_elem = element.find(['h3', 'h4', 'span'], class_=re.compile(r'name|title'))
            if not name_elem:
                name_elem = element.find('a')
            
            if not name_elem:
                return None
            
            name = name_elem.get_text(strip=True)
            if not name:
                return None
            
            # Extract item link for detailed data
            link_elem = element.find('a')
            item_url = None
            if link_elem and link_elem.get('href'):
                item_url = urljoin(self.base_url, link_elem['href'])
            
            # Basic item data
            item_data = {
                'name': name,
                'url': item_url,
                'cost': self._extract_cost(element),
                'stats': self._extract_stats(element),
                'category': self._extract_category(element),
                'last_updated': datetime.now().isoformat()
            }
            
            # Get detailed data if we have a URL
            if item_url:
                detailed_data = await self._get_item_details(item_url)
                if detailed_data:
                    item_data.update(detailed_data)
            
            return item_data
            
        except Exception as e:
            logger.error(f"Error extracting item data: {e}")
            return None
    
    async def _get_item_details(self, item_url: str) -> Optional[Dict[str, Any]]:
        """Get detailed item information"""
        try:
            soup = await self._get_page(item_url)
            if not soup:
                return None
            
            details = {}
            
            # Extract description
            desc_elem = soup.find(['p', 'div'], class_=re.compile(r'description|passive'))
            if desc_elem:
                details['description'] = desc_elem.get_text(strip=True)
            
            # Extract build path
            build_path = []
            build_elements = soup.find_all(['div', 'span'], class_=re.compile(r'build|path|component'))
            for elem in build_elements:
                component = elem.get_text(strip=True)
                if component and component not in build_path:
                    build_path.append(component)
            
            if build_path:
                details['build_path'] = build_path
            
            # Extract tier information
            tier_elem = soup.find(['span', 'div'], class_=re.compile(r'tier|level'))
            if tier_elem:
                details['tier'] = tier_elem.get_text(strip=True)
            
            return details
            
        except Exception as e:
            logger.error(f"Error getting item details from {item_url}: {e}")
            return None
    
    def _extract_cost(self, element) -> int:
        """Extract item cost"""
        try:
            cost_elem = element.find(['span', 'div'], class_=re.compile(r'cost|price|gold'))
            if cost_elem:
                cost_text = cost_elem.get_text(strip=True)
                # Extract numbers from text
                cost_match = re.search(r'(\d+)', cost_text)
                if cost_match:
                    return int(cost_match.group(1))
            return 0
        except:
            return 0
    
    def _extract_stats(self, element) -> Dict[str, Any]:
        """Extract item stats"""
        stats = {}
        try:
            # Look for stat elements
            stat_elements = element.find_all(['span', 'div'], class_=re.compile(r'stat|power|health|mana'))
            
            for stat_elem in stat_elements:
                stat_text = stat_elem.get_text(strip=True)
                
                # Parse common stat patterns
                patterns = [
                    (r'(\d+)\s*power', 'power'),
                    (r'(\d+)\s*health', 'health'),
                    (r'(\d+)\s*mana', 'mana'),
                    (r'(\d+)%?\s*lifesteal', 'lifesteal'),
                    (r'(\d+)%?\s*crit', 'critical_chance'),
                    (r'(\d+)%?\s*attack\s*speed', 'attack_speed'),
                    (r'(\d+)\s*penetration', 'penetration'),
                ]
                
                for pattern, stat_name in patterns:
                    match = re.search(pattern, stat_text.lower())
                    if match:
                        stats[stat_name] = int(match.group(1))
            
            return stats
            
        except Exception as e:
            logger.error(f"Error extracting stats: {e}")
            return {}
    
    def _extract_category(self, element) -> str:
        """Extract item category"""
        try:
            # Look for category indicators
            category_elem = element.find(['span', 'div'], class_=re.compile(r'category|type|class'))
            if category_elem:
                return category_elem.get_text(strip=True).lower()
            
            # Fallback: check parent elements
            parent = element.parent
            if parent:
                parent_class = ' '.join(parent.get('class', []))
                if 'starter' in parent_class.lower():
                    return 'starter'
                elif 'power' in parent_class.lower():
                    return 'power'
                elif 'defense' in parent_class.lower():
                    return 'defense'
            
            return 'unknown'
            
        except:
            return 'unknown'
    
    async def scrape_gods_list(self) -> List[Dict[str, Any]]:
        """Scrape the gods list page"""
        logger.info("🔍 Scraping SmiteSource gods list...")
        
        gods_url = f"{self.base_url}/gods"
        soup = await self._get_page(gods_url)
        
        if not soup:
            logger.error("Failed to load gods page")
            return []
        
        gods = []
        
        try:
            # Look for god cards or links
            god_elements = soup.find_all(['div', 'a'], class_=re.compile(r'god|character|champion'))
            
            for element in god_elements:
                god_data = await self._extract_god_data(element)
                if god_data:
                    gods.append(god_data)
            
            logger.info(f"✅ Found {len(gods)} gods")
            return gods
            
        except Exception as e:
            logger.error(f"Error parsing gods page: {e}")
            return []
    
    async def _extract_god_data(self, element) -> Optional[Dict[str, Any]]:
        """Extract god data from an element"""
        try:
            # Extract god name
            name_elem = element.find(['h3', 'h4', 'span'], class_=re.compile(r'name|title'))
            if not name_elem:
                name_elem = element.find('a')
            
            if not name_elem:
                return None
            
            name = name_elem.get_text(strip=True)
            if not name:
                return None
            
            # Extract god link for detailed data
            link_elem = element.find('a')
            god_url = None
            if link_elem and link_elem.get('href'):
                god_url = urljoin(self.base_url, link_elem['href'])
            
            # Basic god data
            god_data = {
                'name': name,
                'url': god_url,
                'role': self._extract_role(element),
                'pantheon': self._extract_pantheon(element),
                'last_updated': datetime.now().isoformat()
            }
            
            # Get detailed data if we have a URL
            if god_url:
                detailed_data = await self._get_god_details(god_url)
                if detailed_data:
                    god_data.update(detailed_data)
            
            return god_data
            
        except Exception as e:
            logger.error(f"Error extracting god data: {e}")
            return None
    
    async def _get_god_details(self, god_url: str) -> Optional[Dict[str, Any]]:
        """Get detailed god information"""
        try:
            soup = await self._get_page(god_url)
            if not soup:
                return None
            
            details = {}
            
            # Extract win rate
            winrate_elem = soup.find(['span', 'div'], string=re.compile(r'win\s*rate', re.I))
            if winrate_elem:
                winrate_text = winrate_elem.get_text()
                winrate_match = re.search(r'(\d+(?:\.\d+)?)%?', winrate_text)
                if winrate_match:
                    details['win_rate'] = float(winrate_match.group(1)) / 100
            
            # Extract pick rate
            pickrate_elem = soup.find(['span', 'div'], string=re.compile(r'pick\s*rate', re.I))
            if pickrate_elem:
                pickrate_text = pickrate_elem.get_text()
                pickrate_match = re.search(r'(\d+(?:\.\d+)?)%?', pickrate_text)
                if pickrate_match:
                    details['pick_rate'] = float(pickrate_match.group(1)) / 100
            
            # Extract recommended builds
            build_elements = soup.find_all(['div', 'section'], class_=re.compile(r'build|item'))
            builds = []
            for build_elem in build_elements:
                build_items = []
                item_elements = build_elem.find_all(['span', 'div'], class_=re.compile(r'item'))
                for item_elem in item_elements:
                    item_name = item_elem.get_text(strip=True)
                    if item_name:
                        build_items.append(item_name)
                
                if build_items:
                    builds.append({
                        'name': 'Recommended Build',
                        'items': build_items,
                        'rating': 'A'
                    })
            
            if builds:
                details['recommended_builds'] = builds
            
            return details
            
        except Exception as e:
            logger.error(f"Error getting god details from {god_url}: {e}")
            return None
    
    def _extract_role(self, element) -> str:
        """Extract god role"""
        try:
            role_elem = element.find(['span', 'div'], class_=re.compile(r'role|class|type'))
            if role_elem:
                role = role_elem.get_text(strip=True).lower()
                # Normalize role names
                if 'mage' in role:
                    return 'Mage'
                elif 'hunter' in role or 'adc' in role:
                    return 'Hunter'
                elif 'assassin' in role:
                    return 'Assassin'
                elif 'warrior' in role:
                    return 'Warrior'
                elif 'guardian' in role or 'support' in role:
                    return 'Guardian'
            
            return 'Unknown'
            
        except:
            return 'Unknown'
    
    def _extract_pantheon(self, element) -> str:
        """Extract god pantheon"""
        try:
            pantheon_elem = element.find(['span', 'div'], class_=re.compile(r'pantheon|mythology'))
            if pantheon_elem:
                return pantheon_elem.get_text(strip=True)
            
            return 'Unknown'
            
        except:
            return 'Unknown'

class RealTrackerGGScraper:
    """Real scraper for Tracker.gg"""
    
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.base_url = "https://tracker.gg/smite"
        self.api_base = "https://api.tracker.gg/api/v2/smite"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        self.rate_limit_delay = 2.0  # More conservative for API-like endpoints
    
    async def search_player(self, player_name: str) -> Optional[Dict[str, Any]]:
        """Search for a player"""
        try:
            await asyncio.sleep(self.rate_limit_delay)
            
            search_url = f"{self.base_url}/profile/pc/{player_name}"
            
            async with self.session.get(search_url, headers=self.headers) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract player data from the page
                    player_data = await self._extract_player_data(soup)
                    return player_data
                else:
                    logger.warning(f"Player {player_name} not found (HTTP {response.status})")
                    return None
                    
        except Exception as e:
            logger.error(f"Failed to search for player {player_name}: {e}")
            return None
    
    async def _extract_player_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract player data from profile page"""
        try:
            player_data = {}
            
            # Extract rank
            rank_elem = soup.find(['span', 'div'], class_=re.compile(r'rank|tier'))
            if rank_elem:
                player_data['rank'] = rank_elem.get_text(strip=True)
            
            # Extract stats
            stat_elements = soup.find_all(['div', 'span'], class_=re.compile(r'stat|metric'))
            
            for stat_elem in stat_elements:
                stat_text = stat_elem.get_text(strip=True)
                
                # Parse common stats
                if 'win' in stat_text.lower() and '%' in stat_text:
                    winrate_match = re.search(r'(\d+(?:\.\d+)?)%', stat_text)
                    if winrate_match:
                        player_data['win_rate'] = float(winrate_match.group(1)) / 100
                
                elif 'kda' in stat_text.lower():
                    kda_match = re.search(r'(\d+(?:\.\d+)?)', stat_text)
                    if kda_match:
                        player_data['kda'] = float(kda_match.group(1))
            
            # Extract recent matches
            match_elements = soup.find_all(['div', 'tr'], class_=re.compile(r'match|game'))
            recent_matches = []
            
            for match_elem in match_elements[:5]:  # Last 5 matches
                match_data = self._extract_match_data(match_elem)
                if match_data:
                    recent_matches.append(match_data)
            
            if recent_matches:
                player_data['recent_matches'] = recent_matches
            
            return player_data
            
        except Exception as e:
            logger.error(f"Error extracting player data: {e}")
            return {}
    
    def _extract_match_data(self, match_elem) -> Optional[Dict[str, Any]]:
        """Extract match data from match element"""
        try:
            match_data = {}
            
            # Extract god played
            god_elem = match_elem.find(['span', 'div'], class_=re.compile(r'god|character|champion'))
            if god_elem:
                match_data['god'] = god_elem.get_text(strip=True)
            
            # Extract result
            result_elem = match_elem.find(['span', 'div'], class_=re.compile(r'result|outcome|win|loss'))
            if result_elem:
                result_text = result_elem.get_text(strip=True).lower()
                match_data['result'] = 'win' if 'win' in result_text else 'loss'
            
            # Extract KDA
            kda_elem = match_elem.find(['span', 'div'], class_=re.compile(r'kda|score'))
            if kda_elem:
                kda_text = kda_elem.get_text(strip=True)
                kda_match = re.search(r'(\d+)/(\d+)/(\d+)', kda_text)
                if kda_match:
                    match_data['kills'] = int(kda_match.group(1))
                    match_data['deaths'] = int(kda_match.group(2))
                    match_data['assists'] = int(kda_match.group(3))
            
            return match_data if match_data else None
            
        except Exception as e:
            logger.error(f"Error extracting match data: {e}")
            return None

async def test_real_scrapers():
    """Test the real web scrapers"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🔍 REAL WEB SCRAPER TEST                                  ║
║                  Testing SmiteSource.com & Tracker.gg                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    async with aiohttp.ClientSession() as session:
        
        # Test SmiteSource scraper
        print("🔍 Testing SmiteSource scraper...")
        smitesource = RealSmiteSourceScraper(session)
        
        try:
            # Test items scraping
            print("   📦 Scraping items...")
            items = await smitesource.scrape_items_list()
            print(f"   ✅ Found {len(items)} items")
            
            if items:
                print("   📋 Sample item:")
                sample_item = items[0]
                for key, value in sample_item.items():
                    print(f"      {key}: {value}")
            
            # Test gods scraping
            print("\n   🎭 Scraping gods...")
            gods = await smitesource.scrape_gods_list()
            print(f"   ✅ Found {len(gods)} gods")
            
            if gods:
                print("   📋 Sample god:")
                sample_god = gods[0]
                for key, value in sample_god.items():
                    print(f"      {key}: {value}")
                    
        except Exception as e:
            print(f"   ❌ SmiteSource scraping failed: {e}")
        
        # Test Tracker.gg scraper
        print(f"\n🔍 Testing Tracker.gg scraper...")
        tracker = RealTrackerGGScraper(session)
        
        try:
            # Test player search
            print("   👤 Searching for player...")
            player_data = await tracker.search_player("TestPlayer")
            
            if player_data:
                print(f"   ✅ Found player data")
                print("   📋 Player info:")
                for key, value in player_data.items():
                    if key != 'recent_matches':
                        print(f"      {key}: {value}")
                    else:
                        print(f"      recent_matches: {len(value)} matches")
            else:
                print("   ⚠️ No player data found (expected for test player)")
                
        except Exception as e:
            print(f"   ❌ Tracker.gg scraping failed: {e}")
    
    print(f"\n🚀 Real web scraper testing complete!")
    print(f"💡 Note: Actual scraping depends on website structure")
    print(f"🔧 Scrapers can be adapted as websites change")

if __name__ == "__main__":
    asyncio.run(test_real_scrapers())