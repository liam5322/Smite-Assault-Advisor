#!/usr/bin/env python3
"""
SMITE 2 Assault Brain - Headless Demo
Demonstrates core functionality without GUI components
"""

import sys
import time
import numpy as np
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from core.config_manager import ConfigManager
from core.hardware_detector import HardwareDetector
from analysis.comp_analyzer import CompAnalyzer
from analysis.build_suggester import BuildSuggester

def create_mock_screenshot():
    """Create a mock screenshot for testing"""
    # Create a 1920x1080 RGB image with some text-like patterns
    img = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
    
    # Add some "text" regions (white rectangles)
    # Team 1 region
    img[200:800, 50:450] = [240, 240, 240]  # Light gray background
    
    # Team 2 region  
    img[200:800, 1470:1870] = [240, 240, 240]  # Light gray background
    
    # Loading indicator region
    img[50:150, 860:1060] = [255, 255, 255]  # White background
    
    return img

def demo_analysis():
    """Demonstrate team analysis functionality"""
    print("\n🧠 TEAM ANALYSIS DEMO")
    print("=" * 50)
    
    # Sample teams
    team1 = ['Zeus', 'Ymir', 'Apollo', 'Aphrodite', 'Loki']
    team2 = ['Ra', 'Ares', 'Neith', 'Chang\'e', 'Thor']
    
    print(f"Team 1: {', '.join(team1)}")
    print(f"Team 2: {', '.join(team2)}")
    
    # Analyze composition
    config = ConfigManager().config
    analyzer = CompAnalyzer(config)
    analysis = analyzer.analyze_matchup(team1, team2)
    
    print(f"\n📊 Analysis Results:")
    print(f"  Win Probability: {analysis['win_probability']*100:.1f}%")
    print(f"  Team 1 Score: {analysis['team1_score']:.1f}")
    print(f"  Team 2 Score: {analysis['team2_score']:.1f}")
    
    if analysis['team1_strengths']:
        print(f"\n✅ Team 1 Strengths:")
        for strength in analysis['team1_strengths']:
            print(f"    • {strength}")
            
    if analysis['team1_weaknesses']:
        print(f"\n❌ Team 1 Weaknesses:")
        for weakness in analysis['team1_weaknesses']:
            print(f"    • {weakness}")
            
    if analysis['key_factors']:
        print(f"\n🎯 Key Factors:")
        for factor in analysis['key_factors']:
            print(f"    • {factor}")
    
    return analysis

def demo_build_suggestions():
    """Demonstrate build suggestion functionality"""
    print("\n🛡️ BUILD SUGGESTION DEMO")
    print("=" * 50)
    
    config = ConfigManager().config
    suggester = BuildSuggester(config)
    
    # Test builds for different gods against enemy team
    enemy_team = ['Aphrodite', 'Chang\'e', 'Ares', 'Kumbhakarna', 'Zeus']
    test_gods = ['Zeus', 'Apollo', 'Ymir']
    
    for god in test_gods:
        print(f"\n🔮 Build for {god} vs {', '.join(enemy_team[:3])}...")
        build = suggester.suggest_build(god, enemy_team)
        
        if build.start_items:
            print(f"  Start: {', '.join([item.name for item in build.start_items])}")
        if build.core_build:
            print(f"  Core: {', '.join([item.name for item in build.core_build])}")
        if build.relics:
            print(f"  Relics: {', '.join([item.name for item in build.relics])}")
        if build.tips:
            print(f"  Tips:")
            for tip in build.tips:
                print(f"    • {tip}")

