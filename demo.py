#!/usr/bin/env python3
"""
SMITE 2 Assault Brain - Demo Mode
Demonstrates the application features without requiring SMITE 2
"""

import sys
import tkinter as tk
import time
import threading
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from ui.overlay import AssaultOverlay
from ui.themes import UIThemes

def demo_analysis():
    """Generate demo analysis data"""
    return {
        'team1_score': 75.5,
        'team2_score': 68.2,
        'win_probability': 0.72,
        'team1_strengths': [
            "Superior crowd control",
            "Strong healing support", 
            "Excellent late game scaling",
            "2 S-tier gods"
        ],
        'team1_weaknesses': [
            "Weak early game",
            "Limited mobility"
        ],
        'team2_strengths': [
            "Strong team fighting",
            "Balanced damage types"
        ],
        'team2_weaknesses': [
            "No tank - vulnerable to dive",
            "Poor sustain - vulnerable to poke",
            "2 off-meta picks"
        ],
        'key_factors': [
            "Team 1 wins fights with CC chains",
            "Team 1 outlasts in extended fights",
            "Team 1 gets stronger as game progresses"
        ]
    }

def demo_builds():
    """Generate demo build suggestions"""
    return {
        'Zeus': {
            'tips': [
                "🚫 CRITICAL: Enemy has multiple healers - BUILD ANTIHEAL IMMEDIATELY",
                "🔮 MANDATORY: Purification Beads - enemy has heavy CC",
                "🛡️ Consider Spectral Armor vs enemy critical damage"
            ]
        },
        'Ares': {
            'tips': [
                "🔮 Blink Rune recommended for initiation",
                "💡 Consider Pestilence for team antiheal aura"
            ]
        }
    }

