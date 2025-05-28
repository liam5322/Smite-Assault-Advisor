#!/usr/bin/env python3
"""
🎤 Advanced Voice System for SMITE 2 Assault Brain
Multiple voice options with personality modes
"""

import pyttsx3
import threading
import time
import logging
from typing import Dict, List, Optional
import os

logger = logging.getLogger(__name__)

class VoiceSystem:
    """Advanced voice system with multiple personalities and voices"""
    
    def __init__(self):
        self.engine = None
        self.available_voices = []
        self.current_personality = 'casual'
        self.last_speech = 0
        self.speech_cooldown = 3.0
        
        # Voice personalities with different characteristics
        self.personalities = {
            'professional': {
                'rate': 180,
                'volume': 0.8,
                'pitch': 0,
                'style': 'formal',
                'preferred_voice': 'female'
            },
            'casual': {
                'rate': 200,
                'volume': 0.9,
                'pitch': 10,
                'style': 'friendly',
                'preferred_voice': 'male'
            },
            'hype': {
                'rate': 220,
                'volume': 1.0,
                'pitch': 20,
                'style': 'energetic',
                'preferred_voice': 'young_male'
            },
            'tactical': {
                'rate': 160,
                'volume': 0.7,
                'pitch': -10,
                'style': 'serious',
                'preferred_voice': 'deep_male'
            }
        }
        
        self.initialize_engine()
    
    def initialize_engine(self):
        """Initialize TTS engine and discover voices"""
        try:
            self.engine = pyttsx3.init()
            self.discover_voices()
            self.set_personality('casual')
            logger.info(f"Voice system initialized with {len(self.available_voices)} voices")
        except Exception as e:
            logger.error(f"Failed to initialize voice system: {e}")
    
    def discover_voices(self):
        """Discover and categorize available voices"""
        if not self.engine:
            return
            
        voices = self.engine.getProperty('voices')
        self.available_voices = []
        
        for i, voice in enumerate(voices):
            voice_info = {
                'id': voice.id,
                'index': i,
                'name': voice.name,
                'gender': self._detect_gender(voice.name),
                'age': self._detect_age(voice.name),
                'quality': self._rate_voice_quality(voice.name)
            }
            self.available_voices.append(voice_info)
            logger.debug(f"Found voice: {voice_info}")
    
    def _detect_gender(self, voice_name: str) -> str:
        """Detect voice gender from name"""
        name_lower = voice_name.lower()
        
        # Common patterns for female voices
        female_indicators = ['zira', 'hazel', 'susan', 'female', 'woman', 'girl', 'cortana']
        if any(indicator in name_lower for indicator in female_indicators):
            return 'female'
        
        # Common patterns for male voices
        male_indicators = ['david', 'mark', 'male', 'man', 'boy', 'george']
        if any(indicator in name_lower for indicator in male_indicators):
            return 'male'
        
        return 'unknown'
    
    def _detect_age(self, voice_name: str) -> str:
        """Detect approximate voice age from name"""
        name_lower = voice_name.lower()
        
        if any(word in name_lower for word in ['child', 'kid', 'young']):
            return 'young'
        elif any(word in name_lower for word in ['adult', 'mature']):
            return 'adult'
        else:
            return 'unknown'
    
    def _rate_voice_quality(self, voice_name: str) -> int:
        """Rate voice quality (1-10) based on known good voices"""
        name_lower = voice_name.lower()
        
        # High quality voices (Windows 10/11)
        high_quality = ['zira', 'david', 'hazel', 'mark', 'cortana']
        if any(hq in name_lower for hq in high_quality):
            return 8
        
        # Medium quality
        medium_quality = ['microsoft', 'windows']
        if any(mq in name_lower for mq in medium_quality):
            return 6
        
        # Default quality
        return 4
    
    def get_best_voice_for_personality(self, personality: str) -> Optional[Dict]:
        """Get the best voice for a given personality"""
        if not self.available_voices:
            return None
        
        personality_config = self.personalities.get(personality, self.personalities['casual'])
        preferred_gender = personality_config.get('preferred_voice', 'male')
        
        # Filter voices by preference
        candidates = []
        
        for voice in self.available_voices:
            score = voice['quality']
            
            # Gender preference bonus
            if preferred_gender == 'female' and voice['gender'] == 'female':
                score += 3
            elif preferred_gender == 'male' and voice['gender'] == 'male':
                score += 3
            elif preferred_gender == 'young_male' and voice['gender'] == 'male' and voice['age'] == 'young':
                score += 4
            elif preferred_gender == 'deep_male' and voice['gender'] == 'male':
                score += 2
            
            candidates.append((voice, score))
        
        # Sort by score and return best
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0] if candidates else self.available_voices[0]
    
    def set_personality(self, personality: str):
        """Set voice personality and configure engine"""
        if personality not in self.personalities:
            logger.warning(f"Unknown personality: {personality}")
            personality = 'casual'
        
        self.current_personality = personality
        config = self.personalities[personality]
        
        if not self.engine:
            return
        
        # Set voice
        best_voice = self.get_best_voice_for_personality(personality)
        if best_voice:
            self.engine.setProperty('voice', best_voice['id'])
            logger.info(f"Set voice to: {best_voice['name']} for {personality} personality")
        
        # Set speech parameters
        self.engine.setProperty('rate', config['rate'])
        self.engine.setProperty('volume', config['volume'])
        
        logger.info(f"Voice personality set to: {personality}")
    
    def speak_analysis(self, analysis: Dict, priority: int = 1):
        """Speak analysis with personality-based message"""
        if not self.engine or not self._should_speak(priority):
            return
        
        message = self._generate_personality_message(analysis)
        self._speak_async(message)
    
    def _should_speak(self, priority: int) -> bool:
        """Check if should speak based on cooldown and priority"""
        now = time.time()
        if priority >= 8:  # High priority overrides cooldown
            return True
        return now - self.last_speech > self.speech_cooldown
    
    def _generate_personality_message(self, analysis: Dict) -> str:
        """Generate personality-based message"""
        win_rate = analysis.get('win_probability', 0.5) * 100
        key_advice = analysis.get('key_advice', [''])[0]
        
        personality = self.current_personality
        
        if personality == 'professional':
            return f"Analysis complete. Win probability {win_rate:.0f} percent. {key_advice}"
        
        elif personality == 'casual':
            if win_rate > 70:
                return f"Looking good! {win_rate:.0f} percent win rate. {key_advice}"
            elif win_rate < 40:
                return f"Tough matchup at {win_rate:.0f} percent. {key_advice}"
            else:
                return f"Even match at {win_rate:.0f} percent. {key_advice}"
        
        elif personality == 'hype':
            if win_rate > 60:
                return f"LET'S GO! {win_rate:.0f} percent! Time to dominate! {key_advice}"
            else:
                return f"Challenge accepted! {win_rate:.0f} percent! {key_advice} Let's prove them wrong!"
        
        elif personality == 'tactical':
            return f"Tactical assessment: {win_rate:.0f} percent probability. Priority: {key_advice}"
        
        return f"Win rate: {win_rate:.0f} percent. {key_advice}"
    
    def _speak_async(self, message: str):
        """Speak message asynchronously"""
        def speak_thread():
            try:
                self.engine.say(message)
                self.engine.runAndWait()
                self.last_speech = time.time()
                logger.debug(f"Spoke: {message}")
            except Exception as e:
                logger.error(f"Speech error: {e}")
        
        thread = threading.Thread(target=speak_thread, daemon=True)
        thread.start()
    
    def test_voice(self, personality: str = None):
        """Test current voice with sample message"""
        if personality:
            self.set_personality(personality)
        
        test_analysis = {
            'win_probability': 0.67,
            'key_advice': ['Focus on team positioning and buy anti-heal items']
        }
        
        self.speak_analysis(test_analysis, priority=10)
    
    def list_available_voices(self) -> List[Dict]:
        """Get list of available voices with details"""
        return self.available_voices
    
    def get_personality_info(self) -> Dict:
        """Get current personality configuration"""
        return {
            'current': self.current_personality,
            'available': list(self.personalities.keys()),
            'config': self.personalities[self.current_personality]
        }

def main():
    """Test the voice system"""
    print("🎤 Voice System Test")
    print("=" * 40)
    
    voice_system = VoiceSystem()
    
    print(f"Available voices: {len(voice_system.available_voices)}")
    for voice in voice_system.available_voices:
        print(f"  - {voice['name']} ({voice['gender']}, quality: {voice['quality']})")
    
    print("\nTesting personalities:")
    personalities = ['professional', 'casual', 'hype', 'tactical']
    
    for personality in personalities:
        print(f"\nTesting {personality} personality...")
        voice_system.test_voice(personality)
        time.sleep(3)  # Wait between tests

if __name__ == "__main__":
    main()