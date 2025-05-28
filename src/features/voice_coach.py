"""
Voice Coaching System - Real-time audio guidance
Your personal Assault sensei in your ear
"""

import logging
import time
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class CoachingTone(Enum):
    """Different coaching personalities"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    HYPE = "hype"
    SARCASTIC = "sarcastic"
    EDUCATIONAL = "educational"

@dataclass
class VoiceLine:
    """A voice coaching line"""
    text: str
    tone: CoachingTone
    priority: int  # 1-10, higher = more important
    context: str
    cooldown: float = 30.0  # Seconds before can repeat

class VoiceCoach:
    """AI voice coach for Assault gameplay"""
    
    def __init__(self, tone: CoachingTone = CoachingTone.CASUAL):
        self.tone = tone
        self.voice_lines = self._load_voice_lines()
        self.recent_lines = {}  # Track cooldowns
        self.tts_engine = None
        self.enabled = False
        
    def _load_voice_lines(self) -> Dict[str, List[VoiceLine]]:
        """Load voice coaching lines by context"""
        return {
            'loading_screen': [
                VoiceLine("Alright team, let's see what RNG gave us today", CoachingTone.CASUAL, 5, "loading"),
                VoiceLine("Time to analyze this composition and find our win condition", CoachingTone.PROFESSIONAL, 7, "loading"),
                VoiceLine("LET'S GOOO! Time to show them what we're made of!", CoachingTone.HYPE, 6, "loading"),
                VoiceLine("Oh wonderful, another 'balanced' Assault comp...", CoachingTone.SARCASTIC, 4, "loading"),
            ],
            
            'high_win_rate': [
                VoiceLine("This comp is looking spicy! You've got a great chance here", CoachingTone.CASUAL, 8, "analysis"),
                VoiceLine("Excellent team synergy detected. Execute your strategy and victory is yours", CoachingTone.PROFESSIONAL, 9, "analysis"),
                VoiceLine("OH MY GOD THIS COMP IS INSANE! Time to absolutely demolish them!", CoachingTone.HYPE, 10, "analysis"),
                VoiceLine("Well well, looks like someone actually got a decent comp for once", CoachingTone.SARCASTIC, 7, "analysis"),
            ],
            
            'low_win_rate': [
                VoiceLine("Tough comp, but don't give up! Focus on your positioning and teamwork", CoachingTone.CASUAL, 8, "analysis"),
                VoiceLine("Challenging composition detected. Prioritize safe play and capitalize on enemy mistakes", CoachingTone.PROFESSIONAL, 9, "analysis"),
                VoiceLine("Underdog story time! Let's prove the algorithm wrong!", CoachingTone.HYPE, 8, "analysis"),
                VoiceLine("Ah yes, the classic 'how did this happen' team comp. Good luck with that", CoachingTone.SARCASTIC, 6, "analysis"),
            ],
            
            'antiheal_needed': [
                VoiceLine("Enemy has multiple healers - antiheal is mandatory, not optional!", CoachingTone.CASUAL, 10, "build"),
                VoiceLine("Critical: Enemy healing detected. Prioritize anti-heal items immediately", CoachingTone.PROFESSIONAL, 10, "build"),
                VoiceLine("ANTIHEAL TIME! Shut down their sustain and watch them crumble!", CoachingTone.HYPE, 10, "build"),
                VoiceLine("Oh look, healers everywhere. Guess someone forgot antiheal exists", CoachingTone.SARCASTIC, 9, "build"),
            ],
            
            'beads_needed': [
                VoiceLine("Heavy CC comp detected - beads are your best friend here", CoachingTone.CASUAL, 9, "build"),
                VoiceLine("Enemy crowd control threat level: Maximum. Purification Beads recommended", CoachingTone.PROFESSIONAL, 9, "build"),
                VoiceLine("CC CHAINS INCOMING! Get those beads ready!", CoachingTone.HYPE, 9, "build"),
                VoiceLine("Wow, that's a lot of CC. Hope you like being stunned", CoachingTone.SARCASTIC, 8, "build"),
            ],
            
            'fountain_phase': [
                VoiceLine("Fountain phase! Time to buy your items and mentally prepare", CoachingTone.CASUAL, 5, "fountain"),
                VoiceLine("Pre-game preparation phase. Review your build and strategy", CoachingTone.PROFESSIONAL, 6, "fountain"),
                VoiceLine("FOUNTAIN HYPE! Get those items and let's do this!", CoachingTone.HYPE, 5, "fountain"),
                VoiceLine("Ah yes, the traditional fountain standing simulator", CoachingTone.SARCASTIC, 4, "fountain"),
            ],
            
            'jump_party': [
                VoiceLine("Jump party detected! The team bonding has begun", CoachingTone.CASUAL, 6, "fountain"),
                VoiceLine("Team coordination exercise in progress via synchronized jumping", CoachingTone.PROFESSIONAL, 5, "fountain"),
                VoiceLine("JUMP PARTY! This is what Assault culture is all about!", CoachingTone.HYPE, 8, "fountain"),
                VoiceLine("Oh great, the spacebar warriors are at it again", CoachingTone.SARCASTIC, 5, "fountain"),
            ],
            
            'positioning_tips': [
                VoiceLine("Remember: positioning is everything in Assault. Stay behind your frontline", CoachingTone.CASUAL, 7, "gameplay"),
                VoiceLine("Maintain proper positioning. Utilize your tank as cover and respect enemy poke", CoachingTone.PROFESSIONAL, 8, "gameplay"),
                VoiceLine("POSITIONING! Stay safe, stay alive, stay winning!", CoachingTone.HYPE, 7, "gameplay"),
                VoiceLine("Yes, standing in the enemy team is definitely the play here", CoachingTone.SARCASTIC, 6, "gameplay"),
            ],
            
            'teamfight_tips': [
                VoiceLine("Teamfight incoming! Focus targets and use your abilities wisely", CoachingTone.CASUAL, 8, "gameplay"),
                VoiceLine("Engage parameters optimal. Execute coordinated team fight strategy", CoachingTone.PROFESSIONAL, 9, "gameplay"),
                VoiceLine("TEAMFIGHT TIME! Let's show them what we're made of!", CoachingTone.HYPE, 9, "gameplay"),
                VoiceLine("Ah yes, the classic 'everyone press all buttons' strategy", CoachingTone.SARCASTIC, 7, "gameplay"),
            ],
            
            'comeback_motivation': [
                VoiceLine("Down but not out! One good teamfight can change everything", CoachingTone.CASUAL, 8, "motivation"),
                VoiceLine("Current deficit manageable. Maintain focus and capitalize on opportunities", CoachingTone.PROFESSIONAL, 8, "motivation"),
                VoiceLine("COMEBACK TIME! This is where legends are made!", CoachingTone.HYPE, 9, "motivation"),
                VoiceLine("Well this is going about as expected", CoachingTone.SARCASTIC, 5, "motivation"),
            ]
        }
        
    def initialize_tts(self) -> bool:
        """Initialize text-to-speech engine"""
        try:
            import pyttsx3
            
            self.tts_engine = pyttsx3.init()
            
            # Configure voice settings
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Try to find a good voice
                for voice in voices:
                    if 'english' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
                        
            # Set speech rate and volume
            self.tts_engine.setProperty('rate', 180)  # Words per minute
            self.tts_engine.setProperty('volume', 0.8)  # 0.0 to 1.0
            
            self.enabled = True
            logger.info("🎤 Voice coaching system initialized")
            return True
            
        except ImportError:
            logger.warning("pyttsx3 not available - voice coaching disabled")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize TTS: {e}")
            return False
            
    def speak(self, text: str, priority: int = 5) -> bool:
        """Speak text using TTS"""
        if not self.enabled or not self.tts_engine:
            logger.debug(f"Voice line (disabled): {text}")
            return False
            
        try:
            # Check if we should interrupt current speech for high priority
            if priority >= 8:
                self.tts_engine.stop()
                
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            
            logger.info(f"🎤 Spoke: {text}")
            return True
            
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return False
            
    def get_voice_line(self, context: str, filters: Dict[str, Any] = None) -> Optional[VoiceLine]:
        """Get appropriate voice line for context"""
        if context not in self.voice_lines:
            return None
            
        # Filter by tone
        available_lines = [
            line for line in self.voice_lines[context]
            if line.tone == self.tone or self.tone == CoachingTone.CASUAL
        ]
        
        if not available_lines:
            available_lines = self.voice_lines[context]
            
        # Filter out recently used lines
        current_time = time.time()
        available_lines = [
            line for line in available_lines
            if line.text not in self.recent_lines or 
            (current_time - self.recent_lines[line.text]) > line.cooldown
        ]
        
        if not available_lines:
            return None
            
        # Choose line based on priority and randomness
        weights = [line.priority for line in available_lines]
        chosen_line = random.choices(available_lines, weights=weights)[0]
        
        # Mark as recently used
        self.recent_lines[chosen_line.text] = current_time
        
        return chosen_line
        
    def coach_loading_screen(self, analysis: Dict[str, Any]):
        """Provide coaching during loading screen"""
        # General loading screen comment
        line = self.get_voice_line('loading_screen')
        if line:
            self.speak(line.text, line.priority)
            
        # Specific analysis-based coaching
        win_prob = analysis.get('win_probability', 0.5)
        
        if win_prob > 0.7:
            line = self.get_voice_line('high_win_rate')
        elif win_prob < 0.4:
            line = self.get_voice_line('low_win_rate')
        else:
            return  # No specific coaching for average comps
            
        if line:
            time.sleep(2)  # Brief pause between lines
            self.speak(line.text, line.priority)
            
    def coach_build_suggestions(self, build_tips: List[str]):
        """Provide coaching for build suggestions"""
        for tip in build_tips:
            tip_lower = tip.lower()
            
            if 'antiheal' in tip_lower or 'heal' in tip_lower:
                line = self.get_voice_line('antiheal_needed')
                if line:
                    self.speak(line.text, line.priority)
                    break
                    
            elif 'beads' in tip_lower or 'cc' in tip_lower:
                line = self.get_voice_line('beads_needed')
                if line:
                    self.speak(line.text, line.priority)
                    break
                    
    def coach_fountain_phase(self, activity: str = None):
        """Provide coaching during fountain phase"""
        if activity == 'jump_party':
            line = self.get_voice_line('jump_party')
        else:
            line = self.get_voice_line('fountain_phase')
            
        if line:
            self.speak(line.text, line.priority)
            
    def coach_gameplay_tips(self, context: str):
        """Provide general gameplay coaching"""
        contexts = ['positioning_tips', 'teamfight_tips', 'comeback_motivation']
        
        if context in contexts:
            line = self.get_voice_line(context)
            if line:
                self.speak(line.text, line.priority)
                
    def set_coaching_tone(self, tone: CoachingTone):
        """Change coaching personality"""
        self.tone = tone
        logger.info(f"🎭 Coaching tone changed to: {tone.value}")
        
        # Announce the change
        announcements = {
            CoachingTone.PROFESSIONAL: "Professional coaching mode activated",
            CoachingTone.CASUAL: "Casual coaching mode activated",
            CoachingTone.HYPE: "HYPE MODE ACTIVATED! LET'S GOOO!",
            CoachingTone.SARCASTIC: "Sarcastic mode enabled. This should be fun",
            CoachingTone.EDUCATIONAL: "Educational mode activated. Time to learn"
        }
        
        if tone in announcements:
            self.speak(announcements[tone], 6)
            
    def get_coaching_stats(self) -> Dict[str, Any]:
        """Get coaching session statistics"""
        return {
            'lines_spoken': len(self.recent_lines),
            'current_tone': self.tone.value,
            'enabled': self.enabled,
            'recent_contexts': list(set(
                line.context for line in self.voice_lines.values()
                for line in line if line.text in self.recent_lines
            ))
        }
        
    def cleanup(self):
        """Clean up TTS resources"""
        if self.tts_engine:
            try:
                self.tts_engine.stop()
            except:
                pass
            self.tts_engine = None
            
        self.enabled = False
        logger.info("🎤 Voice coaching system cleaned up")

class VoiceLinePlayer:
    """Plays pre-recorded god voice lines for extra immersion"""
    
    def __init__(self):
        self.voice_files = {}
        self.audio_enabled = False
        
    def initialize_audio(self) -> bool:
        """Initialize audio playback system"""
        try:
            import pygame
            pygame.mixer.init()
            self.audio_enabled = True
            logger.info("🔊 Audio system initialized for voice lines")
            return True
        except ImportError:
            logger.warning("pygame not available - voice line playback disabled")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize audio: {e}")
            return False
            
    def load_voice_files(self, voice_pack_path: str):
        """Load god voice line files"""
        # This would load actual audio files
        # voice_files = {
        #     'Zeus': {
        #         'ultimate': 'zeus_ultimate.wav',
        #         'victory': 'zeus_victory.wav'
        #     }
        # }
        pass
        
    def play_god_line(self, god: str, context: str) -> bool:
        """Play a god voice line"""
        if not self.audio_enabled:
            return False
            
        # This would play actual audio files
        logger.info(f"🎭 Playing {god} voice line: {context}")
        return True