class DemoApp:
    """Demo application to showcase features"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SMITE 2 Assault Brain - Demo")
        self.root.geometry("600x400")
        self.root.configure(bg='#1a1a1a')
        
        # Demo config
        self.config = {
            'theme': 'divine_dark',
            'overlay_position': 'top-right',
            'overlay_opacity': 0.85,
            'debug_mode': True
        }
        
        self.overlay = None
        self.demo_running = False
        
        self._create_demo_ui()
        
    def _create_demo_ui(self):
        """Create demo control UI"""
        # Title
        title = tk.Label(
            self.root,
            text="🎮 SMITE 2 Assault Brain - Demo",
            font=('Arial', 20, 'bold'),
            fg='#FFD700',
            bg='#1a1a1a'
        )
        title.pack(pady=20)
        
        # Description
        desc = tk.Label(
            self.root,
            text="Experience the smooth, thematic UI and intelligent analysis\nwithout needing SMITE 2 running!",
            font=('Arial', 12),
            fg='#FFFFFF',
            bg='#1a1a1a',
            justify='center'
        )
        desc.pack(pady=10)
        
        # Buttons frame
        buttons_frame = tk.Frame(self.root, bg='#1a1a1a')
        buttons_frame.pack(pady=30)
        
        # Start demo button
        self.start_btn = tk.Button(
            buttons_frame,
            text="🚀 Start Demo",
            command=self.start_demo,
            font=('Arial', 14, 'bold'),
            bg='#4A90E2',
            fg='white',
            padx=20,
            pady=10,
            relief='flat'
        )
        self.start_btn.pack(side='left', padx=10)
        
        # Theme cycle button
        self.theme_btn = tk.Button(
            buttons_frame,
            text="🎨 Cycle Themes",
            command=self.cycle_themes,
            font=('Arial', 14),
            bg='#FF6B35',
            fg='white',
            padx=20,
            pady=10,
            relief='flat'
        )
        self.theme_btn.pack(side='left', padx=10)
        
        # Stop demo button
        self.stop_btn = tk.Button(
            buttons_frame,
            text="⏹️ Stop Demo",
            command=self.stop_demo,
            font=('Arial', 14),
            bg='#DC2626',
            fg='white',
            padx=20,
            pady=10,
            relief='flat',
            state='disabled'
        )
        self.stop_btn.pack(side='left', padx=10)
        
        # Instructions
        instructions = tk.Label(
            self.root,
            text="Demo Features:\n" +
                 "• F1 - Toggle overlay visibility\n" +
                 "• F2 - Refresh analysis\n" +
                 "• F3 - Cycle overlay position\n" +
                 "• F4 - Toggle themes\n" +
                 "• Drag overlay to reposition\n" +
                 "• Hover buttons for smooth effects",
            font=('Arial', 10),
            fg='#CCCCCC',
            bg='#1a1a1a',
            justify='left'
        )
        instructions.pack(pady=20)
        
        # Status
        self.status_label = tk.Label(
            self.root,
            text="Ready to start demo",
            font=('Arial', 11),
            fg='#00FF00',
            bg='#1a1a1a'
        )
        self.status_label.pack(pady=10)
        
    def start_demo(self):
        """Start the demo"""
        if self.demo_running:
            return
            
        self.demo_running = True
        self.start_btn.configure(state='disabled')
        self.stop_btn.configure(state='normal')
        self.status_label.configure(text="Demo running - Check overlay!", fg='#00FF00')
        
        # Create overlay
        self.overlay = AssaultOverlay(self.config)
        self.overlay.show()
        
        # Start demo sequence
        threading.Thread(target=self._demo_sequence, daemon=True).start()
        
    def _demo_sequence(self):
        """Run demo sequence"""
        try:
            # Initial state
            time.sleep(1)
            
            # Simulate loading screen detection
            self.status_label.configure(text="Simulating loading screen detection...")
            time.sleep(2)
            
            # Show analysis
            analysis = demo_analysis()
            builds = demo_builds()
            
            self.overlay.update_analysis(analysis, builds)
            self.status_label.configure(text="Analysis complete! Try the hotkeys (F1-F4)")
            
            # Demo theme cycling every 10 seconds
            themes = ['divine_dark', 'celestial_light', 'pantheon_contrast']
            theme_index = 0
            
            while self.demo_running:
                time.sleep(10)
                if self.demo_running:
                    theme_index = (theme_index + 1) % len(themes)
                    self.config['theme'] = themes[theme_index]
                    if self.overlay:
                        self.overlay._toggle_theme()
                        
        except Exception as e:
            print(f"Demo error: {e}")
            
    def cycle_themes(self):
        """Manually cycle themes"""
        if self.overlay:
            self.overlay._toggle_theme()
            
    def stop_demo(self):
        """Stop the demo"""
        self.demo_running = False
        self.start_btn.configure(state='normal')
        self.stop_btn.configure(state='disabled')
        self.status_label.configure(text="Demo stopped", fg='#FF6666')
        
        if self.overlay:
            self.overlay.hide()
            self.overlay.destroy()
            self.overlay = None
            
    def run(self):
        """Run the demo application"""
        try:
            print("""
╔══════════════════════════════════════════════════════════════╗
║              SMITE 2 ASSAULT BRAIN - DEMO MODE              ║
║                                                              ║
║  🎨 Experience smooth, thematic UI design                   ║
║  🔧 Test hardware-adaptive performance                      ║
║  📊 See intelligent analysis in action                      ║
║                                                              ║
║  No SMITE 2 required - Pure UI/UX demonstration!           ║
╚══════════════════════════════════════════════════════════════╝
            """)
            
            self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
            self.root.mainloop()
            
        except KeyboardInterrupt:
            print("\nDemo interrupted")
        except Exception as e:
            print(f"Demo error: {e}")
        finally:
            self.stop_demo()
            
    def _on_closing(self):
        """Handle window closing"""
        self.stop_demo()
        self.root.quit()

if __name__ == "__main__":
    demo = DemoApp()
    demo.run()