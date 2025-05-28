"""
SMITE Meme Engine - Adding personality and humor to analysis
Because Assault without memes is just... sad
"""

import random
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class MemeResponse:
    """A meme response with context"""
    text: str
    category: str
    confidence: float
    voice_line: Optional[str] = None

class SmiteMemeEngine:
    """Generates SMITE-specific memes and humor for analysis"""
    
    def __init__(self):
        self.god_memes = self._load_god_memes()
        self.comp_memes = self._load_comp_memes()
        self.item_memes = self._load_item_memes()
        self.general_memes = self._load_general_memes()
        self.jump_party_quotes = self._load_jump_party_quotes()
        
    def _load_god_memes(self) -> Dict[str, List[str]]:
        """God-specific memes and references"""
        return {
            'Loki': [
                "Ah yes, the 'I have no friends' pick",
                "Someone's about to make 9 people angry",
                "Loki in Assault? Bold strategy, Cotton",
                "Time to practice your VEL spam"
            ],
            'Zeus': [
                "UNLIMITED POWER! ⚡",
                "Someone watched too much Star Wars",
                "Chain lightning go BRRRRR",
                "Press 4 to delete enemy team"
            ],
            'Aphrodite': [
                "The pocket healer has arrived",
                "Someone's getting a permanent boyfriend",
                "Love birds incoming 💕",
                "Time to kiss your way to victory"
            ],
            'Ares': [
                "Beads or feed, choose wisely",
                "The chain gang leader",
                "No escape! 🔗",
                "Blink + Ult = Profit"
            ],
            'Ymir': [
                "Hi! 👋 (in Ymir voice)",
                "The walking wall of 'nope'",
                "Ice to meet you! ❄️",
                "Ymir is here! *happy frost giant noises*"
            ],
            'Neith': [
                "The global sniper has entered the chat",
                "Nowhere to hide from those arrows",
                "Backflip into victory",
                "Root + Spirit Arrow = Chef's kiss"
            ],
            'Ra': [
                "KAKAW! 🦅",
                "The solar-powered chicken",
                "Healing beam go WHOOSH",
                "Snipe from across the map"
            ],
            'Kumbhakarna': [
                "The sleepy boy cometh",
                "Naptime for the enemy team",
                "Yawn your way to victory",
                "CC for days and days..."
            ]
        }
        
    def _load_comp_memes(self) -> Dict[str, List[str]]:
        """Team composition memes"""
        return {
            'healer_heavy': [
                "Your team has more healers than a hospital 🏥",
                "Sustain wars: Assault edition",
                "The 'we never die' composition",
                "Antiheal? What's that? - Enemy team probably"
            ],
            'no_healer': [
                "No healer? That's a bold strategy",
                "Meditation Cloak is your new best friend",
                "Time to play 'the floor is lava' with health",
                "Health pots are about to become currency"
            ],
            'all_physical': [
                "Physical damage only? Someone's getting cocky",
                "Enemy team: *stacks physical defense*",
                "The 'one-trick pony' composition",
                "Magical damage is overrated anyway... right?"
            ],
            'cc_heavy': [
                "CC chain combo incoming! 🔗",
                "Beads are mandatory, not optional",
                "The 'you can't move' team comp",
                "Someone's about to get locked down harder than a bank vault"
            ],
            'late_game': [
                "The 'just survive until 20 minutes' strategy",
                "Early game? Never heard of her",
                "Scaling intensifies 📈",
                "Time to play the waiting game"
            ],
            'early_game': [
                "Snowball or go home! ⛄",
                "The 'end it before they scale' rush",
                "Early aggression is the name of the game",
                "Strike fast, strike hard"
            ]
        }
        
    def _load_item_memes(self) -> Dict[str, List[str]]:
        """Item-related memes"""
        return {
            'antiheal': [
                "Time to ruin someone's day with antiheal 😈",
                "Healing? Not in my house!",
                "The fun police have arrived",
                "Say goodbye to your sustain"
            ],
            'beads': [
                "Beads or feed, the eternal dilemma",
                "Your get-out-of-jail-free card",
                "CC immunity is priceless",
                "The panic button"
            ],
            'aegis': [
                "The 'nope' button",
                "Damage immunity for the win",
                "Ultimate denial tool",
                "Making assassins cry since 2012"
            ],
            'meditation': [
                "The Assault special",
                "Mana and health, the dynamic duo",
                "Keeping the team alive since forever",
                "The fountain in your pocket"
            ]
        }
        
    def _load_general_memes(self) -> List[str]:
        """General SMITE/Assault memes"""
        return [
            "Welcome to Assault, where the comps are random and the salt is real",
            "RNG gods have spoken 🎲",
            "Time to make the best of what you've got",
            "Assault: Where positioning matters more than your main",
            "The great equalizer of SMITE",
            "Random gods, maximum chaos",
            "Adapt, improvise, overcome... or feed",
            "The mode where everyone's out of their comfort zone"
        ]
        
    def _load_jump_party_quotes(self) -> List[str]:
        """Jump party and fountain phase quotes"""
        return [
            "Jump party in fountain! 🦘",
            "Someone's practicing their spacebar skills",
            "The pre-game ritual has begun",
            "Fountain festivities detected!",
            "VEL spam incoming in 3... 2... 1...",
            "Time for the traditional Assault dance",
            "Warming up those jump muscles",
            "The calm before the storm... and jumping"
        ]
        
    def get_god_meme(self, god_name: str) -> Optional[MemeResponse]:
        """Get a meme for a specific god"""
        if god_name in self.god_memes:
            meme = random.choice(self.god_memes[god_name])
            return MemeResponse(
                text=meme,
                category="god_specific",
                confidence=0.9
            )
        return None
        
    def get_comp_meme(self, analysis: Dict[str, Any]) -> Optional[MemeResponse]:
        """Get a meme based on team composition analysis"""
        memes = []
        
        # Check for healer situations
        if analysis.get('team1_healers', 0) >= 3:
            memes.extend([(m, 'healer_heavy') for m in self.comp_memes['healer_heavy']])
        elif analysis.get('team1_healers', 0) == 0:
            memes.extend([(m, 'no_healer') for m in self.comp_memes['no_healer']])
            
        # Check for damage type imbalance
        if analysis.get('team1_physical_heavy', False):
            memes.extend([(m, 'all_physical') for m in self.comp_memes['all_physical']])
            
        # Check for CC heavy comp
        if analysis.get('team1_cc_score', 0) > 40:
            memes.extend([(m, 'cc_heavy') for m in self.comp_memes['cc_heavy']])
            
        # Check for scaling patterns
        if analysis.get('team1_late_game_score', 0) > analysis.get('team1_early_game_score', 0) + 20:
            memes.extend([(m, 'late_game') for m in self.comp_memes['late_game']])
        elif analysis.get('team1_early_game_score', 0) > analysis.get('team1_late_game_score', 0) + 20:
            memes.extend([(m, 'early_game') for m in self.comp_memes['early_game']])
            
        if memes:
            meme_text, category = random.choice(memes)
            return MemeResponse(
                text=meme_text,
                category=category,
                confidence=0.8
            )
            
        return None
        
    def get_item_meme(self, build_tips: List[str]) -> Optional[MemeResponse]:
        """Get a meme based on build recommendations"""
        for tip in build_tips:
            tip_lower = tip.lower()
            
            if 'antiheal' in tip_lower or 'heal' in tip_lower:
                meme = random.choice(self.item_memes['antiheal'])
                return MemeResponse(
                    text=meme,
                    category="item_antiheal",
                    confidence=0.9
                )
            elif 'beads' in tip_lower:
                meme = random.choice(self.item_memes['beads'])
                return MemeResponse(
                    text=meme,
                    category="item_beads",
                    confidence=0.9
                )
            elif 'aegis' in tip_lower:
                meme = random.choice(self.item_memes['aegis'])
                return MemeResponse(
                    text=meme,
                    category="item_aegis",
                    confidence=0.9
                )
            elif 'meditation' in tip_lower:
                meme = random.choice(self.item_memes['meditation'])
                return MemeResponse(
                    text=meme,
                    category="item_meditation",
                    confidence=0.8
                )
                
        return None
        
    def get_jump_party_meme(self) -> MemeResponse:
        """Get a jump party related meme"""
        meme = random.choice(self.jump_party_quotes)
        return MemeResponse(
            text=meme,
            category="jump_party",
            confidence=1.0
        )
        
    def get_win_prediction_meme(self, win_probability: float) -> MemeResponse:
        """Get a meme based on win prediction"""
        if win_probability > 0.8:
            memes = [
                "This is looking spicy! 🌶️",
                "The odds are ever in your favor",
                "Time to style on them",
                "Victory is within reach!",
                "Someone's about to get schooled"
            ]
        elif win_probability > 0.6:
            memes = [
                "Looking good, but don't get cocky",
                "Solid comp, solid chances",
                "The force is with you... mostly",
                "Cautiously optimistic vibes",
                "You've got this... probably"
            ]
        elif win_probability > 0.4:
            memes = [
                "It's anyone's game!",
                "50/50 - perfectly balanced",
                "Time to prove the algorithm wrong",
                "Skill diff incoming",
                "The real test begins now"
            ]
        else:
            memes = [
                "Time to channel your inner comeback king",
                "David vs Goliath vibes",
                "Underdog story incoming",
                "Prove the haters wrong!",
                "Miracle runs start somewhere"
            ]
            
        meme = random.choice(memes)
        return MemeResponse(
            text=meme,
            category="win_prediction",
            confidence=0.7
        )
        
    def get_random_assault_wisdom(self) -> MemeResponse:
        """Get random Assault wisdom/memes"""
        wisdom = [
            "Remember: In Assault, positioning is everything",
            "The tower is your friend, hug it tight",
            "Poke wars are an art form",
            "Never chase into their tower... unless you're feeling spicy",
            "Meditation timing separates the pros from the noobs",
            "That one guy who builds full damage on a tank... we see you",
            "Assault: Where supports become carries and carries become... confused",
            "The sacred art of backing at the right time",
            "Health relics are not suggestions, they're requirements",
            "When in doubt, group up and teamfight"
        ]
        
        meme = random.choice(wisdom)
        return MemeResponse(
            text=meme,
            category="assault_wisdom",
            confidence=0.6
        )