def demo_data_systems():
    """Demonstrate data loading and management"""
    print("\n📚 DATA SYSTEMS DEMO")
    print("=" * 50)
    
    # Test data loading through analysis components
    config = ConfigManager().config
    analyzer = CompAnalyzer(config)
    suggester = BuildSuggester(config)
    
    print(f"Gods loaded in analyzer: {len(analyzer.god_data)}")
    print(f"Sample gods: {list(analyzer.god_data.keys())[:5]}")
    
    print(f"\nItems loaded in suggester: {len(suggester.item_database)}")
    print(f"Sample items: {list(suggester.item_database.keys())[:3]}")
    
    # Test god info
    if 'Zeus' in analyzer.god_data:
        zeus_info = analyzer.god_data['Zeus']
        print(f"\nZeus info: {zeus_info}")
    else:
        print(f"\nAvailable gods: {list(analyzer.god_data.keys())}")

def demo_hardware_adaptation():
    """Demonstrate hardware-adaptive configuration"""
    print("\n⚙️ HARDWARE ADAPTATION DEMO")
    print("=" * 50)
    
    detector = HardwareDetector()
    config_manager = ConfigManager()
    
    print(f"Detected Hardware:")
    for key, value in detector.system_info.items():
        print(f"  {key}: {value}")
    
    print(f"\nRecommended Tier: {detector.recommended_tier}")
    print(f"Current Config Tier: {config_manager.config['performance_tier']}")
    
    # Show tier-specific settings
    recommended_config = detector.get_recommended_config()
    print(f"\nRecommended Settings:")
    for key, value in recommended_config.items():
        if key != 'features':
            print(f"  {key}: {value}")
    
    print(f"\nEnabled Features:")
    for feature, enabled in recommended_config['features'].items():
        status = "✅" if enabled else "❌"
        print(f"  {status} {feature}")

def demo_performance_simulation():
    """Simulate performance under different loads"""
    print("\n⚡ PERFORMANCE SIMULATION")
    print("=" * 50)
    
    config = ConfigManager().config
    analyzer = CompAnalyzer(config)
    
    # Simulate multiple analyses
    teams = [
        (['Zeus', 'Ymir', 'Apollo', 'Aphrodite', 'Loki'], 
         ['Ra', 'Ares', 'Neith', 'Chang\'e', 'Thor']),
        (['Odin', 'Freya', 'Ullr', 'Hel', 'Fenrir'],
         ['Tyr', 'Sol', 'Rama', 'Sylvanus', 'Hun Batz']),
        (['Athena', 'Scylla', 'Jing Wei', 'Terra', 'Susano'],
         ['Geb', 'Thoth', 'Hou Yi', 'Khepri', 'Serqet'])
    ]
    
    print("Running analysis performance test...")
    start_time = time.time()
    
    results = []
    for i, (team1, team2) in enumerate(teams, 1):
        analysis_start = time.time()
        analysis = analyzer.analyze_matchup(team1, team2)
        analysis_time = time.time() - analysis_start
        
        results.append({
            'match': i,
            'time': analysis_time,
            'win_prob': analysis['win_probability']
        })
        
        print(f"  Match {i}: {analysis_time*1000:.1f}ms - {analysis['win_probability']*100:.1f}% win rate")
    
    total_time = time.time() - start_time
    avg_time = total_time / len(teams)
    
    print(f"\nPerformance Summary:")
    print(f"  Total time: {total_time*1000:.1f}ms")
    print(f"  Average per analysis: {avg_time*1000:.1f}ms")
    print(f"  Theoretical FPS: {1/avg_time:.1f} analyses/second")

def main():
    """Run headless demo"""
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                 SMITE 2 ASSAULT BRAIN v1.0.0                ║")
    print("║                    HEADLESS DEMO MODE                        ║")
    print("║                                                              ║")
    print("║  🎯 Testing core functionality without GUI components       ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    
    try:
        # Run all demos
        demo_hardware_adaptation()
        demo_data_systems()
        demo_analysis()
        demo_build_suggestions()
        demo_performance_simulation()
        
        print("\n" + "="*60)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("🎮 The core engine is ready for SMITE 2 Assault mode!")
        print("\n💡 Next steps:")
        print("  • Run on a system with display for full GUI testing")
        print("  • Test with actual SMITE 2 screenshots")
        print("  • Calibrate OCR regions for your resolution")
        print("  • Customize god and item databases")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)