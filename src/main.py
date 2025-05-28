"""
SMITE 2 Assault Brain - Main Application
Hardware-adaptive AI assistant for SMITE 2 Assault mode
"""

import asyncio
import sys
import tkinter as tk
from pathlib import Path
import logging
from datetime import datetime
import signal
import threading
from typing import Optional, Dict, Any

# Add src to path
sys.path.append(str(Path(__file__).parent))

from core.hardware_detector import HardwareDetector, PerformanceTier
from core.config_manager import ConfigManager
from vision.screen_capture import ScreenCapture
from vision.ocr_engine import OCREngine
from analysis.comp_analyzer import CompAnalyzer
from analysis.build_suggester import BuildSuggester
from ui.overlay import AssaultOverlay

# Setup logging
def setup_logging(config: Dict[str, Any]):
    """Setup logging configuration"""
    log_level = getattr(logging, config.get('log_level', 'INFO').upper())
    
    # Create logs directory
    log_dir = Path(__file__).parent.parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    # Setup logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / f'assault_brain_{datetime.now().strftime("%Y%m%d")}.log'),
            logging.StreamHandler()
        ]
    )

logger = logging.getLogger(__name__)

class AssaultBrain:
    """Main application controller with hardware-adaptive performance"""
    
    def __init__(self):
        logger.info("🎮 Initializing SMITE 2 Assault Brain...")
        
        # Initialize configuration and hardware detection
        self.config_manager = ConfigManager()
        self.config = self.config_manager.config
        self.hardware_detector = self.config_manager.hardware_detector
        
        # Setup logging with config
        setup_logging(self.config)
        
        # Log system information
        self._log_system_info()
        
        # Initialize components based on hardware capabilities
        self._initialize_components()
        
        # State tracking
        self.current_match = None
        self.last_screen_state = None
        self.running = False
        self.main_loop_task = None
        
        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()
        
        logger.info("✅ SMITE 2 Assault Brain initialized successfully!")
        
    def _log_system_info(self):
        """Log comprehensive system information"""
        system_info = self.config_manager.get_system_info()
        
        logger.info("🔧 System Information:")
        logger.info(f"  Hardware: {system_info['hardware']}")
        logger.info(f"  Recommended Tier: {system_info['recommended_tier']}")
        logger.info(f"  Current Tier: {system_info['current_tier']}")
        logger.info(f"  Features Enabled: {list(system_info['features_enabled'].keys())}")
        logger.info(f"  Validation: {system_info['validation']}")
        
    def _initialize_components(self):
        """Initialize components based on hardware capabilities"""
        try:
            # Screen capture
            self.screen_capture = ScreenCapture(self.config)
            logger.info("✅ Screen capture initialized")
            
            # OCR engine
            self.ocr_engine = OCREngine(self.config)
            logger.info(f"✅ OCR engine initialized: {self.ocr_engine.get_backend_info()}")
            
            # Analysis components
            self.comp_analyzer = CompAnalyzer(self.config)
            self.build_suggester = BuildSuggester(self.config)
            logger.info("✅ Analysis components initialized")
            
            # UI overlay
            self.overlay = AssaultOverlay(self.config)
            logger.info("✅ UI overlay initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize components: {e}")
            raise
            
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down gracefully...")
            self.stop()
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
    async def detect_game_state(self, screenshot) -> str:
        """Determine current game state from screenshot"""
        try:
            # Check for loading screen
            if self.ocr_engine.is_loading_screen(screenshot):
                return 'loading'
            elif self.ocr_engine.is_tab_screen(screenshot):
                return 'tab'
            elif self.ocr_engine.is_in_game(screenshot):
                return 'in_game'
            else:
                return 'menu'
                
        except Exception as e:
            logger.error(f"Error detecting game state: {e}")
            return 'unknown'
            
    async def process_loading_screen(self, screenshot) -> bool:
        """Extract and analyze team compositions from loading screen"""
        logger.info("🔍 Processing loading screen...")
        
        try:
            # Extract team compositions
            teams = self.ocr_engine.extract_teams(screenshot)
            
            if not teams or not teams.get('team1') or not teams.get('team2'):
                logger.warning("⚠️ Failed to detect complete teams from loading screen")
                return False
                
            logger.info(f"🎯 Teams detected - Team 1: {teams['team1']}, Team 2: {teams['team2']}")
            
            # Analyze team matchup
            analysis = self.comp_analyzer.analyze_matchup(teams['team1'], teams['team2'])
            
            # Generate build suggestions for team 1
            builds = {}
            for god in teams['team1']:
                try:
                    builds[god] = self.build_suggester.suggest_build(god, teams['team2'], teams['team1'])
                except Exception as e:
                    logger.warning(f"Failed to generate build for {god}: {e}")
                    
            # Update overlay with analysis
            self.overlay.update_analysis(analysis, builds)
            
            # Store current match data
            self.current_match = {
                'teams': teams,
                'analysis': analysis,
                'builds': builds,
                'timestamp': datetime.now()
            }
            
            logger.info(f"📊 Analysis complete - Win probability: {analysis['win_probability']*100:.1f}%")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error processing loading screen: {e}")
            return False
            
    async def process_tab_screen(self, screenshot):
        """Process TAB screen for item detection (future feature)"""
        # Placeholder for future item detection
        pass
        
    async def main_loop(self):
        """Main application loop with adaptive performance"""
        logger.info("🚀 Starting main application loop...")
        
        try:
            while self.running:
                loop_start = datetime.now()
                
                # Capture screen
                screenshot = await self.screen_capture.capture()
                
                # Detect game state
                game_state = await self.detect_game_state(screenshot)
                
                # Process based on state
                if game_state == 'loading' and self.last_screen_state != 'loading':
                    # New loading screen detected
                    await self.process_loading_screen(screenshot)
                    
                elif game_state == 'tab':
                    # TAB screen - future feature for item detection
                    await self.process_tab_screen(screenshot)
                    
                elif game_state == 'menu':
                    # Clear overlay when in menu
                    if self.current_match and self.config.get('auto_hide_in_menu', True):
                        self.overlay.clear()
                        self.current_match = None
                        
                # Update last state
                self.last_screen_state = game_state
                
                # Update overlay
                self.overlay.update()
                
                # Adaptive sleep based on performance tier
                update_rate = self.config.get('update_rate', 1.0)
                loop_time = (datetime.now() - loop_start).total_seconds()
                sleep_time = max(0.1, update_rate - loop_time)
                
                await asyncio.sleep(sleep_time)
                
        except asyncio.CancelledError:
            logger.info("Main loop cancelled")
        except Exception as e:
            logger.error(f"❌ Error in main loop: {e}", exc_info=True)
        finally:
            logger.info("Main loop stopped")
            
    def start(self):
        """Start the application"""
        if self.running:
            logger.warning("Application is already running")
            return
            
        self.running = True
        
        # Show overlay
        self.overlay.show()
        
        # Start main loop in background thread
        def run_async_loop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                self.main_loop_task = loop.create_task(self.main_loop())
                loop.run_until_complete(self.main_loop_task)
            except Exception as e:
                logger.error(f"Error in async loop: {e}")
            finally:
                loop.close()
                
        self.async_thread = threading.Thread(target=run_async_loop, daemon=True)
        self.async_thread.start()
        
        logger.info("🎮 SMITE 2 Assault Brain started!")
        
    def stop(self):
        """Stop the application gracefully"""
        if not self.running:
            return
            
        logger.info("🛑 Stopping SMITE 2 Assault Brain...")
        
        self.running = False
        
        # Cancel main loop
        if self.main_loop_task:
            self.main_loop_task.cancel()
            
        # Hide overlay
        if hasattr(self, 'overlay'):
            self.overlay.hide()
            
        # Save configuration
        self.config_manager.save_config()
        
        logger.info("✅ SMITE 2 Assault Brain stopped")
        
    def run_gui(self):
        """Run the application with GUI event loop"""
        try:
            self.start()
            
            # Keep the main thread alive for GUI
            root = tk.Tk()
            root.withdraw()  # Hide the root window
            
            # Setup cleanup on window close
            def on_closing():
                self.stop()
                root.quit()
                
            root.protocol("WM_DELETE_WINDOW", on_closing)
            
            # Run GUI event loop
            root.mainloop()
            
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Error in GUI loop: {e}", exc_info=True)
        finally:
            self.stop()

