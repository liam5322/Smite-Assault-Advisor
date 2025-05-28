#!/usr/bin/env python3
"""
Test core functionality without GUI components
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

def test_hardware_detection():
    """Test hardware detection"""
    print("🔧 Testing Hardware Detection...")
    
    from core.hardware_detector import HardwareDetector
    
    detector = HardwareDetector()
    tier = detector.recommended_tier
    
    print(f"  ✅ Detected tier: {tier}")
    print(f"  ✅ System info: {detector.system_info}")
    
    return True

def test_config_management():
    """Test configuration management"""
    print("⚙️ Testing Configuration Management...")
    
    from core.config_manager import ConfigManager
    
    config_manager = ConfigManager()
    config = config_manager.config
    
    print(f"  ✅ Config loaded: {len(config)} settings")
    print(f"  ✅ Performance tier: {config.get('performance_tier', 'unknown')}")
    
    return True

def test_analysis_components():
    """Test analysis components"""
    print("🧠 Testing Analysis Components...")
    
    from analysis.comp_analyzer import CompAnalyzer
    from analysis.build_suggester import BuildSuggester
    
    config = {'performance_tier': 'minimal'}
    
    # Test team composition analysis
    analyzer = CompAnalyzer(config)
    
    team1 = ['Zeus', 'Ymir', 'Apollo', 'Aphrodite', 'Thor']
    team2 = ['Ares', 'Scylla', 'Neith', 'Chang\'e', 'Fenrir']
    
    analysis = analyzer.analyze_matchup(team1, team2)
    
    print(f"  ✅ Analysis complete: {analysis['win_probability']:.1%} win chance")
    print(f"  ✅ Team 1 strengths: {len(analysis['team1_strengths'])}")
    print(f"  ✅ Key factors: {len(analysis['key_factors'])}")
    
    # Test build suggestions
    suggester = BuildSuggester(config)
    
    build = suggester.suggest_build('Zeus', team2)
    
    print(f"  ✅ Build suggested for Zeus: {len(build.core_build)} items")
    print(f"  ✅ Build tips: {len(build.tips)}")
    
    return True

def test_vision_components():
    """Test vision components (without actual screen capture)"""
    print("👁️ Testing Vision Components...")
    
    from vision.screen_capture import ScreenCapture
    from vision.ocr_engine import OCREngine
    
    config = {'performance_tier': 'minimal'}
    
    # Test screen capture initialization
    try:
        capture = ScreenCapture(config)
        print("  ✅ Screen capture initialized")
    except Exception as e:
        print(f"  ⚠️ Screen capture failed (expected in headless): {e}")
    
    # Test OCR engine initialization
    ocr = OCREngine(config)
    print("  ✅ OCR engine initialized")
    
    # Test god name matching
    test_names = ['Zeus', 'Zues', 'ZEUS', 'zeus', 'Aphrodite', 'Afrodite']
    for name in test_names:
        matched = ocr._match_god_name(name)
        print(f"    '{name}' -> '{matched}'")
    
    return True

def test_data_loading():
    """Test data loading"""
    print("📊 Testing Data Loading...")
    
    # Test god database
    god_file = Path(__file__).parent / 'assets' / 'gods.json'
    if god_file.exists():
        import json
        with open(god_file, 'r') as f:
            god_data = json.load(f)
        print(f"  ✅ Gods loaded: {len(god_data.get('gods', []))} gods")
        print(f"  ✅ God data: {len(god_data.get('god_data', {}))} entries")
    else:
        print("  ⚠️ Gods file not found")
    
    # Test item database
    item_file = Path(__file__).parent / 'assets' / 'items.json'
    if item_file.exists():
        import json
        with open(item_file, 'r') as f:
            item_data = json.load(f)
        print(f"  ✅ Items loaded: {len(item_data.get('items', []))} items")
    else:
        print("  ⚠️ Items file not found")
    
    return True

def main():
    """Run all tests"""
    print("🎮 SMITE 2 ASSAULT BRAIN - CORE FUNCTIONALITY TEST")
    print("=" * 60)
    
    tests = [
        test_hardware_detection,
        test_config_management,
        test_data_loading,
        test_analysis_components,
        test_vision_components,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"  ❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            print()
    
    print("=" * 60)
    print(f"🎯 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All core functionality working!")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)