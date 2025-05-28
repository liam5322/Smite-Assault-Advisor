#!/usr/bin/env python3
"""
SMITE 2 Assault Brain - Hardware Optimization Demo
Demonstrates dynamic performance adaptation across different hardware tiers
"""

import sys
import time
import json
from pathlib import Path
from typing import Dict, Any

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from core.hardware_detector import HardwareDetector, PerformanceTier
from core.config_manager import ConfigManager
from analysis.comp_analyzer import CompAnalyzer
from analysis.build_suggester import BuildSuggester
from vision.ocr_engine import OCREngine

def print_header():
    """Print demo header"""
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║           SMITE 2 ASSAULT BRAIN - OPTIMIZATION DEMO         ║")
    print("║                                                              ║")
    print("║  🚀 Dynamic Hardware Adaptation & Performance Scaling       ║")
    print("║  ⚡ From Minimal to Maximum Performance Tiers               ║")
    print("╚══════════════════════════════════════════════════════════════╝")

def demo_hardware_tiers():
    """Demonstrate all performance tiers"""
    print("\n🔧 HARDWARE TIER DEMONSTRATION")
    print("="*60)
    
    detector = HardwareDetector()
    current_hardware = detector._gather_system_info()
    
    print(f"Current System:")
    print(f"  CPU Cores: {current_hardware['cpu_count']}")
    print(f"  Memory: {current_hardware['memory_gb']:.1f} GB")
    print(f"  GPU Available: {current_hardware['gpu_available']}")
    print(f"  Platform: {current_hardware['platform']}")
    
    print(f"\nRecommended Tier: {detector.recommended_tier.value}")
    
    # Show all tier configurations
    tier_configs = detector.get_tier_options()
    
    for tier_name, config in tier_configs.items():
        print(f"\n📊 {tier_name.upper()} TIER:")
        print(f"  Description: {config.get('description', 'N/A')}")
        print(f"  OCR Engine: {config['ocr_engine']}")
        print(f"  GPU Acceleration: {config['gpu_acceleration']}")
        print(f"  Update Rate: {config['update_rate']}s")
        
        # Show requirements
        requirements = config.get('requirements', {})
        if requirements and isinstance(requirements, dict):
            print(f"  Requirements:")
            for req, value in requirements.items():
                print(f"    {req}: {value}")
        elif requirements:
            print(f"  Requirements: {requirements}")
        
        # Show enabled features
        features_enabled = config.get('features_enabled', [])
        print(f"  Features: {', '.join(features_enabled) if features_enabled else 'Basic only'}")

def demo_performance_scaling():
    """Demonstrate performance across different configurations"""
    print("\n⚡ PERFORMANCE SCALING DEMONSTRATION")
    print("="*60)
    
    # Test teams for analysis
    test_teams = [
        (['Zeus', 'Ymir', 'Apollo', 'Aphrodite', 'Loki'], 
         ['Ra', 'Ares', 'Neith', 'Chang\'e', 'Thor']),
        (['Agni', 'Sobek', 'Rama', 'Hel', 'Fenrir'], 
         ['Scylla', 'Geb', 'Jing Wei', 'Sylvanus', 'Hun Batz']),
        (['Poseidon', 'Athena', 'Anhur', 'Baron Samedi', 'Susano'], 
         ['Thoth', 'Khepri', 'Cernunnos', 'Terra', 'Serqet'])
    ]
    
    # Test each tier
    detector = HardwareDetector()
    tier_configs = detector.get_tier_options()
    
    for tier_name, tier_config in tier_configs.items():
        print(f"\n🎯 Testing {tier_name.upper()} tier performance...")
        
        # Create config for this tier
        config_manager = ConfigManager()
        config_manager.set_performance_tier(tier_name)
        config = config_manager.config
        
        # Initialize components with tier config
        analyzer = CompAnalyzer(config)
        suggester = BuildSuggester(config)
        
        # Performance test
        start_time = time.time()
        analysis_times = []
        build_times = []
        
        for team1, team2 in test_teams:
            # Test analysis
            analysis_start = time.time()
            analysis = analyzer.analyze_matchup(team1, team2)
            analysis_time = time.time() - analysis_start
            analysis_times.append(analysis_time)
            
            # Test build suggestion
            build_start = time.time()
            build = suggester.suggest_build(team1[0], team2)
            build_time = time.time() - build_start
            build_times.append(build_time)
        
        total_time = time.time() - start_time
        
        # Calculate averages
        avg_analysis = sum(analysis_times) / len(analysis_times)
        avg_build = sum(build_times) / len(build_times)
        
        print(f"  Analysis: {avg_analysis*1000:.1f}ms avg ({1/avg_analysis:.0f} FPS)")
        print(f"  Builds: {avg_build*1000:.1f}ms avg ({1/avg_build:.0f} FPS)")
        print(f"  Total: {total_time*1000:.1f}ms for {len(test_teams)} matches")
        print(f"  Features: {', '.join(tier_config.get('features_enabled', []))}")