class SetupWizard:
    """Setup wizard for first-time users"""
    
    def __init__(self):
        self.hardware_detector = HardwareDetector()
        
    def run(self):
        """Run the setup wizard"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║                 SMITE 2 ASSAULT BRAIN SETUP                 ║
║              Hardware-Adaptive AI Assistant                 ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
        # Display system information
        print("🔧 SYSTEM ANALYSIS:")
        system_info = self.hardware_detector.system_info
        print(f"  CPU: {system_info['cpu_count']} cores @ {system_info.get('cpu_freq', 'Unknown')} MHz")
        print(f"  RAM: {system_info['memory_gb']:.1f} GB")
        print(f"  GPU: {'Available' if system_info['gpu_available'] else 'Not detected'}")
        if system_info['gpu_available']:
            print(f"  VRAM: {system_info['gpu_memory_gb']:.1f} GB")
        print(f"  Platform: {system_info['platform']} ({system_info['architecture']})")
        
        # Show recommended tier
        recommended_tier = self.hardware_detector.recommended_tier
        print(f"\n🎯 RECOMMENDED PERFORMANCE TIER: {recommended_tier.value.upper()}")
        
        # Show available options
        print("\n📋 AVAILABLE PERFORMANCE TIERS:")
        tier_options = self.hardware_detector.get_tier_options()
        
        for i, (tier_name, tier_config) in enumerate(tier_options.items(), 1):
            print(f"  {i}. {tier_config['name']}")
            print(f"     {tier_config['description']}")
            print(f"     Requirements: {tier_config['requirements']}")
            print(f"     Features: {', '.join(tier_config['features_enabled'])}")
            print()
            
        # Get user choice
        while True:
            try:
                choice = input(f"Select performance tier (1-{len(tier_options)}) or press Enter for recommended: ").strip()
                
                if not choice:
                    selected_tier = recommended_tier.value
                    break
                    
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(tier_options):
                    selected_tier = list(tier_options.keys())[choice_idx]
                    break
                else:
                    print("❌ Invalid choice. Please try again.")
                    
            except ValueError:
                print("❌ Please enter a number.")
                
        print(f"\n✅ Selected: {selected_tier.upper()}")
        
        # Show installation commands
        commands = self.hardware_detector.get_installation_commands(PerformanceTier(selected_tier))
        print(f"\n📦 INSTALLATION COMMANDS:")
        for cmd in commands:
            print(f"  {cmd}")
            
        print(f"\n🚀 Setup complete! Run 'python src/main.py' to start the application.")
        
        return selected_tier

def main():
    """Main entry point"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                 SMITE 2 ASSAULT BRAIN v1.0.0                ║
║              Your AI-Powered Assault Assistant              ║
║                                                              ║
║  🎯 Real-time team analysis    🛡️ Smart build suggestions   ║
║  ⚡ Hardware-adaptive performance  🎨 Smooth thematic UI    ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Check if this is first run
    config_file = Path(__file__).parent.parent / 'config' / 'settings.yaml'
    
    if not config_file.exists() or '--setup' in sys.argv:
        # Run setup wizard
        wizard = SetupWizard()
        wizard.run()
        return
        
    try:
        # Create and run application
        app = AssaultBrain()
        app.run_gui()
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        print(f"\n❌ Fatal error: {e}")
        print("Check the log file for details.")

if __name__ == "__main__":
    main()