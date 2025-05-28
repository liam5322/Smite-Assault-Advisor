"""
Discord Integration - Rich Presence and webhook features
Show off your Assault prowess to your Discord buddies
"""

import json
import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class DiscordStatus:
    """Discord Rich Presence status"""
    state: str
    details: str
    large_image: str
    large_text: str
    small_image: Optional[str] = None
    small_text: Optional[str] = None
    start_timestamp: Optional[int] = None
    end_timestamp: Optional[int] = None

class DiscordRichPresence:
    """Discord Rich Presence integration"""
    
    def __init__(self, client_id: str = "your_discord_app_id"):
        self.client_id = client_id
        self.rpc = None
        self.connected = False
        self.current_status = None
        
    def connect(self) -> bool:
        """Connect to Discord Rich Presence"""
        try:
            # This would require pypresence library
            # import pypresence
            # self.rpc = pypresence.Presence(self.client_id)
            # self.rpc.connect()
            
            self.connected = True
            logger.info("🎮 Connected to Discord Rich Presence")
            return True
            
        except ImportError:
            logger.warning("pypresence not installed - Discord Rich Presence disabled")
            return False
        except Exception as e:
            logger.error(f"Failed to connect to Discord: {e}")
            return False
            
    def update_status(self, status: DiscordStatus):
        """Update Discord Rich Presence status"""
        if not self.connected:
            return
            
        try:
            status_dict = {k: v for k, v in asdict(status).items() if v is not None}
            
            # self.rpc.update(**status_dict)
            self.current_status = status
            
            logger.debug(f"Discord status updated: {status.state}")
            
        except Exception as e:
            logger.error(f"Failed to update Discord status: {e}")
            
    def set_analyzing_status(self, team: List[str]):
        """Set status for team analysis"""
        status = DiscordStatus(
            state="Analyzing team composition",
            details=f"Playing: {', '.join(team[:3])}{'...' if len(team) > 3 else ''}",
            large_image="smite_assault_brain",
            large_text="SMITE 2 Assault Brain",
            small_image="analyzing",
            small_text="Crunching numbers",
            start_timestamp=int(time.time())
        )
        self.update_status(status)
        
    def set_match_status(self, win_probability: float, team: List[str]):
        """Set status for active match"""
        confidence_emoji = "🔥" if win_probability > 0.7 else "⚡" if win_probability > 0.5 else "🤞"
        
        status = DiscordStatus(
            state=f"{confidence_emoji} Win Rate: {win_probability*100:.0f}%",
            details=f"Assault: {team[0]} & friends",
            large_image="smite_assault_brain",
            large_text="SMITE 2 Assault Brain",
            small_image="in_match",
            small_text="Dominating Assault",
            start_timestamp=int(time.time())
        )
        self.update_status(status)
        
    def set_fountain_status(self, activity: str):
        """Set status for fountain phase activities"""
        activity_messages = {
            'jump_party': "🦘 Jump party in fountain!",
            'vel_spam': "😂 VEL spam detected",
            'item_shopping': "🛒 Shopping for victory",
            'waiting': "⏳ Waiting for game start"
        }
        
        status = DiscordStatus(
            state=activity_messages.get(activity, "In fountain"),
            details="Pre-game shenanigans",
            large_image="smite_assault_brain",
            large_text="SMITE 2 Assault Brain",
            small_image="fountain",
            small_text="Fountain phase",
            start_timestamp=int(time.time())
        )
        self.update_status(status)
        
    def clear_status(self):
        """Clear Discord status"""
        if self.connected and self.rpc:
            try:
                # self.rpc.clear()
                self.current_status = None
                logger.debug("Discord status cleared")
            except Exception as e:
                logger.error(f"Failed to clear Discord status: {e}")
                
    def disconnect(self):
        """Disconnect from Discord"""
        if self.connected and self.rpc:
            try:
                # self.rpc.close()
                self.connected = False
                logger.info("Disconnected from Discord Rich Presence")
            except Exception as e:
                logger.error(f"Error disconnecting from Discord: {e}")

