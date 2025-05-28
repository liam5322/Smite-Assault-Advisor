#!/usr/bin/env python3
"""
SMITE 2 Assault Brain - Cool Features Demo
Show off the impressive features that'll blow your Discord buddies' minds
"""

import sys
import time
import random
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from features.meme_engine import SmiteMemeEngine, MemeResponse
from features.fountain_detector import FountainPhaseDetector, FountainActivity
from features.discord_integration import DiscordRichPresence, DiscordWebhook
from features.voice_coach import VoiceCoach, CoachingTone
from core.config_manager import ConfigManager
from analysis.comp_analyzer import CompAnalyzer
from analysis.build_suggester import BuildSuggester

def print_header():
    """Print demo header"""
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║           🎮 SMITE 2 ASSAULT BRAIN - COOL FEATURES 🎮        ║")
    print("║                                                              ║")
    print("║  🎭 Memes  🦘 Jump Parties  🎤 Voice Coach  💬 Discord      ║")
    print("║                                                              ║")
    print("║        Features that'll impress your Assault buddies        ║")
    print("╚══════════════════════════════════════════════════════════════╝")

def demo_meme_engine():
    """Demonstrate the meme engine"""
    print("\n🎭 MEME ENGINE DEMONSTRATION")
    print("="*60)
    
    meme_engine = SmiteMemeEngine()
    
    # Test god-specific memes
    print("🔥 God-Specific Memes:")
    test_gods = ['Loki', 'Zeus', 'Aphrodite', 'Ares', 'Ymir']
    for god in test_gods:
        meme = meme_engine.get_god_meme(god)
        if meme:
            print(f"  {god}: \"{meme.text}\"")
    
    # Test composition memes
    print("\n😂 Composition Analysis Memes:")
    mock_analysis = {
        'team1_healers': 3,
        'team1_cc_score': 45,
        'team1_physical_heavy': True,
        'team1_late_game_score': 80,
        'team1_early_game_score': 40
    }
    
    comp_meme = meme_engine.get_comp_meme(mock_analysis)
    if comp_meme:
        print(f"  Comp: \"{comp_meme.text}\"")
    
    # Test item memes
    print("\n🛡️ Item Build Memes:")
    mock_tips = [
        "Enemy has multiple healers - BUILD ANTIHEAL IMMEDIATELY",
        "Purification Beads - enemy has heavy CC"
    ]
    
    for tip in mock_tips:
        item_meme = meme_engine.get_item_meme([tip])
        if item_meme:
            print(f"  Tip: \"{item_meme.text}\"")
    
    # Test win prediction memes
    print("\n🏆 Win Prediction Memes:")
    win_rates = [0.9, 0.65, 0.45, 0.2]
    for win_rate in win_rates:
        pred_meme = meme_engine.get_win_prediction_meme(win_rate)
        print(f"  {win_rate*100:.0f}% win rate: \"{pred_meme.text}\"")
    
    # Test jump party memes
    print("\n🦘 Jump Party Memes:")
    jump_meme = meme_engine.get_jump_party_meme()
    print(f"  \"{jump_meme.text}\"")
    
    # Test random wisdom
    print("\n🧠 Assault Wisdom:")
    wisdom = meme_engine.get_random_assault_wisdom()
    print(f"  \"{wisdom.text}\"")

def demo_fountain_detector():
    """Demonstrate fountain phase detection"""
    print("\n🦘 FOUNTAIN PHASE DETECTOR")
    print("="*60)
    
    detector = FountainPhaseDetector()
    
    # Simulate fountain phase detection
    print("🏛️ Simulating fountain phase...")
    
    # Mock screenshot (in reality this would be actual screen capture)
    import numpy as np
    mock_screenshot = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
    
    # Simulate fountain phase
    detector.phase_start_time = time.time() - 10  # Started 10 seconds ago
    
    # Detect activities
    print("\n🔍 Detecting activities...")
    
    # Simulate jump party
    jump_activity = detector.detect_jump_party(mock_screenshot)
    if jump_activity:
        print(f"  🦘 {jump_activity.activity_type}: {jump_activity.participants} players, {jump_activity.confidence:.2f} confidence")
    
    # Simulate VEL spam
    vel_activity = detector.detect_vel_spam(mock_screenshot)
    if vel_activity:
        print(f"  😂 {vel_activity.activity_type}: {vel_activity.participants} players, {vel_activity.confidence:.2f} confidence")
    
    # Analyze overall behavior
    print("\n📊 Fountain Behavior Analysis:")
    analysis = detector.analyze_fountain_behavior()
    print(f"  Total activities: {analysis['total_activities']}")
    print(f"  Social score: {analysis['social_score']:.2f}")
    print(f"  Fun factor: {analysis['fun_factor']:.2f}")
    
    # Get commentary
    print("\n💬 Fountain Commentary:")
    commentary = detector.get_fountain_commentary()
    for comment in commentary[:3]:
        print(f"  • {comment}")

