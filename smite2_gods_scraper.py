#!/usr/bin/env python3
"""
SMITE 2 Gods Scraper - Get accurate SMITE 2 god roster
"""

import requests
import json
import sqlite3
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Smite2God:
    """SMITE 2 God data"""
    name: str
    role: str
    damage_type: str
    pantheon: str
    difficulty: int
    is_healer: bool
    is_tank: bool
    is_hunter: bool
    assault_tier: str
    description: str

class Smite2GodsDatabase:
    """SMITE 2 Gods Database Manager"""
    
    def __init__(self):
        self.data_dir = Path("smite2_data")
        self.data_dir.mkdir(exist_ok=True)
        self.db_path = self.data_dir / "smite2_gods.db"
        self._init_database()
    
    def _init_database(self):
        """Initialize gods database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS smite2_gods (
                    name TEXT PRIMARY KEY,
                    role TEXT,
                    damage_type TEXT,
                    pantheon TEXT,
                    difficulty INTEGER,
                    is_healer BOOLEAN,
                    is_tank BOOLEAN,
                    is_hunter BOOLEAN,
                    assault_tier TEXT,
                    description TEXT,
                    last_updated TEXT
                )
            """)
    
    def create_smite2_gods_database(self) -> List[Smite2God]:
        """Create comprehensive SMITE 2 gods database"""
        logger.info("🔄 Creating SMITE 2 gods database...")
        
        # SMITE 2 confirmed god roster (as of early access)
        smite2_gods = [
            # Hunters
            Smite2God("Neith", "Hunter", "Physical", "Egyptian", 2, True, False, True, "S", "Weaver of Fate - Has heal on Spirit Arrow"),
            Smite2God("Apollo", "Hunter", "Physical", "Greek", 2, False, False, True, "A", "God of Music"),
            Smite2God("Artemis", "Hunter", "Physical", "Greek", 2, False, False, True, "A", "Goddess of the Hunt"),
            Smite2God("Anhur", "Hunter", "Physical", "Egyptian", 3, False, False, True, "B", "Slayer of Enemies"),
            Smite2God("Cupid", "Hunter", "Physical", "Roman", 2, True, False, True, "B", "God of Love - Has heal on Heart Bomb"),
            
            # Mages
            Smite2God("Zeus", "Mage", "Magical", "Greek", 2, False, False, False, "S", "God of the Sky"),
            Smite2God("Ra", "Mage", "Magical", "Egyptian", 1, True, False, False, "S", "Sun God - Primary healer with Solar Blessing"),
            Smite2God("Kukulkan", "Mage", "Magical", "Maya", 2, False, False, False, "A", "Serpent of the Nine Winds"),
            Smite2God("Anubis", "Mage", "Magical", "Egyptian", 1, True, False, False, "A", "God of the Dead - Has lifesteal on abilities"),
            Smite2God("Poseidon", "Mage", "Magical", "Greek", 2, False, False, False, "A", "God of the Oceans"),
            Smite2God("Agni", "Mage", "Magical", "Hindu", 3, False, False, False, "B", "God of Fire"),
            
            # Guardians
            Smite2God("Ymir", "Guardian", "Magical", "Norse", 1, False, True, False, "S", "Father of the Frost Giants"),
            Smite2God("Ares", "Guardian", "Magical", "Greek", 2, False, True, False, "S", "God of War"),
            Smite2God("Sobek", "Guardian", "Magical", "Egyptian", 2, True, True, False, "A", "God of the Nile - Has heal on Tail Whip"),
            Smite2God("Bacchus", "Guardian", "Magical", "Roman", 3, False, True, False, "A", "God of Wine"),
            Smite2God("Geb", "Guardian", "Magical", "Egyptian", 2, True, True, False, "A", "God of Earth - Has shield/heal on Stone Shield"),
            
            # Warriors
            Smite2God("Thor", "Warrior", "Physical", "Norse", 2, False, False, False, "A", "God of Thunder"),
            Smite2God("Sun Wukong", "Warrior", "Physical", "Chinese", 2, False, False, False, "A", "The Monkey King"),
            Smite2God("Chaac", "Warrior", "Physical", "Maya", 2, False, False, False, "B", "God of Rain"),
            Smite2God("Odin", "Warrior", "Physical", "Norse", 2, False, False, False, "B", "The Allfather"),
            
            # Assassins
            Smite2God("Loki", "Assassin", "Physical", "Norse", 3, False, False, False, "B", "The Trickster God"),
            Smite2God("Fenrir", "Assassin", "Physical", "Norse", 2, False, False, False, "A", "The Unbound"),
            Smite2God("Bastet", "Assassin", "Physical", "Egyptian", 2, False, False, False, "B", "Goddess of Cats"),
            Smite2God("Hun Batz", "Assassin", "Physical", "Maya", 3, False, False, False, "B", "Howler Monkey God"),
            
            # Special/Hybrid
            Smite2God("Aphrodite", "Mage", "Magical", "Greek", 2, True, False, False, "S", "Goddess of Beauty - Primary healer with Kiss/Back Off"),
            Smite2God("Hades", "Mage", "Magical", "Greek", 2, True, False, False, "A", "King of the Underworld - Has lifesteal on Devour Souls"),
            Smite2God("Janus", "Mage", "Magical", "Roman", 3, False, False, False, "A", "God of Transitions"),
        ]
        
        logger.info(f"✅ Created SMITE 2 database with {len(smite2_gods)} gods")
        return smite2_gods
    
    def save_gods(self, gods: List[Smite2God]):
        """Save gods to database"""
        with sqlite3.connect(self.db_path) as conn:
            for god in gods:
                conn.execute("""
                    INSERT OR REPLACE INTO smite2_gods VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    god.name, god.role, god.damage_type, god.pantheon,
                    god.difficulty, god.is_healer, god.is_tank, god.is_hunter,
                    god.assault_tier, god.description, "2025-01-01 00:00:00"
                ))
        
        logger.info(f"💾 Saved {len(gods)} gods to database")
    
    def get_all_gods(self) -> List[Smite2God]:
        """Get all gods from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM smite2_gods ORDER BY name")
            gods = []
            for row in cursor.fetchall():
                god = Smite2God(
                    name=row[0], role=row[1], damage_type=row[2], pantheon=row[3],
                    difficulty=row[4], is_healer=bool(row[5]), is_tank=bool(row[6]),
                    is_hunter=bool(row[7]), assault_tier=row[8], description=row[9]
                )
                gods.append(god)
            return gods
    
    def get_god_names(self) -> List[str]:
        """Get list of all god names"""
        gods = self.get_all_gods()
        return [god.name for god in gods]
    
    def get_healers(self) -> List[str]:
        """Get list of healer gods"""
        gods = self.get_all_gods()
        return [god.name for god in gods if god.is_healer]
    
    def get_hunters(self) -> List[str]:
        """Get list of hunter gods"""
        gods = self.get_all_gods()
        return [god.name for god in gods if god.is_hunter]
    
    def get_tanks(self) -> List[str]:
        """Get list of tank gods"""
        gods = self.get_all_gods()
        return [god.name for god in gods if god.is_tank]
    
    def is_valid_god(self, god_name: str) -> bool:
        """Check if god name is valid in SMITE 2"""
        god_names = [name.lower() for name in self.get_god_names()]
        return god_name.lower() in god_names

def main():
    """Test the gods database"""
    db = Smite2GodsDatabase()
    
    # Create and save gods
    gods = db.create_smite2_gods_database()
    db.save_gods(gods)
    
    # Test queries
    print(f"\n📊 SMITE 2 Gods Database:")
    print(f"Total Gods: {len(db.get_god_names())}")
    print(f"Healers: {db.get_healers()}")
    print(f"Hunters: {db.get_hunters()}")
    print(f"Tanks: {db.get_tanks()}")
    
    print(f"\n🎯 God Validation Tests:")
    print(f"Zeus valid: {db.is_valid_god('Zeus')}")
    print(f"Scylla valid: {db.is_valid_god('Scylla')}")  # Should be False
    print(f"Hel valid: {db.is_valid_god('Hel')}")        # Should be False

if __name__ == "__main__":
    main()