def demo_ocr_backends():
    """Demonstrate OCR backend selection"""
    print("\n👁️ OCR BACKEND DEMONSTRATION")
    print("="*60)
    
    # Test different OCR configurations
    ocr_configs = [
        {'ocr_engine': 'tesseract', 'gpu_acceleration': False},
        {'ocr_engine': 'easyocr', 'gpu_acceleration': False},
        {'ocr_engine': 'easyocr', 'gpu_acceleration': True},
    ]
    
    for i, ocr_config in enumerate(ocr_configs, 1):
        print(f"\n🔍 Configuration {i}: {ocr_config['ocr_engine'].upper()}")
        print(f"  GPU Acceleration: {ocr_config['gpu_acceleration']}")
        
        try:
            # Create config
            config_manager = ConfigManager()
            config = config_manager.config.copy()
            config.update(ocr_config)
            
            # Initialize OCR
            ocr = OCREngine(config)
            print(f"  Backend: {type(ocr.backend).__name__}")
            print(f"  God names loaded: {len(ocr.god_names)}")
            
            # Test god name matching performance
            test_names = ['Zeus', 'APOLLO', 'chang\'e', 'Ah Muzen Cab', 'The Morrigan']
            
            start_time = time.time()
            matches = []
            for name in test_names:
                matched = ocr._match_god_name(name)
                matches.append((name, matched))
            match_time = time.time() - start_time
            
            print(f"  Matching speed: {match_time*1000:.1f}ms for {len(test_names)} names")
            print(f"  Sample matches:")
            for original, matched in matches[:3]:
                print(f"    '{original}' -> '{matched}'")
                
        except Exception as e:
            print(f"  ❌ Failed to initialize: {e}")

def demo_memory_optimization():
    """Demonstrate memory usage optimization"""
    print("\n💾 MEMORY OPTIMIZATION DEMONSTRATION")
    print("="*60)
    
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    print(f"Initial memory usage: {initial_memory:.1f} MB")
    
    # Test different cache sizes
    cache_sizes = [10, 50, 100, 500]
    
    for cache_size in cache_sizes:
        print(f"\n📊 Testing cache size: {cache_size}")
        
        # Create config with specific cache size
        config_manager = ConfigManager()
        config = config_manager.config.copy()
        config['cache_size'] = cache_size
        
        # Initialize components
        analyzer = CompAnalyzer(config)
        suggester = BuildSuggester(config)
        
        # Load data and measure memory
        current_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = current_memory - initial_memory
        
        print(f"  Memory usage: {current_memory:.1f} MB (+{memory_increase:.1f} MB)")
        print(f"  Gods loaded: {len(analyzer.god_data)}")
        print(f"  Items loaded: {len(suggester.item_database)}")