def demo_voice_coach():
    """Demonstrate voice coaching system"""
    print("\n🎤 VOICE COACHING SYSTEM")
    print("="*60)
    
    # Test different coaching tones
    tones = [CoachingTone.CASUAL, CoachingTone.HYPE, CoachingTone.SARCASTIC, CoachingTone.PROFESSIONAL]
    
    for tone in tones:
        print(f"\n🎭 {tone.value.upper()} TONE:")
        coach = VoiceCoach(tone)
        
        # Mock analysis for coaching
        mock_analysis = {
            'win_probability': random.uniform(0.2, 0.9),
            'team1_score': random.uniform(40, 90)
        }
        
        # Get loading screen coaching
        line = coach.get_voice_line('loading_screen')
        if line:
            print(f"  Loading: \"{line.text}\"")
        
        # Get win rate specific coaching
        if mock_analysis['win_probability'] > 0.7:
            line = coach.get_voice_line('high_win_rate')
        else:
            line = coach.get_voice_line('low_win_rate')
        
        if line:
            print(f"  Analysis: \"{line.text}\"")
        
        # Get build coaching
        line = coach.get_voice_line('antiheal_needed')
        if line:
            print(f"  Build tip: \"{line.text}\"")

def demo_discord_integration():
    """Demonstrate Discord integration features"""
    print("\n💬 DISCORD INTEGRATION")
    print("="*60)
    
    # Rich Presence demo
    print("🎮 Discord Rich Presence:")
    rpc = DiscordRichPresence()
    
    # Simulate different status updates
    team = ['Zeus', 'Ymir', 'Apollo', 'Aphrodite', 'Loki']
    
    print("  • Setting analyzing status...")
    rpc.set_analyzing_status(team)
    if rpc.current_status:
        print(f"    State: {rpc.current_status.state}")
        print(f"    Details: {rpc.current_status.details}")
    
    print("  • Setting match status...")
    rpc.set_match_status(0.75, team)
    if rpc.current_status:
        print(f"    State: {rpc.current_status.state}")
        print(f"    Details: {rpc.current_status.details}")
    
    print("  • Setting fountain status...")
    rpc.set_fountain_status('jump_party')
    if rpc.current_status:
        print(f"    State: {rpc.current_status.state}")
        print(f"    Details: {rpc.current_status.details}")
    
    # Webhook demo (without actually sending)
    print("\n📨 Discord Webhook Features:")
    webhook = DiscordWebhook()  # No URL = demo mode
    
    print("  • Analysis embed structure ready")
    print("  • Fountain activity notifications ready")
    print("  • Build suggestion sharing ready")
    print("  • Meme integration ready")

