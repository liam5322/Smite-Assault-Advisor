#!/usr/bin/env python3
"""
SMITE 2 Comprehensive Database Creator
Creates a lightweight SQLite database optimized for AI model access
Stores gods, abilities, items, aspects, and assault-specific data
"""

import sqlite3
import json
import os
from datetime import datetime

def create_comprehensive_database():
    """Create a comprehensive SQLite database for SMITE 2 assault data"""
    
    # Database path
    db_path = "assets/smite2_comprehensive.db"
    
    # Remove existing database
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Create connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    print("Creating comprehensive SMITE 2 database...")
    
    # ==================== METADATA TABLE ====================
    cursor.execute("""
    CREATE TABLE metadata (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Insert metadata
    metadata = [
        ("version", "Open Beta 10"),
        ("last_updated", "2025-05-28"),
        ("total_gods", "58"),
        ("total_aspects", "27"),
        ("anti_heal_cap", "75%"),
        ("starting_gold", "3000"),
        ("data_source", "Comprehensive SMITE 2 Assault Research")
    ]
    
    cursor.executemany("INSERT INTO metadata (key, value) VALUES (?, ?)", metadata)
    
    # ==================== GODS TABLE ====================
    cursor.execute("""
    CREATE TABLE gods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        pantheon TEXT NOT NULL,
        damage_type TEXT NOT NULL CHECK (damage_type IN ('Physical', 'Magical')),
        primary_role TEXT NOT NULL,
        assault_tier TEXT NOT NULL CHECK (assault_tier IN ('S+', 'S', 'A', 'B', 'C', 'D')),
        
        -- Assault scores (1-10)
        sustain_score INTEGER CHECK (sustain_score BETWEEN 1 AND 10),
        team_fight_score INTEGER CHECK (team_fight_score BETWEEN 1 AND 10),
        poke_score INTEGER CHECK (poke_score BETWEEN 1 AND 10),
        wave_clear_score INTEGER CHECK (wave_clear_score BETWEEN 1 AND 10),
        cc_score INTEGER CHECK (cc_score BETWEEN 1 AND 10),
        mobility_score INTEGER CHECK (mobility_score BETWEEN 1 AND 10),
        late_game_score INTEGER CHECK (late_game_score BETWEEN 1 AND 10),
        
        -- Text fields
        assault_roles TEXT, -- JSON array
        assault_strengths TEXT, -- JSON array
        assault_weaknesses TEXT, -- JSON array
        recommended_items TEXT, -- JSON array
        counters TEXT, -- JSON array
        synergies TEXT, -- JSON array
        assault_build_priority TEXT, -- JSON array
        
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # ==================== ASPECTS TABLE ====================
    cursor.execute("""
    CREATE TABLE aspects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        god_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        impact TEXT,
        category TEXT CHECK (category IN ('support_oriented', 'damage_oriented', 'role_changing')),
        
        FOREIGN KEY (god_id) REFERENCES gods (id) ON DELETE CASCADE
    )
    """)
    
    # ==================== ABILITIES TABLE ====================
    cursor.execute("""
    CREATE TABLE abilities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        god_id INTEGER NOT NULL,
        ability_type TEXT NOT NULL CHECK (ability_type IN ('passive', 'ability_1', 'ability_2', 'ability_3', 'ability_4')),
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        
        -- Damage and scaling
        damage_base TEXT, -- e.g., "100/155/210/265/320"
        damage_scaling TEXT, -- e.g., "+65% Intelligence"
        
        -- Crowd control
        cc_type TEXT,
        cc_duration TEXT,
        
        -- Cooldown and cost
        cooldown TEXT,
        cost TEXT,
        
        -- Range and area
        range_value TEXT,
        radius TEXT,
        cone_angle TEXT,
        
        -- Special properties
        duration TEXT,
        max_charges INTEGER,
        channel_duration TEXT,
        
        -- Additional properties as JSON
        additional_properties TEXT, -- JSON object for flexible data
        
        FOREIGN KEY (god_id) REFERENCES gods (id) ON DELETE CASCADE
    )
    """)
    
    # ==================== ITEMS TABLE ====================
    cursor.execute("""
    CREATE TABLE items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        tier INTEGER NOT NULL CHECK (tier BETWEEN 1 AND 3),
        cost INTEGER,
        category TEXT NOT NULL,
        
        -- Stats
        strength INTEGER DEFAULT 0,
        intelligence INTEGER DEFAULT 0,
        health INTEGER DEFAULT 0,
        mana INTEGER DEFAULT 0,
        physical_protection INTEGER DEFAULT 0,
        magical_protection INTEGER DEFAULT 0,
        attack_speed INTEGER DEFAULT 0,
        physical_lifesteal INTEGER DEFAULT 0,
        magical_lifesteal INTEGER DEFAULT 0,
        hp5 INTEGER DEFAULT 0,
        mp5 INTEGER DEFAULT 0,
        cooldown_reduction INTEGER DEFAULT 0,
        critical_chance INTEGER DEFAULT 0,
        penetration_flat INTEGER DEFAULT 0,
        penetration_percent INTEGER DEFAULT 0,
        
        -- Passive/Active effects
        passive_name TEXT,
        passive_description TEXT,
        active_name TEXT,
        active_description TEXT,
        active_cooldown INTEGER,
        
        -- Assault specific
        assault_priority TEXT NOT NULL,
        assault_utility TEXT NOT NULL,
        recommended_for TEXT, -- JSON array
        notes TEXT,
        
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # ==================== ITEM CATEGORIES TABLE ====================
    cursor.execute("""
    CREATE TABLE item_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT NOT NULL,
        priority TEXT NOT NULL,
        assault_notes TEXT
    )
    """)
    
    # ==================== BUILD TEMPLATES TABLE ====================
    cursor.execute("""
    CREATE TABLE build_templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT NOT NULL,
        role TEXT NOT NULL,
        priority_order TEXT NOT NULL, -- JSON array
        key_stats TEXT NOT NULL, -- JSON array
        notes TEXT,
        
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # ==================== ASSAULT MATCHUPS TABLE ====================
    cursor.execute("""
    CREATE TABLE assault_matchups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        god_id INTEGER NOT NULL,
        counter_god_id INTEGER NOT NULL,
        advantage_score INTEGER CHECK (advantage_score BETWEEN -5 AND 5), -- -5 = hard counter, +5 = hard counters
        notes TEXT,
        
        FOREIGN KEY (god_id) REFERENCES gods (id) ON DELETE CASCADE,
        FOREIGN KEY (counter_god_id) REFERENCES gods (id) ON DELETE CASCADE,
        UNIQUE(god_id, counter_god_id)
    )
    """)
    
    # ==================== TEAM COMPOSITION ANALYSIS TABLE ====================
    cursor.execute("""
    CREATE TABLE team_compositions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        composition_hash TEXT UNIQUE NOT NULL, -- Hash of sorted god names
        god_names TEXT NOT NULL, -- JSON array of god names
        
        -- Analysis scores
        overall_score INTEGER CHECK (overall_score BETWEEN 1 AND 10),
        sustain_score INTEGER CHECK (sustain_score BETWEEN 1 AND 10),
        damage_score INTEGER CHECK (damage_score BETWEEN 1 AND 10),
        cc_score INTEGER CHECK (cc_score BETWEEN 1 AND 10),
        wave_clear_score INTEGER CHECK (wave_clear_score BETWEEN 1 AND 10),
        
        -- Composition properties
        has_healer BOOLEAN DEFAULT FALSE,
        physical_damage_count INTEGER DEFAULT 0,
        magical_damage_count INTEGER DEFAULT 0,
        tank_count INTEGER DEFAULT 0,
        
        -- Recommendations
        strengths TEXT, -- JSON array
        weaknesses TEXT, -- JSON array
        recommended_strategy TEXT,
        priority_items TEXT, -- JSON array
        
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    print("Database schema created successfully!")
    
    # ==================== POPULATE GODS DATA ====================
    print("Populating gods data...")
    
    # Load comprehensive gods data
    with open("assets/gods_comprehensive.json", "r") as f:
        gods_data = json.load(f)
    
    for god_name, god_info in gods_data["gods"].items():
        # Insert god
        cursor.execute("""
        INSERT INTO gods (
            name, pantheon, damage_type, primary_role, assault_tier,
            sustain_score, team_fight_score, poke_score, wave_clear_score,
            cc_score, mobility_score, late_game_score,
            assault_roles, assault_strengths, assault_weaknesses,
            recommended_items, counters, synergies, assault_build_priority
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            god_info["name"],
            god_info["pantheon"],
            god_info["damage_type"],
            god_info["primary_role"],
            god_info["assault_tier"],
            god_info["assault_scores"]["sustain"],
            god_info["assault_scores"]["team_fight"],
            god_info["assault_scores"]["poke"],
            god_info["assault_scores"]["wave_clear"],
            god_info["assault_scores"]["cc"],
            god_info["assault_scores"]["mobility"],
            god_info["assault_scores"]["late_game"],
            json.dumps(god_info["assault_roles"]),
            json.dumps(god_info["assault_strengths"]),
            json.dumps(god_info["assault_weaknesses"]),
            json.dumps(god_info.get("recommended_items", [])),
            json.dumps(god_info.get("counters", [])),
            json.dumps(god_info.get("synergies", [])),
            json.dumps(god_info.get("assault_build_priority", []))
        ))
        
        god_id = cursor.lastrowid
        
        # Insert aspect if exists
        if "aspect" in god_info:
            aspect = god_info["aspect"]
            cursor.execute("""
            INSERT INTO aspects (god_id, name, description, impact, category)
            VALUES (?, ?, ?, ?, ?)
            """, (
                god_id,
                aspect["name"],
                aspect["description"],
                aspect.get("impact", ""),
                "role_changing"  # Default category, could be improved with better classification
            ))
        
        # Insert abilities
        if "abilities" in god_info:
            abilities = god_info["abilities"]
            for ability_type, ability_info in abilities.items():
                # Handle special ability types
                if ability_type.startswith("ability_") and "_light" in ability_type:
                    ability_type = ability_type.split("_light")[0]  # Convert ability_1_light to ability_1
                elif ability_type.startswith("ability_") and "_dark" in ability_type:
                    ability_type = ability_type.split("_dark")[0]   # Convert ability_1_dark to ability_1
                
                # Only insert if it's a valid ability type
                valid_types = ['passive', 'ability_1', 'ability_2', 'ability_3', 'ability_4']
                if ability_type in valid_types:
                    cursor.execute("""
                    INSERT INTO abilities (
                        god_id, ability_type, name, description,
                        damage_base, damage_scaling, cc_type, cc_duration,
                        cooldown, cost, range_value, radius, cone_angle,
                        duration, max_charges, channel_duration, additional_properties
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        god_id,
                        ability_type,
                        ability_info.get("name", ""),
                        ability_info.get("description", ""),
                        ability_info.get("damage", ability_info.get("damage_per_second", ability_info.get("damage_per_tick", ""))),
                        ability_info.get("damage_scaling", ""),
                        ability_info.get("cc", ""),
                        ability_info.get("cc_duration", ""),
                        ability_info.get("cooldown", ""),
                        ability_info.get("cost", ""),
                        ability_info.get("range", ""),
                        ability_info.get("radius", ""),
                        ability_info.get("cone_angle", ""),
                        ability_info.get("duration", ability_info.get("trail_duration", "")),
                        ability_info.get("max_charges", ability_info.get("max_hives", ability_info.get("max_chains", None))),
                        ability_info.get("channel_duration", ""),
                        json.dumps({k: v for k, v in ability_info.items() if k not in [
                            "name", "description", "damage", "damage_per_second", "damage_per_tick",
                            "cc", "cooldown", "cost", "range", "radius", "cone_angle", "duration"
                        ]})
                    ))
    
    # ==================== POPULATE ITEMS DATA ====================
    print("Populating items data...")
    
    # Load comprehensive items data
    with open("assets/items_comprehensive.json", "r") as f:
        items_data = json.load(f)
    
    # Insert item categories
    for category_name, category_info in items_data["item_categories"].items():
        cursor.execute("""
        INSERT INTO item_categories (name, description, priority, assault_notes)
        VALUES (?, ?, ?, ?)
        """, (
            category_name,
            category_info["description"],
            category_info["priority"],
            category_info.get("notes", "")
        ))
    
    # Insert items
    for item_name, item_info in items_data["items"].items():
        stats = item_info.get("stats", {})
        if isinstance(stats, str):
            stats = {}  # Handle case where stats is a string
        passive = item_info.get("passive", {})
        if isinstance(passive, str):
            passive = {"description": passive}  # Handle case where passive is a string
        active = item_info.get("active", {})
        if isinstance(active, str):
            active = {"description": active}  # Handle case where active is a string
        
        # Parse cost - handle string costs like "~2400g"
        cost = item_info.get("cost", 0)
        if isinstance(cost, str):
            # Extract numeric value from strings like "~2400g" or "2300g"
            import re
            cost_match = re.search(r'(\d+)', cost)
            cost = int(cost_match.group(1)) if cost_match else 0
        
        # Handle tier - relics are special case
        tier = item_info.get("tier", 3)
        if isinstance(tier, str) and tier.lower() == "relic":
            tier = 3  # Treat relics as tier 3
        elif not isinstance(tier, int) or tier < 1 or tier > 3:
            tier = 3  # Default to tier 3
        
        cursor.execute("""
        INSERT INTO items (
            name, tier, cost, category,
            strength, intelligence, health, mana,
            physical_protection, magical_protection, attack_speed,
            physical_lifesteal, magical_lifesteal, hp5, mp5,
            cooldown_reduction, critical_chance,
            passive_name, passive_description,
            active_name, active_description, active_cooldown,
            assault_priority, assault_utility, recommended_for, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item_name,
            tier,
            cost,
            "sustain",  # Default category, could be improved
            stats.get("strength", 0),
            stats.get("intelligence", 0),
            stats.get("health", 0),
            stats.get("mana", 0),
            stats.get("physical_protection", 0),
            stats.get("magical_protection", 0),
            stats.get("attack_speed", 0),
            stats.get("physical_lifesteal", 0),
            stats.get("magical_lifesteal", 0),
            stats.get("hp5", 0),
            stats.get("mp5", 0),
            stats.get("cooldown_reduction", 0),
            stats.get("critical_chance", 0),
            passive.get("name", ""),
            passive.get("description", ""),
            active.get("name", ""),
            active.get("description", ""),
            active.get("cooldown", None),
            item_info.get("assault_priority", "Medium"),
            item_info.get("assault_utility", ""),
            json.dumps(item_info.get("recommended_for", [])),
            item_info.get("notes", "")
        ))
    
    # Insert build templates
    for template_name, template_info in items_data["build_templates"].items():
        cursor.execute("""
        INSERT INTO build_templates (name, description, role, priority_order, key_stats, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            template_name,
            template_info["description"],
            template_name.split("_")[0],  # Extract role from name
            json.dumps(template_info["priority_order"]),
            json.dumps(template_info["key_stats"]),
            template_info["notes"]
        ))
    
    # ==================== CREATE INDEXES FOR PERFORMANCE ====================
    print("Creating indexes for optimal query performance...")
    
    indexes = [
        "CREATE INDEX idx_gods_name ON gods(name)",
        "CREATE INDEX idx_gods_assault_tier ON gods(assault_tier)",
        "CREATE INDEX idx_gods_damage_type ON gods(damage_type)",
        "CREATE INDEX idx_gods_primary_role ON gods(primary_role)",
        "CREATE INDEX idx_abilities_god_id ON abilities(god_id)",
        "CREATE INDEX idx_abilities_type ON abilities(ability_type)",
        "CREATE INDEX idx_aspects_god_id ON aspects(god_id)",
        "CREATE INDEX idx_items_name ON items(name)",
        "CREATE INDEX idx_items_category ON items(category)",
        "CREATE INDEX idx_items_assault_priority ON items(assault_priority)",
        "CREATE INDEX idx_matchups_god_id ON assault_matchups(god_id)",
        "CREATE INDEX idx_compositions_hash ON team_compositions(composition_hash)"
    ]
    
    for index in indexes:
        cursor.execute(index)
    
    # ==================== CREATE VIEWS FOR COMMON QUERIES ====================
    print("Creating views for common AI model queries...")
    
    # View for god summary with aspect info
    cursor.execute("""
    CREATE VIEW god_summary AS
    SELECT 
        g.name,
        g.pantheon,
        g.damage_type,
        g.primary_role,
        g.assault_tier,
        g.sustain_score,
        g.team_fight_score,
        g.poke_score,
        g.wave_clear_score,
        g.cc_score,
        g.mobility_score,
        g.late_game_score,
        g.assault_roles,
        g.assault_strengths,
        g.assault_weaknesses,
        a.name as aspect_name,
        a.description as aspect_description,
        a.impact as aspect_impact
    FROM gods g
    LEFT JOIN aspects a ON g.id = a.god_id
    """)
    
    # View for item recommendations
    cursor.execute("""
    CREATE VIEW item_recommendations AS
    SELECT 
        name,
        tier,
        cost,
        category,
        assault_priority,
        assault_utility,
        recommended_for,
        CASE 
            WHEN assault_priority = 'Highest' THEN 5
            WHEN assault_priority = 'Mandatory vs healers' THEN 4
            WHEN assault_priority = 'High' THEN 3
            WHEN assault_priority = 'Situational' THEN 2
            ELSE 1
        END as priority_score
    FROM items
    ORDER BY priority_score DESC, cost ASC
    """)
    
    # View for healer detection
    cursor.execute("""
    CREATE VIEW healers AS
    SELECT name, assault_tier, sustain_score
    FROM gods 
    WHERE assault_tier IN ('S+', 'S') 
    AND sustain_score >= 8
    AND (assault_roles LIKE '%Healer%' OR assault_strengths LIKE '%heal%')
    """)
    
    # ==================== POPULATE SAMPLE TEAM COMPOSITIONS ====================
    print("Adding sample team composition analysis...")
    
    sample_compositions = [
        {
            "gods": ["Ra", "Ares", "Zeus", "Ah Muzen Cab", "Hercules"],
            "analysis": {
                "overall_score": 9,
                "sustain_score": 9,
                "damage_score": 8,
                "cc_score": 9,
                "wave_clear_score": 8,
                "has_healer": True,
                "physical_damage_count": 2,
                "magical_damage_count": 3,
                "tank_count": 2,
                "strengths": ["Strong healer", "Excellent CC", "Good damage balance"],
                "weaknesses": ["Vulnerable to dive", "Mana dependent"],
                "recommended_strategy": "Play defensively, use Ra healing to sustain through poke",
                "priority_items": ["Divine Ruin", "Amanita Charm", "Purification Beads"]
            }
        },
        {
            "gods": ["Anubis", "Sobek", "Apollo", "Bellona", "Agni"],
            "analysis": {
                "overall_score": 6,
                "sustain_score": 4,
                "damage_score": 8,
                "cc_score": 7,
                "wave_clear_score": 7,
                "has_healer": False,
                "physical_damage_count": 2,
                "magical_damage_count": 3,
                "tank_count": 2,
                "strengths": ["High burst damage", "Good CC chain", "Strong wave clear"],
                "weaknesses": ["No healer", "Limited sustain", "Vulnerable to poke"],
                "recommended_strategy": "Aggressive early game, force fights before enemy sustain comes online",
                "priority_items": ["Lifesteal items", "Amanita Charm", "Meditation Cloak"]
            }
        }
    ]
    
    for comp in sample_compositions:
        god_names = comp["gods"]
        analysis = comp["analysis"]
        composition_hash = hash(tuple(sorted(god_names)))
        
        cursor.execute("""
        INSERT INTO team_compositions (
            composition_hash, god_names, overall_score, sustain_score,
            damage_score, cc_score, wave_clear_score, has_healer,
            physical_damage_count, magical_damage_count, tank_count,
            strengths, weaknesses, recommended_strategy, priority_items
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(composition_hash),
            json.dumps(god_names),
            analysis["overall_score"],
            analysis["sustain_score"],
            analysis["damage_score"],
            analysis["cc_score"],
            analysis["wave_clear_score"],
            analysis["has_healer"],
            analysis["physical_damage_count"],
            analysis["magical_damage_count"],
            analysis["tank_count"],
            json.dumps(analysis["strengths"]),
            json.dumps(analysis["weaknesses"]),
            analysis["recommended_strategy"],
            json.dumps(analysis["priority_items"])
        ))
    
    # ==================== FINALIZE DATABASE ====================
    conn.commit()
    
    # Get database statistics
    cursor.execute("SELECT COUNT(*) FROM gods")
    god_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM items")
    item_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM abilities")
    ability_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM aspects")
    aspect_count = cursor.fetchone()[0]
    
    print(f"\n✅ Database created successfully!")
    print(f"📊 Statistics:")
    print(f"   - Gods: {god_count}")
    print(f"   - Items: {item_count}")
    print(f"   - Abilities: {ability_count}")
    print(f"   - Aspects: {aspect_count}")
    print(f"   - Database size: {os.path.getsize(db_path) / 1024:.1f} KB")
    print(f"   - Location: {db_path}")
    
    conn.close()
    return db_path

def test_database_queries():
    """Test some common queries that an AI model might use"""
    print("\n🧪 Testing database with sample AI queries...")
    
    conn = sqlite3.connect("assets/smite2_comprehensive.db")
    cursor = conn.cursor()
    
    # Test 1: Get all S-tier gods
    print("\n1. S-tier gods for assault:")
    cursor.execute("SELECT name, assault_tier, sustain_score FROM gods WHERE assault_tier = 'S' ORDER BY sustain_score DESC")
    for row in cursor.fetchall():
        print(f"   - {row[0]} (Tier {row[1]}, Sustain: {row[2]})")
    
    # Test 2: Get high priority items
    print("\n2. Highest priority assault items:")
    cursor.execute("SELECT name, assault_priority, cost FROM items WHERE assault_priority = 'Highest' ORDER BY cost")
    for row in cursor.fetchall():
        print(f"   - {row[0]} ({row[1]}, {row[2]}g)")
    
    # Test 3: Get healers
    print("\n3. Available healers:")
    cursor.execute("SELECT name, sustain_score FROM healers ORDER BY sustain_score DESC")
    for row in cursor.fetchall():
        print(f"   - {row[0]} (Sustain: {row[1]})")
    
    # Test 4: Get anti-heal items
    print("\n4. Anti-heal items:")
    cursor.execute("SELECT name, passive_description FROM items WHERE passive_description LIKE '%heal%' AND passive_description LIKE '%reduc%'")
    for row in cursor.fetchall():
        print(f"   - {row[0]}")
    
    # Test 5: Get god abilities
    print("\n5. Sample god abilities (Ra):")
    cursor.execute("""
    SELECT ability_type, name, description 
    FROM abilities 
    WHERE god_id = (SELECT id FROM gods WHERE name = 'Ra')
    ORDER BY ability_type
    """)
    for row in cursor.fetchall():
        print(f"   - {row[0]}: {row[1]}")
    
    conn.close()
    print("\n✅ Database queries working correctly!")

if __name__ == "__main__":
    # Create the comprehensive database
    db_path = create_comprehensive_database()
    
    # Test the database
    test_database_queries()
    
    print(f"\n🎯 Database ready for AI model integration!")
    print(f"   Use: sqlite3.connect('{db_path}') to access the data")
    print(f"   Optimized for small AI models like Qwen 0.6B or TinyLlama 1.1B")