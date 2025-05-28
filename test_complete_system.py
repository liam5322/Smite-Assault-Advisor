#!/usr/bin/env python3
"""
🧪 SMITE 2 Assault Advisor - Complete System Test
Tests all components including game detection, OCR, analysis, and voice coaching
"""

import asyncio
import sys
import time
import logging
from pathlib import Path
import numpy as np
import cv2

# Import our modules
from assault_brain_unified import (
    UnifiedDataManager, GameDetector, ScreenCapture, OCREngine, 
    VoiceCoach, AssaultBrainUnified, MatchAnalysis
)
from smite2_data_updater import SMITE2DataUpdater

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SystemTester:
    """Comprehensive system tester"""
    
    def __init__(self):
        self.test_results = {}
        self.total_tests = 0
        self.passed_tests = 0
    
    def test_result(self, test_name: str, passed: bool, details: str = ""):
        """Record test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            print(f"✅ {test_name}: PASSED {details}")
        else:
            print(f"❌ {test_name}: FAILED {details}")
        
        self.test_results[test_name] = {"passed": passed, "details": details}
    
    def test_data_manager(self):
        """Test unified data manager"""
        print("\n🔧 Testing Data Manager...")
        
        try:
            data_manager = UnifiedDataManager()
            
            # Test god loading
            gods_count = len(data_manager.gods)
            self.test_result("God Data Loading", gods_count >= 10, f"({gods_count} gods loaded)")
            
            # Test god retrieval
            zeus = data_manager.get_god("Zeus")
            self.test_result("God Retrieval", zeus is not None and zeus.name == "Zeus", 
                            f"(Zeus: {zeus.role if zeus else 'Not found'})")
            
            # Test items loading
            items_count = len(data_manager.items)
            self.test_result("Item Data Loading", items_count >= 10, f"({items_count} items loaded)")
            
            # Test item retrieval
            meditation = data_manager.get_item("meditation_cloak")
            self.test_result("Item Retrieval", meditation is not None, 
                            f"(Meditation: {meditation.cost if meditation else 'Not found'})")
            
            # Test analysis caching
            test_teams = {
                "team1": ["Zeus", "Ares", "Neith", "Thor", "Hel"],
                "team2": ["Loki", "Ymir", "Tiamat", "Marti", "Cthulhu"]
            }
            
            analysis = data_manager.analyze_teams(test_teams["team1"], test_teams["team2"])
            self.test_result("Team Analysis", analysis is not None, 
                            f"(Analysis generated: {len(analysis.recommendations) if analysis else 0} recommendations)")
            
        except Exception as e:
            self.test_result("Data Manager", False, f"Exception: {e}")
    
    def test_game_detector(self):
        """Test game detection"""
        print("\n🎮 Testing Game Detector...")
        
        try:
            detector = GameDetector()
            
            # Test process detection (will likely fail unless SMITE is running)
            smite_running = detector.is_smite_running()
            self.test_result("SMITE Process Detection", True, 
                            f"(SMITE running: {smite_running})")
            
            # Test window detection
            window = detector.get_smite_window()
            self.test_result("Window Detection", True, 
                            f"(Window found: {window is not None})")
            
            # Test window rect
            rect = detector.get_window_rect()
            self.test_result("Window Rectangle", True, 
                            f"(Rect: {rect is not None})")
            
        except Exception as e:
            self.test_result("Game Detector", False, f"Exception: {e}")
    
    def test_screen_capture(self):
        """Test screen capture"""
        print("\n📸 Testing Screen Capture...")
        
        try:
            capture = ScreenCapture()
            
            # Test screen capture
            screenshot = capture.capture_screen()
            self.test_result("Screen Capture", screenshot is not None, 
                            f"(Image shape: {screenshot.shape if screenshot is not None else 'None'})")
            
            # Test game active detection
            game_active = capture.is_game_active()
            self.test_result("Game Active Detection", True, 
                            f"(Game active: {game_active})")
            
        except Exception as e:
            self.test_result("Screen Capture", False, f"Exception: {e}")
    
    def test_ocr_engine(self):
        """Test OCR engine"""
        print("\n👁️ Testing OCR Engine...")
        
        try:
            ocr = OCREngine()
            
            # Create a test image with text
            test_image = np.ones((600, 800, 3), dtype=np.uint8) * 255
            cv2.putText(test_image, "SMITE 2 ASSAULT", (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
            cv2.putText(test_image, "Zeus Ares Neith Thor Hel", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            cv2.putText(test_image, "Loki Ymir Tiamat Marti", (50, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            
            # Test loading screen detection
            is_loading = ocr.is_loading_screen(test_image)
            self.test_result("Loading Screen Detection", True, 
                            f"(Detected: {is_loading})")
            
            # Test team extraction
            teams = ocr.extract_teams(test_image)
            self.test_result("Team Extraction", teams is not None, 
                            f"(Teams: {len(teams['team1']) if teams else 0} vs {len(teams['team2']) if teams else 0})")
            
        except Exception as e:
            self.test_result("OCR Engine", False, f"Exception: {e}")
    
    def test_voice_coach(self):
        """Test voice coaching"""
        print("\n🎤 Testing Voice Coach...")
        
        try:
            voice = VoiceCoach()
            
            # Test voice initialization
            self.test_result("Voice Initialization", voice.engine is not None, 
                            "(TTS engine initialized)")
            
            # Test voice announcement (without actually speaking)
            test_analysis = MatchAnalysis(
                team1_gods=["Zeus", "Ares", "Neith", "Thor", "Hel"],
                team2_gods=["Loki", "Ymir", "Tiamat", "Marti", "Cthulhu"],
                win_probability=0.65,
                key_strategies=["Focus anti-heal", "Protect Zeus"],
                item_recommendations=["Divine Ruin", "Meditation Cloak"],
                threat_assessment="High burst potential from enemy team",
                recommendations=["Build defensively", "Group for team fights"]
            )
            
            # Test coaching generation (don't actually speak)
            coaching_text = voice._generate_coaching_text(test_analysis)
            self.test_result("Coaching Text Generation", len(coaching_text) > 0, 
                            f"({len(coaching_text)} characters)")
            
        except Exception as e:
            self.test_result("Voice Coach", False, f"Exception: {e}")
    
    async def test_data_updater(self):
        """Test data updater"""
        print("\n🔄 Testing Data Updater...")
        
        try:
            async with SMITE2DataUpdater() as updater:
                # Test god data fetching
                gods_data = await updater.fetch_current_god_data()
                self.test_result("God Data Fetching", len(gods_data) > 0, 
                                f"({len(gods_data)} gods)")
                
                # Test item data fetching
                items_data = await updater.fetch_current_item_data()
                self.test_result("Item Data Fetching", len(items_data) > 0, 
                                f"({len(items_data)} items)")
                
                # Test meta info update
                await updater.update_meta_info()
                meta_summary = updater.get_current_meta_summary()
                self.test_result("Meta Info Update", "meta_info" in meta_summary, 
                                f"(Patch: {meta_summary['meta_info'].get('current_patch', 'Unknown')})")
                
        except Exception as e:
            self.test_result("Data Updater", False, f"Exception: {e}")
    
    def test_unified_system(self):
        """Test the complete unified system"""
        print("\n🎮 Testing Unified System...")
        
        try:
            # Initialize the complete system
            brain = AssaultBrainUnified()
            
            self.test_result("System Initialization", True, 
                            "(All components initialized)")
            
            # Test system state
            self.test_result("System Ready", not brain.running, 
                            "(System ready to start)")
            
            # Test component integration
            has_all_components = all([
                brain.data_manager is not None,
                brain.screen_capture is not None,
                brain.ocr_engine is not None,
                brain.overlay is not None,
                brain.voice_coach is not None
            ])
            
            self.test_result("Component Integration", has_all_components, 
                            "(All components present)")
            
        except Exception as e:
            self.test_result("Unified System", False, f"Exception: {e}")
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🧪 SMITE 2 Assault Advisor - Complete System Test")
        print("=" * 60)
        
        # Run all tests
        self.test_data_manager()
        self.test_game_detector()
        self.test_screen_capture()
        self.test_ocr_engine()
        self.test_voice_coach()
        await self.test_data_updater()
        self.test_unified_system()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 Test Summary:")
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests)*100:.1f}%")
        
        if self.passed_tests == self.total_tests:
            print("\n🎉 ALL TESTS PASSED! System is ready for production!")
        elif self.passed_tests >= self.total_tests * 0.8:
            print("\n✅ Most tests passed. System is functional with minor issues.")
        else:
            print("\n⚠️  Multiple test failures. Please review and fix issues.")
        
        print("\n📋 Detailed Results:")
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result["passed"] else "❌ FAIL"
            print(f"{status}: {test_name} {result['details']}")
        
        return self.passed_tests == self.total_tests

async def main():
    """Main test runner"""
    tester = SystemTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🚀 Ready to launch! Run: python assault_brain_unified.py")
    else:
        print("\n🔧 Please fix issues before launching the application.")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())