#!/usr/bin/env python3
"""
SMITE 2 Assault Advisor Web Application
Showcases the comprehensive database and AI integration
"""

import os
import sys
import sqlite3
import json
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.ai.lightweight_advisor import LightweightAssaultAdvisor
    from src.ai.small_model_integration import create_assault_advisor
except ImportError:
    # Fallback imports
    sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'ai'))
    from lightweight_advisor import LightweightAssaultAdvisor
    from small_model_integration import create_assault_advisor

app = Flask(__name__)
CORS(app)

# Initialize advisors
db_path = os.path.join(os.path.dirname(__file__), "assets/smite2_comprehensive.db")
data_advisor = LightweightAssaultAdvisor(db_path)

# Create AI advisor with correct database path
class ModelConfig:
    def __init__(self):
        self.model_name = "rule-based"
        self.max_tokens = 128
        self.temperature = 0.3
        self.backend = "none"
        self.context_limit = 2048

try:
    from src.ai.small_model_integration import SmallModelAssaultAdvisor
    ai_advisor = SmallModelAssaultAdvisor(ModelConfig(), db_path)
except:
    ai_advisor = None

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/gods')
def get_gods():
    """Get all gods with their basic info"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT name, pantheon, damage_type, primary_role, assault_tier,
           sustain_score, team_fight_score, assault_roles, assault_strengths
    FROM gods
    ORDER BY assault_tier, name
    """)
    
    gods = []
    for row in cursor.fetchall():
        gods.append({
            'name': row['name'],
            'pantheon': row['pantheon'],
            'damage_type': row['damage_type'],
            'role': row['primary_role'],
            'tier': row['assault_tier'],
            'sustain': row['sustain_score'],
            'team_fight': row['team_fight_score'],
            'assault_roles': json.loads(row['assault_roles']) if row['assault_roles'] else [],
            'strengths': json.loads(row['assault_strengths']) if row['assault_strengths'] else []
        })
    
    conn.close()
    return jsonify(gods)

@app.route('/api/items')
def get_items():
    """Get all items with their info"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT name, tier, cost, assault_priority, assault_utility,
           strength, intelligence, health, physical_protection, magical_protection,
           passive_name, passive_description
    FROM items
    ORDER BY 
        CASE assault_priority
            WHEN 'Highest' THEN 1
            WHEN 'Mandatory vs healers' THEN 2
            WHEN 'High' THEN 3
            ELSE 4
        END, cost
    """)
    
    items = []
    for row in cursor.fetchall():
        items.append({
            'name': row['name'],
            'tier': row['tier'],
            'cost': row['cost'],
            'priority': row['assault_priority'],
            'utility': row['assault_utility'],
            'stats': {
                'strength': row['strength'],
                'intelligence': row['intelligence'],
                'health': row['health'],
                'physical_protection': row['physical_protection'],
                'magical_protection': row['magical_protection']
            },
            'passive': {
                'name': row['passive_name'],
                'description': row['passive_description']
            }
        })
    
    conn.close()
    return jsonify(items)