class DiscordWebhook:
    """Discord webhook for sending analysis results to channels"""
    
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url
        self.enabled = webhook_url is not None
        
    def send_analysis(self, analysis: Dict[str, Any], team1: List[str], team2: List[str], memes: List[str] = None):
        """Send team analysis to Discord channel"""
        if not self.enabled:
            return
            
        try:
            import requests
            
            # Create embed
            embed = self._create_analysis_embed(analysis, team1, team2, memes)
            
            payload = {
                "embeds": [embed],
                "username": "Assault Brain",
                "avatar_url": "https://example.com/assault_brain_avatar.png"
            }
            
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info("Analysis sent to Discord channel")
            
        except ImportError:
            logger.warning("requests library not available for Discord webhook")
        except Exception as e:
            logger.error(f"Failed to send Discord webhook: {e}")
            
    def _create_analysis_embed(self, analysis: Dict[str, Any], team1: List[str], team2: List[str], memes: List[str] = None) -> Dict[str, Any]:
        """Create Discord embed for analysis"""
        win_prob = analysis.get('win_probability', 0.5)
        
        # Color based on win probability
        if win_prob > 0.7:
            color = 0x00ff00  # Green
        elif win_prob > 0.5:
            color = 0xffff00  # Yellow
        else:
            color = 0xff0000  # Red
            
        embed = {
            "title": "🎮 SMITE 2 Assault Analysis",
            "color": color,
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
            "fields": [
                {
                    "name": "🏆 Win Probability",
                    "value": f"**{win_prob*100:.1f}%**",
                    "inline": True
                },
                {
                    "name": "📊 Team Score",
                    "value": f"{analysis.get('team1_score', 0):.1f}",
                    "inline": True
                },
                {
                    "name": "⚔️ Enemy Score",
                    "value": f"{analysis.get('team2_score', 0):.1f}",
                    "inline": True
                },
                {
                    "name": "👥 Your Team",
                    "value": " • ".join(team1),
                    "inline": False
                },
                {
                    "name": "🎯 Enemy Team",
                    "value": " • ".join(team2),
                    "inline": False
                }
            ],
            "footer": {
                "text": "SMITE 2 Assault Brain • Powered by AI",
                "icon_url": "https://example.com/icon.png"
            }
        }
        
        # Add strengths if available
        strengths = analysis.get('team1_strengths', [])
        if strengths:
            embed["fields"].append({
                "name": "✅ Your Strengths",
                "value": "\n".join([f"• {strength}" for strength in strengths[:5]]),
                "inline": False
            })
            
        # Add key factors
        key_factors = analysis.get('key_factors', [])
        if key_factors:
            embed["fields"].append({
                "name": "🎯 Key Factors",
                "value": "\n".join([f"• {factor}" for factor in key_factors[:3]]),
                "inline": False
            })
            
        # Add memes if provided
        if memes:
            embed["fields"].append({
                "name": "🎭 Meme Analysis",
                "value": "\n".join([f"• {meme}" for meme in memes[:3]]),
                "inline": False
            })
            
        return embed
        
    def send_fountain_update(self, activity: str, participants: int, duration: float):
        """Send fountain activity update"""
        if not self.enabled:
            return
            
        try:
            import requests
            
            activity_emojis = {
                'jump_party': '🦘',
                'vel_spam': '😂',
                'item_shopping': '🛒',
                'standing_still': '🗿'
            }
            
            emoji = activity_emojis.get(activity, '🎮')
            
            embed = {
                "title": f"{emoji} Fountain Activity Detected!",
                "description": f"**{activity.replace('_', ' ').title()}** in progress",
                "color": 0x00ffff,
                "fields": [
                    {
                        "name": "👥 Participants",
                        "value": str(participants),
                        "inline": True
                    },
                    {
                        "name": "⏱️ Duration",
                        "value": f"{duration:.1f}s",
                        "inline": True
                    }
                ],
                "footer": {
                    "text": "Fountain Phase Monitor",
                    "icon_url": "https://example.com/fountain_icon.png"
                }
            }
            
            payload = {
                "embeds": [embed],
                "username": "Fountain Watcher",
                "avatar_url": "https://example.com/fountain_avatar.png"
            }
            
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Fountain activity sent to Discord: {activity}")
            
        except Exception as e:
            logger.error(f"Failed to send fountain update: {e}")
            
    def send_build_suggestion(self, god: str, build_tips: List[str], priority_items: List[str]):
        """Send build suggestion to Discord"""
        if not self.enabled:
            return
            
        try:
            import requests
            
            embed = {
                "title": f"🛡️ Build Suggestion for {god}",
                "color": 0x9932cc,
                "fields": [
                    {
                        "name": "🔥 Priority Items",
                        "value": "\n".join([f"• {item}" for item in priority_items[:5]]),
                        "inline": False
                    },
                    {
                        "name": "💡 Pro Tips",
                        "value": "\n".join([f"• {tip}" for tip in build_tips[:3]]),
                        "inline": False
                    }
                ],
                "footer": {
                    "text": "Build Advisor",
                    "icon_url": "https://example.com/build_icon.png"
                }
            }
            
            payload = {
                "embeds": [embed],
                "username": "Build Master",
                "avatar_url": "https://example.com/build_avatar.png"
            }
            
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Build suggestion sent to Discord for {god}")
            
        except Exception as e:
            logger.error(f"Failed to send build suggestion: {e}")

class DiscordBot:
    """Discord bot for interactive features (future enhancement)"""
    
    def __init__(self, bot_token: Optional[str] = None):
        self.bot_token = bot_token
        self.enabled = bot_token is not None
        
    async def start_bot(self):
        """Start Discord bot (placeholder for future implementation)"""
        if not self.enabled:
            return
            
        # This would implement a full Discord bot with commands like:
        # !assault analyze <team1> vs <team2>
        # !assault build <god> vs <enemies>
        # !assault stats <player>
        # !assault meme
        
        logger.info("Discord bot functionality ready for implementation")
        
    def register_commands(self):
        """Register bot commands"""
        commands = [
            {
                'name': 'assault',
                'description': 'SMITE 2 Assault analysis commands',
                'subcommands': [
                    {
                        'name': 'analyze',
                        'description': 'Analyze team composition',
                        'options': [
                            {'name': 'team1', 'description': 'Your team gods', 'required': True},
                            {'name': 'team2', 'description': 'Enemy team gods', 'required': True}
                        ]
                    },
                    {
                        'name': 'build',
                        'description': 'Get build suggestion',
                        'options': [
                            {'name': 'god', 'description': 'Your god', 'required': True},
                            {'name': 'enemies', 'description': 'Enemy gods', 'required': False}
                        ]
                    },
                    {
                        'name': 'meme',
                        'description': 'Get a random Assault meme'
                    }
                ]
            }
        ]
        
        return commands