def demo_integrated_experience():
    """Demonstrate how all features work together"""
    print("\n🌟 INTEGRATED EXPERIENCE DEMO")
    print("="*60)
    
    # Initialize all systems
    config = ConfigManager().config
    analyzer = CompAnalyzer(config)
    suggester = BuildSuggester(config)
    meme_engine = SmiteMemeEngine()
    fountain_detector = FountainPhaseDetector()
    voice_coach = VoiceCoach(CoachingTone.CASUAL)
    discord_rpc = DiscordRichPresence()
    
    # Simulate a complete Assault experience
    print("🎮 Simulating complete Assault experience...\n")
    
    # 1. Loading Screen Phase
    print("📱 LOADING SCREEN DETECTED")
    team1 = ['Zeus', 'Ymir', 'Apollo', 'Aphrodite', 'Loki']
    team2 = ['Ra', 'Ares', 'Neith', 'Chang\'e', 'Thor']
    
    print(f"  Your team: {', '.join(team1)}")
    print(f"  Enemy team: {', '.join(team2)}")
    
    # Analyze composition
    analysis = analyzer.analyze_matchup(team1, team2)
    print(f"  Win probability: {analysis['win_probability']*100:.1f}%")
    
    # Get memes
    comp_meme = meme_engine.get_comp_meme(analysis)
    if comp_meme:
        print(f"  🎭 Meme: \"{comp_meme.text}\"")
    
    # Voice coaching
    line = voice_coach.get_voice_line('loading_screen')
    if line:
        print(f"  🎤 Coach: \"{line.text}\"")
    
    # Discord status
    discord_rpc.set_analyzing_status(team1)
    print(f"  💬 Discord: {discord_rpc.current_status.state if discord_rpc.current_status else 'Status updated'}")
    
    time.sleep(1)
    
    # 2. Fountain Phase
    print("\n🏛️ FOUNTAIN PHASE DETECTED")
    
    # Simulate fountain activities
    fountain_detector.phase_start_time = time.time()
    
    # Jump party detection
    mock_screenshot = None  # Would be real screenshot
    jump_activity = fountain_detector.detect_jump_party(mock_screenshot)
    if jump_activity:
        print(f"  🦘 Jump party: {jump_activity.participants} players participating!")
        
        # Meme response
        jump_meme = meme_engine.get_jump_party_meme()
        print(f"  🎭 Meme: \"{jump_meme.text}\"")
        
        # Voice coaching
        voice_coach.coach_fountain_phase('jump_party')
        line = voice_coach.get_voice_line('jump_party')
        if line:
            print(f"  🎤 Coach: \"{line.text}\"")
        
        # Discord status
        discord_rpc.set_fountain_status('jump_party')
    
    time.sleep(1)
    
    # 3. Build Suggestions
    print("\n🛡️ BUILD ANALYSIS")
    
    build = suggester.suggest_build('Zeus', team2)
    print(f"  God: {build.god}")
    print(f"  Tips: {len(build.tips)} recommendations")
    
    if build.tips:
        print(f"  🔥 Priority: {build.tips[0]}")
        
        # Meme for build
        item_meme = meme_engine.get_item_meme(build.tips)
        if item_meme:
            print(f"  🎭 Meme: \"{item_meme.text}\"")
        
        # Voice coaching for build
        voice_coach.coach_build_suggestions(build.tips)
        if 'antiheal' in build.tips[0].lower():
            line = voice_coach.get_voice_line('antiheal_needed')
            if line:
                print(f"  🎤 Coach: \"{line.text}\"")
    
    time.sleep(1)
    
    # 4. Match Status
    print("\n⚔️ MATCH IN PROGRESS")
    
    # Update Discord with match info
    discord_rpc.set_match_status(analysis['win_probability'], team1)
    print(f"  💬 Discord: Showing {analysis['win_probability']*100:.0f}% win rate")
    
    # Win prediction meme
    pred_meme = meme_engine.get_win_prediction_meme(analysis['win_probability'])
    print(f"  🎭 Meme: \"{pred_meme.text}\"")
    
    # Gameplay coaching
    line = voice_coach.get_voice_line('positioning_tips')
    if line:
        print(f"  🎤 Coach: \"{line.text}\"")
    
    print("\n🎉 Complete experience demonstrated!")
    print("   All features working together seamlessly!")

def demo_assault_culture():
    """Demonstrate SMITE Assault culture integration"""
    print("\n🎮 ASSAULT CULTURE INTEGRATION")
    print("="*60)
    
    meme_engine = SmiteMemeEngine()
    
    print("🏛️ Classic Assault Moments:")
    
    # The classics
    moments = [
        ("The 'No Healer' Panic", "no_healer"),
        ("The Healer Paradise", "healer_heavy"),
        ("The CC Chain Nightmare", "cc_heavy"),
        ("The Late Game Dream", "late_game"),
        ("The Early Game Rush", "early_game")
    ]
    
    for moment_name, comp_type in moments:
        print(f"\n  📖 {moment_name}:")
        if comp_type in meme_engine.comp_memes:
            meme = random.choice(meme_engine.comp_memes[comp_type])
            print(f"     \"{meme}\"")
    
    print("\n🎭 God Personality Memes:")
    personality_gods = ['Loki', 'Zeus', 'Ymir', 'Aphrodite', 'Kumbhakarna']
    for god in personality_gods:
        meme = meme_engine.get_god_meme(god)
        if meme:
            print(f"  {god}: \"{meme.text}\"")
    
    print("\n🧠 Assault Wisdom Collection:")
    for i in range(5):
        wisdom = meme_engine.get_random_assault_wisdom()
        print(f"  {i+1}. {wisdom.text}")

def main():
    """Run the cool features demo"""
    print_header()
    
    demos = [
        ("Meme Engine", demo_meme_engine),
        ("Fountain Detector", demo_fountain_detector),
        ("Voice Coach", demo_voice_coach),
        ("Discord Integration", demo_discord_integration),
        ("Assault Culture", demo_assault_culture),
        ("Integrated Experience", demo_integrated_experience),
    ]
    
    for demo_name, demo_func in demos:
        try:
            demo_func()
            time.sleep(0.5)  # Brief pause between demos
        except Exception as e:
            print(f"\n❌ {demo_name} demo failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("🎉 COOL FEATURES DEMO COMPLETE!")
    print("\n💡 Features that'll impress your Discord buddies:")
    print("  🎭 Smart memes that understand SMITE culture")
    print("  🦘 Jump party detection and commentary")
    print("  🎤 AI voice coach with multiple personalities")
    print("  💬 Discord Rich Presence and webhook integration")
    print("  🧠 Deep Assault game knowledge and humor")
    print("  🌟 All features working together seamlessly")
    print("\n🚀 Your Assault buddies won't know what hit them!")

if __name__ == "__main__":
    main()