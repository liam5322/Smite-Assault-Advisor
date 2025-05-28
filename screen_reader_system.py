#!/usr/bin/env python3
"""
🖥️ SMITE 2 Screen Reader System
Advanced screen capture and analysis with multiple trigger options
"""

import cv2
import numpy as np
import mss
import pytesseract
import time
import threading
import keyboard
import json
import requests
from datetime import datetime
import logging
from dataclasses import dataclass
from typing import List, Optional, Callable, Dict, Any

@dataclass
class ScreenRegion:
    """Define screen regions for different game states"""
    name: str
    x: int
    y: int
    width: int
    height: int
    description: str

@dataclass
class GameState:
    """Current game state detection"""
    state: str  # "menu", "champion_select", "loading", "in_game", "scoreboard"
    confidence: float
    detected_gods: List[str]
    timestamp: datetime

class SmiteScreenReader:
    def __init__(self):
        self.running = False
        self.analysis_callback = None
        self.last_analysis = None
        self.game_state = GameState("unknown", 0.0, [], datetime.now())
        
        # Screen regions for different resolutions
        self.regions = {
            "1920x1080": {
                "champion_select": ScreenRegion("champion_select", 100, 200, 1720, 600, "Champion select area"),
                "scoreboard": ScreenRegion("scoreboard", 200, 150, 1520, 700, "Tab scoreboard area"),
                "team_comp": ScreenRegion("team_comp", 50, 50, 400, 800, "Team composition sidebar"),
                "enemy_comp": ScreenRegion("enemy_comp", 1470, 50, 400, 800, "Enemy composition sidebar")
            },
            "1366x768": {
                "champion_select": ScreenRegion("champion_select", 70, 140, 1226, 428, "Champion select area"),
                "scoreboard": ScreenRegion("scoreboard", 143, 107, 1080, 500, "Tab scoreboard area"),
                "team_comp": ScreenRegion("team_comp", 35, 35, 285, 570, "Team composition sidebar"),
                "enemy_comp": ScreenRegion("enemy_comp", 1046, 35, 285, 570, "Enemy composition sidebar")
            }
        }
        
        # Trigger options
        self.triggers = {
            "hotkey": {"enabled": True, "key": "f1", "description": "Press F1 to analyze"},
            "tab_key": {"enabled": True, "key": "tab", "description": "Auto-analyze when Tab pressed"},
            "auto_champion_select": {"enabled": True, "interval": 2.0, "description": "Auto-detect champion select"},
            "manual_button": {"enabled": True, "description": "Manual trigger button"},
            "voice_command": {"enabled": False, "phrase": "analyze team", "description": "Voice activation"}
        }
        
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging for screen reader"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('screen_reader.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def detect_resolution(self):
        """Detect current screen resolution"""
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # Primary monitor
            width = monitor["width"]
            height = monitor["height"]
            resolution = f"{width}x{height}"
            
            if resolution in self.regions:
                return resolution
            else:
                # Default to 1920x1080 and scale
                self.logger.warning(f"Unsupported resolution {resolution}, using 1920x1080 scaled")
                return "1920x1080"
    
    def capture_screen_region(self, region: ScreenRegion) -> np.ndarray:
        """Capture specific screen region"""
        with mss.mss() as sct:
            monitor = {
                "top": region.y,
                "left": region.x,
                "width": region.width,
                "height": region.height
            }
            screenshot = sct.grab(monitor)
            return np.array(screenshot)
    
    def detect_game_state(self) -> GameState:
        """Detect current SMITE 2 game state"""
        resolution = self.detect_resolution()
        regions = self.regions[resolution]
        
        # Try to detect champion select
        champ_select_img = self.capture_screen_region(regions["champion_select"])
        if self.is_champion_select(champ_select_img):
            gods = self.extract_gods_from_champion_select(champ_select_img)
            return GameState("champion_select", 0.8, gods, datetime.now())
        
        # Try to detect scoreboard (Tab pressed)
        scoreboard_img = self.capture_screen_region(regions["scoreboard"])
        if self.is_scoreboard(scoreboard_img):
            gods = self.extract_gods_from_scoreboard(scoreboard_img)
            return GameState("scoreboard", 0.9, gods, datetime.now())
        
        # Default to in-game
        return GameState("in_game", 0.5, [], datetime.now())
    
    def is_champion_select(self, img: np.ndarray) -> bool:
        """Detect if we're in champion select"""
        # Look for champion select UI elements
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Look for "ASSAULT" text or champion portraits
        text = pytesseract.image_to_string(gray, config='--psm 8')
        keywords = ["assault", "champion", "select", "lock in", "random"]
        
        return any(keyword in text.lower() for keyword in keywords)
    
    def is_scoreboard(self, img: np.ndarray) -> bool:
        """Detect if scoreboard is open"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Look for scoreboard elements
        text = pytesseract.image_to_string(gray, config='--psm 6')
        keywords = ["level", "kills", "deaths", "assists", "gold"]
        
        return sum(keyword in text.lower() for keyword in keywords) >= 2
    
    def extract_gods_from_champion_select(self, img: np.ndarray) -> List[str]:
        """Extract god names from champion select screen"""
        # This would need more sophisticated image processing
        # For now, return empty list
        return []
    
    def extract_gods_from_scoreboard(self, img: np.ndarray) -> List[str]:
        """Extract god names from scoreboard"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Enhanced OCR for god names
        text = pytesseract.image_to_string(gray, config='--psm 6')
        
        # Known SMITE 2 gods for matching
        known_gods = [
            "Zeus", "Ares", "Neith", "Ra", "Ymir", "Artemis", "Fenrir", 
            "Kukulkan", "Geb", "Janus", "Aphrodite", "Apollo", "Anhur",
            "Anubis", "Agni", "Bacchus", "Cupid", "Hades", "Poseidon",
            "Sobek", "Thor", "Loki"
        ]
        
        detected_gods = []
        for god in known_gods:
            if god.lower() in text.lower():
                detected_gods.append(god)
        
        return detected_gods[:10]  # Max 10 gods (5v5)
    
    def setup_hotkey_triggers(self):
        """Setup keyboard triggers"""
        if self.triggers["hotkey"]["enabled"]:
            key = self.triggers["hotkey"]["key"]
            keyboard.add_hotkey(key, self.trigger_analysis)
            self.logger.info(f"🔥 Hotkey trigger enabled: {key.upper()}")
        
        if self.triggers["tab_key"]["enabled"]:
            keyboard.add_hotkey("tab", self.on_tab_pressed)
            self.logger.info("🔥 Tab key detection enabled")
    
    def trigger_analysis(self):
        """Trigger team analysis"""
        if not self.running:
            return
        
        self.logger.info("🎯 Analysis triggered!")
        
        # Detect current game state
        self.game_state = self.detect_game_state()
        
        if self.game_state.state in ["champion_select", "scoreboard"]:
            if len(self.game_state.detected_gods) >= 4:  # Minimum for analysis
                self.perform_analysis(self.game_state.detected_gods)
            else:
                self.logger.warning("Not enough gods detected for analysis")
        else:
            self.logger.info(f"Game state: {self.game_state.state} - no analysis needed")
    
    def on_tab_pressed(self):
        """Handle Tab key press (scoreboard)"""
        if not self.triggers["tab_key"]["enabled"]:
            return
        
        self.logger.info("📊 Tab pressed - checking for scoreboard")
        
        # Small delay to let scoreboard appear
        time.sleep(0.2)
        self.trigger_analysis()
    
    def perform_analysis(self, gods: List[str]):
        """Perform team analysis with detected gods"""
        if len(gods) < 4:
            self.logger.warning("Not enough gods for analysis")
            return
        
        # Split into teams (assume first half is team 1, second half is team 2)
        mid_point = len(gods) // 2
        team1 = gods[:mid_point]
        team2 = gods[mid_point:]
        
        # Pad teams to 5 if needed
        while len(team1) < 5:
            team1.append("Unknown")
        while len(team2) < 5:
            team2.append("Unknown")
        
        team1 = team1[:5]
        team2 = team2[:5]
        
        self.logger.info(f"🔍 Analyzing: {team1} vs {team2}")
        
        # Call analysis API
        try:
            response = requests.post(
                "http://localhost:9000/api/analyze",
                json={"team1": team1, "team2": team2},
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                self.last_analysis = result
                
                if self.analysis_callback:
                    self.analysis_callback(result, team1, team2)
                
                self.logger.info(f"✅ Analysis complete: {result.get('win_probability', 0):.1%} win rate")
            else:
                self.logger.error(f"Analysis API error: {response.status_code}")
        
        except Exception as e:
            self.logger.error(f"Analysis failed: {e}")
    
    def start_auto_detection(self):
        """Start automatic detection thread"""
        if not self.triggers["auto_champion_select"]["enabled"]:
            return
        
        def auto_detect_loop():
            while self.running:
                try:
                    current_state = self.detect_game_state()
                    
                    # If we detect champion select and it's different from last state
                    if (current_state.state == "champion_select" and 
                        current_state.state != self.game_state.state):
                        
                        self.logger.info("🎮 Champion select detected!")
                        self.game_state = current_state
                        
                        # Wait a bit for gods to be selected
                        time.sleep(3)
                        self.trigger_analysis()
                    
                    time.sleep(self.triggers["auto_champion_select"]["interval"])
                
                except Exception as e:
                    self.logger.error(f"Auto-detection error: {e}")
                    time.sleep(5)
        
        thread = threading.Thread(target=auto_detect_loop, daemon=True)
        thread.start()
        self.logger.info("🤖 Auto-detection started")
    
    def start(self, analysis_callback: Optional[Callable] = None):
        """Start the screen reader system"""
        self.running = True
        self.analysis_callback = analysis_callback
        
        self.logger.info("🚀 SMITE 2 Screen Reader starting...")
        
        # Setup triggers
        self.setup_hotkey_triggers()
        self.start_auto_detection()
        
        self.logger.info("✅ Screen Reader active!")
        self.logger.info("Triggers:")
        for name, config in self.triggers.items():
            if config["enabled"]:
                self.logger.info(f"  • {config['description']}")
    
    def stop(self):
        """Stop the screen reader system"""
        self.running = False
        keyboard.unhook_all()
        self.logger.info("🛑 Screen Reader stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        return {
            "running": self.running,
            "game_state": self.game_state.state,
            "last_analysis": self.last_analysis,
            "triggers": {name: config["enabled"] for name, config in self.triggers.items()},
            "resolution": self.detect_resolution()
        }

class ScreenReaderGUI:
    """Simple GUI for screen reader control"""
    
    def __init__(self, screen_reader: SmiteScreenReader):
        self.screen_reader = screen_reader
        self.create_overlay()
    
    def create_overlay(self):
        """Create overlay window for manual control"""
        # This would create a small overlay window with:
        # - Manual "Analyze" button
        # - Status indicator
        # - Settings toggles
        # - Last analysis results
        pass
    
    def on_manual_trigger(self):
        """Handle manual trigger button"""
        self.screen_reader.trigger_analysis()

def main():
    """Demo the screen reader system"""
    
    def analysis_callback(result, team1, team2):
        """Handle analysis results"""
        print(f"\n🎯 ANALYSIS COMPLETE")
        print(f"Teams: {team1} vs {team2}")
        print(f"Win Rate: {result.get('win_probability', 0):.1%}")
        print(f"Items: {result.get('item_priorities', [])}")
        print(f"Advice: {result.get('key_advice', [])}")
    
    # Create screen reader
    reader = SmiteScreenReader()
    
    # Start with callback
    reader.start(analysis_callback)
    
    print("🎮 SMITE 2 Screen Reader Demo")
    print("=" * 40)
    print("Available triggers:")
    print("• Press F1 to manually analyze")
    print("• Press Tab in-game for scoreboard analysis")
    print("• Auto-detects champion select")
    print("• Press 'q' to quit")
    
    try:
        while True:
            command = input("\nCommand (status/quit): ").strip().lower()
            
            if command == "quit" or command == "q":
                break
            elif command == "status":
                status = reader.get_status()
                print(f"Status: {json.dumps(status, indent=2, default=str)}")
            elif command == "test":
                reader.trigger_analysis()
    
    except KeyboardInterrupt:
        pass
    
    finally:
        reader.stop()
        print("👋 Screen Reader stopped")

if __name__ == "__main__":
    main()