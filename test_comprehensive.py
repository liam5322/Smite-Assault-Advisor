#!/usr/bin/env python3
"""
Comprehensive test suite for SMITE 2 Assault Brain
Tests all core functionality without requiring GUI components
"""

import sys
import time
import traceback
from pathlib import Path
import numpy as np

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

def test_imports():
    """Test that all modules can be imported"""
    print("🔍 Testing module imports...")
    
    try:
        from core.config_manager import ConfigManager
        from core.hardware_detector import HardwareDetector
        from analysis.comp_analyzer import CompAnalyzer
        from analysis.build_suggester import BuildSuggester
        from vision.ocr_engine import OCREngine
        print("✅ All core modules imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()
        return False

def test_hardware_detection():
    """Test hardware detection and tier recommendation"""
    print("\n🔧 Testing hardware detection...")
    
    try:
        from core.hardware_detector import HardwareDetector
        
        detector = HardwareDetector()
        hardware_info = detector._gather_system_info()
        tier = detector.recommended_tier
        
        print(f"  Hardware detected: {hardware_info}")
        print(f"  Recommended tier: {tier}")
        
        # Validate required fields
        required_fields = ['cpu_count', 'memory_gb', 'platform', 'gpu_available']
        for field in required_fields:
            assert field in hardware_info, f"Missing field: {field}"
            
        print("✅ Hardware detection working")
        return True
    except Exception as e:
        print(f"❌ Hardware detection failed: {e}")
        traceback.print_exc()
        return False

def test_configuration():
    """Test configuration management"""
    print("\n⚙️ Testing configuration management...")
    
    try:
        from core.config_manager import ConfigManager
        
        config_manager = ConfigManager()
        config = config_manager.config
        
        print(f"  Config loaded with {len(config)} settings")
        print(f"  Performance tier: {config.get('performance_tier', 'unknown')}")
        
        # Test tier-specific settings
        settings = config_manager.get_performance_options()
        print(f"  Tier settings: {len(settings)} tiers available")
        
        # Test feature availability
        test_features = ['advanced_analysis', 'voice_output', 'ml_predictions']
        enabled_features = [f for f in test_features if config_manager.is_feature_enabled(f)]
        print(f"  Enabled features: {enabled_features}")
        
        print("✅ Configuration management working")
        return True
    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        traceback.print_exc()
        return False

def test_data_loading():
    """Test god and item data loading"""
    print("\n📚 Testing data loading...")
    
    try:
        from core.config_manager import ConfigManager
        from analysis.comp_analyzer import CompAnalyzer
        from analysis.build_suggester import BuildSuggester
        
        config = ConfigManager().config
        analyzer = CompAnalyzer(config)
        suggester = BuildSuggester(config)
        
        print(f"  Gods loaded: {len(analyzer.god_data)}")
        print(f"  Items loaded: {len(suggester.item_database)}")
        
        # Test god data structure
        if analyzer.god_data:
            sample_god = list(analyzer.god_data.values())[0]
            print(f"  Sample god: {sample_god.name} ({sample_god.role})")
            
        # Test item data structure
        if suggester.item_database:
            sample_item = list(suggester.item_database.keys())[0]
            print(f"  Sample item: {sample_item}")
            
        print("✅ Data loading working")
        return True
    except Exception as e:
        print(f"❌ Data loading failed: {e}")
        traceback.print_exc()
        return False

def test_team_analysis():
    """Test team composition analysis"""
    print("\n🧠 Testing team analysis...")
    
    try:
        from core.config_manager import ConfigManager
        from analysis.comp_analyzer import CompAnalyzer
        
        config = ConfigManager().config
        analyzer = CompAnalyzer(config)
        
        # Test with known gods
        team1 = ['Zeus', 'Ymir', 'Apollo', 'Aphrodite', 'Loki']
        team2 = ['Ra', 'Ares', 'Neith', 'Chang\'e', 'Thor']
        
        analysis = analyzer.analyze_matchup(team1, team2)
        
        print(f"  Win probability: {analysis['win_probability']*100:.1f}%")
        print(f"  Team 1 score: {analysis['team1_score']:.1f}")
        print(f"  Team 2 score: {analysis['team2_score']:.1f}")
        print(f"  Strengths found: {len(analysis['team1_strengths'])}")
        print(f"  Key factors: {len(analysis['key_factors'])}")
        
        # Validate analysis structure
        required_keys = ['win_probability', 'team1_score', 'team2_score', 
                        'team1_strengths', 'team1_weaknesses', 'key_factors']
        for key in required_keys:
            assert key in analysis, f"Missing analysis key: {key}"
            
        print("✅ Team analysis working")
        return True
    except Exception as e:
        print(f"❌ Team analysis failed: {e}")
        traceback.print_exc()
        return False

def test_build_suggestions():
    """Test build suggestion system"""
    print("\n🛡️ Testing build suggestions...")
    
    try:
        from core.config_manager import ConfigManager
        from analysis.build_suggester import BuildSuggester
        
        config = ConfigManager().config
        suggester = BuildSuggester(config)
        
        # Test build for Zeus against healer comp
        enemy_team = ['Aphrodite', 'Chang\'e', 'Ares', 'Kumbhakarna', 'Zeus']
        build = suggester.suggest_build('Zeus', enemy_team)
        
        print(f"  God: {build.god}")
        print(f"  Role: {build.role}")
        print(f"  Start items: {len(build.start_items)}")
        print(f"  Core items: {len(build.core_build)}")
        print(f"  Relics: {len(build.relics)}")
        print(f"  Tips: {len(build.tips)}")
        
        # Check for antiheal recommendation
        has_antiheal_tip = any('antiheal' in tip.lower() or 'heal' in tip.lower() 
                              for tip in build.tips)
        print(f"  Antiheal detected: {has_antiheal_tip}")
        
        print("✅ Build suggestions working")
        return True
    except Exception as e:
        print(f"❌ Build suggestions failed: {e}")
        traceback.print_exc()
        return False

def test_ocr_engine():
    """Test OCR engine functionality"""
    print("\n👁️ Testing OCR engine...")
    
    try:
        from vision.ocr_engine import OCREngine
        from core.config_manager import ConfigManager
        
        config = ConfigManager().config
        ocr = OCREngine(config)
        
        print(f"  OCR backend: {ocr.backend}")
        print(f"  God names loaded: {len(ocr.god_names)}")
        
        # Test god name matching
        test_names = ['Zeus', 'ZEUS', 'zeus', 'Zues', 'Zeuss']
        for name in test_names:
            matched = ocr._match_god_name(name)
            print(f"  '{name}' -> '{matched}'")
            
        # Test with mock image
        mock_image = np.random.randint(0, 255, (100, 200, 3), dtype=np.uint8)
        
        # Test preprocessing
        processed = ocr._preprocess_for_ocr(mock_image)
        print(f"  Image preprocessing: {processed.shape}")
        
        print("✅ OCR engine working")
        return True
    except Exception as e:
        print(f"❌ OCR engine failed: {e}")
        traceback.print_exc()
        return False

def test_performance():
    """Test performance characteristics"""
    print("\n⚡ Testing performance...")
    
    try:
        from core.config_manager import ConfigManager
        from analysis.comp_analyzer import CompAnalyzer
        
        config = ConfigManager().config
        analyzer = CompAnalyzer(config)
        
        # Performance test
        teams = [
            (['Zeus', 'Ymir', 'Apollo', 'Aphrodite', 'Loki'], 
             ['Ra', 'Ares', 'Neith', 'Chang\'e', 'Thor']),
            (['Agni', 'Sobek', 'Rama', 'Hel', 'Fenrir'], 
             ['Scylla', 'Geb', 'Jing Wei', 'Sylvanus', 'Hun Batz']),
            (['Poseidon', 'Athena', 'Anhur', 'Baron Samedi', 'Susano'], 
             ['Thoth', 'Khepri', 'Cernunnos', 'Terra', 'Serqet'])
        ]
        
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
            
        total_time = time.time() - start_time
        avg_time = total_time / len(teams)
        
        print(f"  Total time: {total_time*1000:.1f}ms")
        print(f"  Average per analysis: {avg_time*1000:.1f}ms")
        print(f"  Theoretical FPS: {1/avg_time:.1f} analyses/second")
        
        # Performance should be reasonable
        assert avg_time < 1.0, f"Analysis too slow: {avg_time:.3f}s"
        
        print("✅ Performance acceptable")
        return True
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        traceback.print_exc()
        return False

def test_error_handling():
    """Test error handling and edge cases"""
    print("\n🛡️ Testing error handling...")
    
    try:
        from core.config_manager import ConfigManager
        from analysis.comp_analyzer import CompAnalyzer
        from analysis.build_suggester import BuildSuggester
        
        config = ConfigManager().config
        analyzer = CompAnalyzer(config)
        suggester = BuildSuggester(config)
        
        # Test with empty teams
        analysis = analyzer.analyze_matchup([], [])
        print(f"  Empty teams handled: {analysis['win_probability']}")
        
        # Test with unknown gods
        analysis = analyzer.analyze_matchup(['UnknownGod1'], ['UnknownGod2'])
        print(f"  Unknown gods handled: {analysis['win_probability']}")
        
        # Test build for unknown god
        build = suggester.suggest_build('UnknownGod', ['Zeus'])
        print(f"  Unknown god build: {build.god}")
        
        # Test with mixed known/unknown
        analysis = analyzer.analyze_matchup(['Zeus', 'UnknownGod'], ['Ra', 'FakeGod'])
        print(f"  Mixed teams handled: {analysis['win_probability']}")
        
        print("✅ Error handling working")
        return True
    except Exception as e:
        print(f"❌ Error handling failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run comprehensive test suite"""
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║              SMITE 2 ASSAULT BRAIN - TEST SUITE             ║")
    print("║                  Comprehensive Functionality Test           ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    
    tests = [
        ("Module Imports", test_imports),
        ("Hardware Detection", test_hardware_detection),
        ("Configuration", test_configuration),
        ("Data Loading", test_data_loading),
        ("Team Analysis", test_team_analysis),
        ("Build Suggestions", test_build_suggestions),
        ("OCR Engine", test_ocr_engine),
        ("Performance", test_performance),
        ("Error Handling", test_error_handling),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"📊 TEST RESULTS: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED! The system is ready for deployment.")
        print("\n💡 Next steps:")
        print("  • Test on a system with display for GUI components")
        print("  • Test with actual SMITE 2 screenshots")
        print("  • Calibrate OCR regions for different resolutions")
        print("  • Customize databases for current meta")
    else:
        print(f"⚠️ {failed} tests failed. Please review the errors above.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)