def demo_feature_scaling():
    """Demonstrate feature availability across tiers"""
    print("\n🎛️ FEATURE SCALING DEMONSTRATION")
    print("="*60)
    
    detector = HardwareDetector()
    
    features = [
        'advanced_analysis',
        'voice_output', 
        'ml_predictions',
        'real_time_tracking',
        'build_suggestions',
        'team_analysis'
    ]
    
    tier_configs = detector.get_tier_options()
    
    print("Feature availability by tier:")
    print(f"{'Feature':<20} {'Minimal':<10} {'Maximum':<10}")
    print("-" * 42)
    
    for feature in features:
        minimal_available = detector.can_run_feature(feature) if detector.recommended_tier == PerformanceTier.MINIMAL else "N/A"
        
        # Simulate maximum tier
        detector.recommended_tier = PerformanceTier.MAXIMUM
        maximum_available = detector.can_run_feature(feature)
        
        # Reset to actual tier
        detector.recommended_tier = detector._determine_performance_tier()
        
        minimal_str = "✅" if minimal_available else "❌"
        maximum_str = "✅" if maximum_available else "❌"
        
        print(f"{feature:<20} {minimal_str:<10} {maximum_str:<10}")

def demo_real_world_scenarios():
    """Demonstrate real-world usage scenarios"""
    print("\n🎮 REAL-WORLD SCENARIO DEMONSTRATION")
    print("="*60)
    
    scenarios = [
        {
            'name': 'Budget Gaming Laptop',
            'specs': {'cpu_count': 4, 'memory_gb': 8, 'gpu_available': False},
            'expected_tier': 'minimal'
        },
        {
            'name': 'Mid-range Gaming PC',
            'specs': {'cpu_count': 8, 'memory_gb': 16, 'gpu_available': True, 'gpu_memory_gb': 4},
            'expected_tier': 'maximum'
        },
        {
            'name': 'High-end Gaming Rig',
            'specs': {'cpu_count': 16, 'memory_gb': 32, 'gpu_available': True, 'gpu_memory_gb': 12},
            'expected_tier': 'maximum'
        }
    ]
    
    for scenario in scenarios:
        print(f"\n🖥️ {scenario['name']}:")
        print(f"  Specs: {scenario['specs']}")
        
        # Simulate hardware detection
        detector = HardwareDetector()
        
        # Override hardware info for simulation
        original_gather = detector._gather_system_info
        detector._gather_system_info = lambda: {
            'platform': 'Windows',
            'architecture': '64bit',
            'cpu_freq': 3.0,
            **scenario['specs']
        }
        
        # Get recommendations
        tier = detector._determine_performance_tier()
        config = detector.get_recommended_config()
        
        print(f"  Recommended tier: {tier.value}")
        print(f"  Update rate: {config['update_rate']}s")
        print(f"  OCR engine: {config['ocr_engine']}")
        print(f"  GPU acceleration: {config['gpu_acceleration']}")
        
        # Restore original method
        detector._gather_system_info = original_gather

def main():
    """Run optimization demo"""
    print_header()
    
    demos = [
        ("Hardware Tiers", demo_hardware_tiers),
        ("Performance Scaling", demo_performance_scaling),
        ("OCR Backends", demo_ocr_backends),
        ("Memory Optimization", demo_memory_optimization),
        ("Feature Scaling", demo_feature_scaling),
        ("Real-world Scenarios", demo_real_world_scenarios),
    ]
    
    for demo_name, demo_func in demos:
        try:
            demo_func()
        except Exception as e:
            print(f"\n❌ {demo_name} demo failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("🎉 OPTIMIZATION DEMO COMPLETE!")
    print("\n💡 Key Takeaways:")
    print("  • System automatically adapts to available hardware")
    print("  • Performance scales from minimal to maximum tiers")
    print("  • OCR backends selected based on GPU availability")
    print("  • Memory usage optimized for different system specs")
    print("  • Features enabled/disabled based on performance tier")
    print("\n🚀 The system is ready for deployment across all hardware types!")

if __name__ == "__main__":
    main()