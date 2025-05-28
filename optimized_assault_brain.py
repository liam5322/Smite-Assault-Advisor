#!/usr/bin/env python3
"""
🎮 SMITE 2 Assault Brain v1.0-lite
Optimized desktop overlay with hardware-adaptive performance
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import threading
import queue
import psutil
import cv2
import numpy as np
from mss import mss
import keyboard
import pyttsx3
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class HardwareProfile:
    """Hardware detection and performance scaling"""
    ram_gb: float
    cpu_cores: int
    has_gpu: bool
    performance_tier: str  # 'minimal', 'standard', 'maximum'
    
    @classmethod
    def detect(cls) -> 'HardwareProfile':
        """Auto-detect hardware capabilities"""
        ram_gb = psutil.virtual_memory().total / (1024**3)
        cpu_cores = psutil.cpu_count()
        
        # Simple GPU detection (could be enhanced)
        has_gpu = False
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            has_gpu = len(gpus) > 0
        except ImportError:
            pass
        
        # Determine performance tier
        if ram_gb >= 16 and cpu_cores >= 8:
            tier = 'maximum'
        elif ram_gb >= 8 and cpu_cores >= 4:
            tier = 'standard'
        else:
            tier = 'minimal'
        
        return cls(ram_gb, cpu_cores, has_gpu, tier)

@dataclass
class GameState:
    """Current game state detection"""
    phase: str  # 'loading', 'champion_select', 'in_game', 'scoreboard'
    team1: List[str]
    team2: List[str]
    timestamp: float
    confidence: float

class ScreenReader:
    """Optimized screen capture and OCR"""
    
    def __init__(self, hardware: HardwareProfile):
        self.hardware = hardware
        self.sct = mss()
        self.last_capture = None
        self.capture_interval = self._get_capture_interval()
        
        # Performance scaling
        if hardware.performance_tier == 'minimal':
            self.ocr_enabled = False
            self.capture_size = (640, 360)  # 360p
        elif hardware.performance_tier == 'standard':
            self.ocr_enabled = True
            self.capture_size = (1280, 720)  # 720p
        else:
            self.ocr_enabled = True
            self.capture_size = (1920, 1080)  # 1080p
    
    def _get_capture_interval(self) -> float:
        """Adaptive capture rate based on hardware"""
        intervals = {
            'minimal': 2.0,    # 0.5 FPS
            'standard': 0.5,   # 2 FPS
            'maximum': 0.1     # 10 FPS
        }
        return intervals[self.hardware.performance_tier]
    
    def capture_screen(self) -> Optional[np.ndarray]:
        """Capture game screen with performance optimization"""
        try:
            # Capture primary monitor
            monitor = self.sct.monitors[1]
            screenshot = self.sct.grab(monitor)
            
            # Convert to numpy array
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            # Resize for performance
            if img.shape[:2] != self.capture_size[::-1]:
                img = cv2.resize(img, self.capture_size)
            
            self.last_capture = time.time()
            return img
            
        except Exception as e:
            logger.error(f"Screen capture failed: {e}")
            return None
    
    def detect_game_state(self, img: np.ndarray) -> GameState:
        """Detect current game phase and extract team info"""
        # Simple template matching for game phases
        # This would be enhanced with actual SMITE 2 UI detection
        
        # Mock detection for demo
        return GameState(
            phase='in_game',
            team1=['Zeus', 'Ares', 'Apollo', 'Thor', 'Ymir'],
            team2=['Artemis', 'Fenrir', 'Kukulkan', 'Geb', 'Janus'],
            timestamp=time.time(),
            confidence=0.85
        )

class TriggerSystem:
    """Multiple trigger mechanisms for analysis"""
    
    def __init__(self, callback):
        self.callback = callback
        self.triggers_active = True
        self.last_trigger = 0
        self.cooldown = 2.0  # Prevent spam
        
    def setup_triggers(self):
        """Setup all trigger mechanisms"""
        # 1. Hotkey trigger (F1)
        keyboard.add_hotkey('f1', self._hotkey_trigger)
        
        # 2. Tab key hook (scoreboard detection)
        keyboard.add_hotkey('tab', self._tab_trigger)
        
        # 3. Manual trigger (F9)
        keyboard.add_hotkey('f9', self._manual_trigger)
        
        logger.info("🎮 Triggers active: F1 (auto), Tab (scoreboard), F9 (manual)")
    
    def _hotkey_trigger(self):
        """F1 hotkey pressed"""
        self._trigger('hotkey_f1')
    
    def _tab_trigger(self):
        """Tab key pressed (scoreboard)"""
        self._trigger('tab_scoreboard')
    
    def _manual_trigger(self):
        """F9 manual trigger"""
        self._trigger('manual_f9')
    
    def _trigger(self, source: str):
        """Execute trigger with cooldown"""
        now = time.time()
        if now - self.last_trigger < self.cooldown:
            return
        
        self.last_trigger = now
        logger.info(f"🔥 Trigger activated: {source}")
        
        if self.callback:
            threading.Thread(target=self.callback, args=(source,), daemon=True).start()

class VoiceCoach:
    """AI voice coaching with personality modes"""
    
    def __init__(self, hardware: HardwareProfile):
        self.hardware = hardware
        self.engine = None
        self.personality = 'casual'  # 'professional', 'casual', 'hype', 'sarcastic'
        self.last_advice = 0
        self.advice_cooldown = 10.0
        
        # Initialize TTS if hardware allows
        if hardware.performance_tier != 'minimal':
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', 180)
                self.engine.setProperty('volume', 0.8)
            except Exception as e:
                logger.warning(f"TTS initialization failed: {e}")
    
    def speak_analysis(self, analysis: Dict, priority: int = 1):
        """Speak analysis with personality"""
        if not self.engine or not self._should_speak(priority):
            return
        
        # Generate personality-based message
        message = self._generate_message(analysis)
        
        # Speak in background thread
        threading.Thread(target=self._speak_async, args=(message,), daemon=True).start()
    
    def _should_speak(self, priority: int) -> bool:
        """Check if should speak based on cooldown and priority"""
        now = time.time()
        if priority >= 8:  # High priority overrides cooldown
            return True
        return now - self.last_advice > self.advice_cooldown
    
    def _generate_message(self, analysis: Dict) -> str:
        """Generate personality-based message"""
        win_rate = analysis.get('win_probability', 0.5) * 100
        
        personalities = {
            'professional': f"Analysis complete. Win probability {win_rate:.0f} percent. {analysis.get('key_advice', [''])[0]}",
            'casual': f"Looking at {win_rate:.0f} percent win rate. {analysis.get('key_advice', [''])[0]}",
            'hype': f"LET'S GO! {win_rate:.0f} percent! {analysis.get('key_advice', [''])[0]}",
            'sarcastic': f"Oh wow, {win_rate:.0f} percent. {analysis.get('key_advice', [''])[0]}"
        }
        
        return personalities.get(self.personality, personalities['casual'])
    
    def _speak_async(self, message: str):
        """Speak message asynchronously"""
        try:
            self.engine.say(message)
            self.engine.runAndWait()
            self.last_advice = time.time()
        except Exception as e:
            logger.error(f"TTS error: {e}")

class AssaultBrain:
    """Main Assault Brain system"""
    
    def __init__(self):
        self.hardware = HardwareProfile.detect()
        self.screen_reader = ScreenReader(self.hardware)
        self.voice_coach = VoiceCoach(self.hardware)
        self.trigger_system = TriggerSystem(self.analyze_current_state)
        
        # Analysis components
        self.analysis_queue = queue.Queue()
        self.running = False
        
        logger.info(f"🚀 Assault Brain initialized - {self.hardware.performance_tier} tier")
        logger.info(f"💾 RAM: {self.hardware.ram_gb:.1f}GB, CPU: {self.hardware.cpu_cores} cores")
    
    def start(self):
        """Start the Assault Brain system"""
        self.running = True
        
        # Setup triggers
        self.trigger_system.setup_triggers()
        
        # Start analysis worker
        analysis_thread = threading.Thread(target=self._analysis_worker, daemon=True)
        analysis_thread.start()
        
        logger.info("🎮 Assault Brain is ACTIVE! Press F1 for analysis, F9 for manual trigger")
        
        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop the system"""
        self.running = False
        logger.info("🛑 Assault Brain stopped")
    
    def analyze_current_state(self, trigger_source: str):
        """Analyze current game state"""
        # Capture screen
        img = self.screen_reader.capture_screen()
        if img is None:
            logger.warning("Failed to capture screen")
            return
        
        # Detect game state
        game_state = self.screen_reader.detect_game_state(img)
        
        # Queue analysis
        self.analysis_queue.put({
            'trigger_source': trigger_source,
            'game_state': game_state,
            'timestamp': time.time()
        })
    
    def _analysis_worker(self):
        """Background analysis worker"""
        while self.running:
            try:
                # Get analysis request
                request = self.analysis_queue.get(timeout=1)
                
                # Perform analysis
                analysis = self._perform_analysis(request['game_state'])
                
                # Voice coaching
                self.voice_coach.speak_analysis(analysis)
                
                # Log results
                logger.info(f"📊 Analysis: {analysis['win_probability']:.1%} win rate")
                for advice in analysis.get('key_advice', []):
                    logger.info(f"💡 {advice}")
                
                for item in analysis.get('item_priorities', []):
                    logger.info(f"🛡️ {item}")
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Analysis error: {e}")
    
    def _perform_analysis(self, game_state: GameState) -> Dict:
        """Perform team composition analysis"""
        # Import analysis components
        try:
            from enhanced_items_scraper import EnhancedItemsScraper
            from smite_data_manager import SmiteDataManager
            
            # Initialize components
            scraper = EnhancedItemsScraper()
            data_manager = SmiteDataManager()
            
            # Perform analysis
            analysis = data_manager.quick_analyze(game_state.team1, game_state.team2)
            
            # Get item recommendations
            recommended_items = scraper.get_assault_recommendations(game_state.team2, game_state.team1)
            item_priorities = [
                f"🔥 {item.name} ({item.cost}g) - Priority {item.assault_priority}"
                for item in recommended_items[:3]
            ]
            
            return {
                'win_probability': analysis.win_probability,
                'confidence': analysis.confidence,
                'key_advice': analysis.key_advice,
                'item_priorities': item_priorities,
                'voice_summary': analysis.voice_summary,
                'timestamp': analysis.timestamp
            }
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {
                'win_probability': 0.5,
                'confidence': 'low',
                'key_advice': ['Analysis temporarily unavailable'],
                'item_priorities': ['🔥 Meditation Cloak (0g) - Priority 9'],
                'voice_summary': 'Analysis unavailable',
                'timestamp': time.time()
            }

def main():
    """Main entry point"""
    print("🎮 SMITE 2 Assault Brain v1.0-lite")
    print("=" * 50)
    
    # Initialize and start
    brain = AssaultBrain()
    brain.start()

if __name__ == "__main__":
    main()