@app.route('/api/analyze', methods=['POST'])
def analyze_team():
    """Analyze a team composition"""
    data = request.get_json()
    team_gods = data.get('team_gods', [])
    enemy_gods = data.get('enemy_gods', [])
    
    if len(team_gods) != 5:
        return jsonify({'error': 'Team must have exactly 5 gods'}), 400
    
    try:
        # Get structured analysis
        analysis = data_advisor.analyze_team_composition(team_gods)
        quick_recs = data_advisor.get_quick_recommendations(team_gods)
        
        # Get AI advice if available
        ai_advice = ""
        try:
            ai_advice = ai_advisor.get_natural_language_advice(team_gods, enemy_gods)
        except Exception as e:
            ai_advice = f"AI advice unavailable: {str(e)}"
        
        result = {
            'analysis': {
                'overall_score': analysis.overall_score,
                'win_probability': f"{analysis.win_probability:.1%}",
                'sustain_score': analysis.sustain_score,
                'damage_score': analysis.damage_score,
                'cc_score': analysis.cc_score,
                'wave_clear_score': analysis.wave_clear_score,
                'has_healer': analysis.has_healer,
                'damage_split': f"{analysis.physical_damage_count}P/{analysis.magical_damage_count}M",
                'tank_count': analysis.tank_count
            },
            'recommendations': {
                'strategy': analysis.recommended_strategy,
                'priority_items': analysis.priority_items[:5],
                'strengths': analysis.strengths[:3],
                'weaknesses': analysis.weaknesses[:3]
            },
            'quick_summary': quick_recs,
            'ai_advice': ai_advice
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/god/<god_name>')
def get_god_details(god_name):
    """Get detailed information about a specific god"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get god info
    cursor.execute("SELECT * FROM gods WHERE name = ?", (god_name,))
    god = cursor.fetchone()
    
    if not god:
        return jsonify({'error': 'God not found'}), 404
    
    # Get abilities
    cursor.execute("""
    SELECT ability_type, name, description, damage_base, damage_scaling,
           cc_type, cc_duration, cooldown, cost, range_value, radius
    FROM abilities
    WHERE god_id = ?
    ORDER BY ability_type
    """, (god['id'],))
    
    abilities = []
    for ability in cursor.fetchall():
        abilities.append({
            'type': ability['ability_type'],
            'name': ability['name'],
            'description': ability['description'],
            'damage': ability['damage_base'],
            'scaling': ability['damage_scaling'],
            'cc': ability['cc_type'],
            'cc_duration': ability['cc_duration'],
            'cooldown': ability['cooldown'],
            'cost': ability['cost'],
            'range': ability['range_value'],
            'radius': ability['radius']
        })
    
    # Get aspect
    cursor.execute("SELECT * FROM aspects WHERE god_id = ?", (god['id'],))
    aspect = cursor.fetchone()
    
    result = {
        'name': god['name'],
        'pantheon': god['pantheon'],
        'damage_type': god['damage_type'],
        'role': god['primary_role'],
        'tier': god['assault_tier'],
        'scores': {
            'sustain': god['sustain_score'],
            'team_fight': god['team_fight_score'],
            'poke': god['poke_score'],
            'wave_clear': god['wave_clear_score'],
            'cc': god['cc_score'],
            'mobility': god['mobility_score'],
            'late_game': god['late_game_score']
        },
        'assault_info': {
            'roles': json.loads(god['assault_roles']) if god['assault_roles'] else [],
            'strengths': json.loads(god['assault_strengths']) if god['assault_strengths'] else [],
            'weaknesses': json.loads(god['assault_weaknesses']) if god['assault_weaknesses'] else [],
            'recommended_items': json.loads(god['recommended_items']) if god['recommended_items'] else []
        },
        'abilities': abilities,
        'aspect': {
            'name': aspect['name'],
            'description': aspect['description'],
            'impact': aspect['impact']
        } if aspect else None
    }
    
    conn.close()
    return jsonify(result)

@app.route('/api/build/<god_name>', methods=['POST'])
def get_god_build(god_name):
    """Get build recommendation for a specific god"""
    data = request.get_json()
    team_gods = data.get('team_gods', [])
    enemy_gods = data.get('enemy_gods', [])
    
    try:
        # Get AI advice for the god
        ai_advice = ai_advisor.get_god_specific_advice(god_name, team_gods)
        
        # Get structured build recommendation
        build_rec = data_advisor.get_god_build_recommendation(god_name, team_gods, enemy_gods)
        
        result = {
            'god_name': god_name,
            'build_order': build_rec.build_order,
            'priority_items': build_rec.priority_items,
            'situational_items': build_rec.situational_items,
            'playstyle_notes': build_rec.playstyle_notes,
            'aspect_recommendation': build_rec.aspect_recommendation,
            'ai_advice': ai_advice
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/database/stats')
def get_database_stats():
    """Get database statistics"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    stats = {}
    
    # Count tables
    tables = ['gods', 'items', 'abilities', 'aspects', 'team_compositions']
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        stats[table] = cursor.fetchone()[0]
    
    # Get metadata
    cursor.execute("SELECT key, value FROM metadata")
    metadata = dict(cursor.fetchall())
    
    # Database size
    db_size = os.path.getsize("assets/smite2_comprehensive.db")
    
    result = {
        'counts': stats,
        'metadata': metadata,
        'database_size_kb': round(db_size / 1024, 1),
        'total_records': sum(stats.values())
    }
    
    conn.close()
    return jsonify(result)

# Create templates directory and basic HTML
@app.before_first_request
def create_templates():
    """Create templates directory and basic HTML if they don't exist"""
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    # Create basic index.html if it doesn't exist
    index_path = os.path.join(templates_dir, 'index.html')
    if not os.path.exists(index_path):
        with open(index_path, 'w') as f:
            f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SMITE 2 Assault Advisor</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: #fff; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .section { background: #2a2a2a; padding: 20px; margin: 20px 0; border-radius: 8px; }
        .god-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; }
        .god-card { background: #3a3a3a; padding: 15px; border-radius: 5px; border-left: 4px solid #FFD700; }
        .tier-S { border-left-color: #ff6b6b; }
        .tier-A { border-left-color: #4ecdc4; }
        .tier-B { border-left-color: #45b7d1; }
        .tier-C { border-left-color: #96ceb4; }
        .tier-D { border-left-color: #feca57; }
        .stats { display: flex; gap: 20px; margin: 10px 0; }
        .stat { text-align: center; }
        .stat-value { font-size: 1.2em; font-weight: bold; color: #FFD700; }
        .team-builder { display: flex; gap: 20px; margin: 20px 0; }
        .team-slot { background: #3a3a3a; padding: 10px; border-radius: 5px; min-height: 40px; }
        button { background: #FFD700; color: #000; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
        button:hover { background: #e6c200; }
        .analysis-result { background: #2a4a2a; padding: 20px; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎮 SMITE 2 Assault Advisor</h1>
            <p>Comprehensive database with AI-powered recommendations</p>
        </div>
        
        <div class="section">
            <h2>📊 Database Statistics</h2>
            <div id="stats" class="stats">
                <div class="stat">
                    <div class="stat-value" id="god-count">-</div>
                    <div>Gods</div>
                </div>
                <div class="stat">
                    <div class="stat-value" id="item-count">-</div>
                    <div>Items</div>
                </div>
                <div class="stat">
                    <div class="stat-value" id="ability-count">-</div>
                    <div>Abilities</div>
                </div>
                <div class="stat">
                    <div class="stat-value" id="aspect-count">-</div>
                    <div>Aspects</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>⚔️ Team Composition Analyzer</h2>
            <p>Select 5 gods to analyze team composition:</p>
            <div class="team-builder">
                <div>
                    <h3>Your Team</h3>
                    <div id="team-slots">
                        <div class="team-slot" data-slot="0">Slot 1</div>
                        <div class="team-slot" data-slot="1">Slot 2</div>
                        <div class="team-slot" data-slot="2">Slot 3</div>
                        <div class="team-slot" data-slot="3">Slot 4</div>
                        <div class="team-slot" data-slot="4">Slot 5</div>
                    </div>
                    <button onclick="analyzeTeam()">Analyze Team</button>
                </div>
            </div>
            <div id="analysis-result" class="analysis-result" style="display: none;"></div>
        </div>
        
        <div class="section">
            <h2>🏛️ God Database</h2>
            <div id="gods-grid" class="god-grid">
                Loading gods...
            </div>
        </div>
    </div>
    
    <script>
        let selectedTeam = [null, null, null, null, null];
        let allGods = [];
        
        // Load initial data
        async function loadData() {
            try {
                // Load stats
                const statsResponse = await fetch('/api/database/stats');
                const stats = await statsResponse.json();
                
                document.getElementById('god-count').textContent = stats.counts.gods;
                document.getElementById('item-count').textContent = stats.counts.items;
                document.getElementById('ability-count').textContent = stats.counts.abilities;
                document.getElementById('aspect-count').textContent = stats.counts.aspects;
                
                // Load gods
                const godsResponse = await fetch('/api/gods');
                allGods = await godsResponse.json();
                displayGods(allGods);
                
            } catch (error) {
                console.error('Error loading data:', error);
            }
        }
        
        function displayGods(gods) {
            const grid = document.getElementById('gods-grid');
            grid.innerHTML = gods.map(god => `
                <div class="god-card tier-${god.tier}" onclick="selectGod('${god.name}')">
                    <h3>${god.name}</h3>
                    <p><strong>${god.pantheon}</strong> | ${god.damage_type}</p>
                    <p>Tier: <strong>${god.tier}</strong> | Role: ${god.role}</p>
                    <div class="stats">
                        <div class="stat">
                            <div class="stat-value">${god.sustain}</div>
                            <div>Sustain</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value">${god.team_fight}</div>
                            <div>Team Fight</div>
                        </div>
                    </div>
                    <p><small>${god.strengths.slice(0, 2).join(', ')}</small></p>
                </div>
            `).join('');
        }
        
        function selectGod(godName) {
            // Find first empty slot
            const emptySlot = selectedTeam.findIndex(slot => slot === null);
            if (emptySlot !== -1) {
                selectedTeam[emptySlot] = godName;
                updateTeamDisplay();
            }
        }
        
        function updateTeamDisplay() {
            const slots = document.querySelectorAll('.team-slot');
            slots.forEach((slot, index) => {
                if (selectedTeam[index]) {
                    slot.textContent = selectedTeam[index];
                    slot.style.background = '#4a4a4a';
                    slot.onclick = () => {
                        selectedTeam[index] = null;
                        updateTeamDisplay();
                    };
                } else {
                    slot.textContent = `Slot ${index + 1}`;
                    slot.style.background = '#3a3a3a';
                    slot.onclick = null;
                }
            });
        }
        
        async function analyzeTeam() {
            const team = selectedTeam.filter(god => god !== null);
            if (team.length !== 5) {
                alert('Please select exactly 5 gods');
                return;
            }
            
            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ team_gods: team })
                });
                
                const result = await response.json();
                displayAnalysis(result);
                
            } catch (error) {
                console.error('Error analyzing team:', error);
            }
        }
        
        function displayAnalysis(result) {
            const analysisDiv = document.getElementById('analysis-result');
            analysisDiv.style.display = 'block';
            analysisDiv.innerHTML = `
                <h3>📊 Team Analysis Results</h3>
                <div class="stats">
                    <div class="stat">
                        <div class="stat-value">${result.analysis.overall_score}/10</div>
                        <div>Overall Score</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">${result.analysis.win_probability}</div>
                        <div>Win Probability</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">${result.analysis.has_healer ? 'Yes' : 'No'}</div>
                        <div>Has Healer</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">${result.analysis.damage_split}</div>
                        <div>Damage Split</div>
                    </div>
                </div>
                
                <h4>🎯 Strategy</h4>
                <p>${result.recommendations.strategy}</p>
                
                <h4>🛡️ Priority Items</h4>
                <p>${result.recommendations.priority_items.join(', ')}</p>
                
                <h4>💪 Strengths</h4>
                <ul>${result.recommendations.strengths.map(s => `<li>${s}</li>`).join('')}</ul>
                
                <h4>⚠️ Weaknesses</h4>
                <ul>${result.recommendations.weaknesses.map(w => `<li>${w}</li>`).join('')}</ul>
                
                <h4>🤖 AI Advice</h4>
                <p><em>${result.ai_advice}</em></p>
            `;
        }
        
        // Load data on page load
        loadData();
    </script>
</body>
</html>""")

if __name__ == '__main__':
    print("🌐 Starting SMITE 2 Assault Advisor Web App...")
    print("📊 Database loaded with comprehensive game data")
    print("🤖 AI advisor initialized")
    print("🔗 Access the app at: http://localhost:12000")
    
    app.run(host='0.0.0.0', port=12000, debug=True)