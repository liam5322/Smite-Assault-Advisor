#!/usr/bin/env python3
"""
🎮 SMITE 2 Assault Brain - Integrated Professional GUI
Combines your excellent UI design with our analysis system
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
import json
import os
import sys
from datetime import datetime
import webbrowser
import time
import logging

# Import our analysis components
try:
    from enhanced_items_scraper import EnhancedItemsScraper
    from smite_data_manager import SmiteDataManager
    from voice_system import VoiceSystem
    from optimized_assault_brain import HardwareProfile
except ImportError as e:
    print(f"Warning: Some analysis components not available: {e}")

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalysisOverlay(ctk.CTkToplevel):
    """Desktop overlay that appears over SMITE 2"""
    
    def __init__(self, parent, analysis_data):
        super().__init__(parent)
        
        self.analysis_data = analysis_data
        
        # Configure overlay window
        self.geometry("450x250+100+100")
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.95)
        self.title("SMITE 2 Analysis")
        
        # Make it draggable
        self.bind("<Button-1>", self.start_drag)
        self.bind("<B1-Motion>", self.on_drag)
        
        self.create_overlay_content()
        
        # Auto-close after 15 seconds
        self.after(15000, self.destroy)
    
    def create_overlay_content(self):
        """Create overlay content"""
        # Main frame
        main_frame = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(15, 10))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="⚔️ ASSAULT ANALYSIS",
            font=("Arial Black", 18),
            text_color="#f39c12"
        )
        title_label.pack(side="left")
        
        # Close button
        close_btn = ctk.CTkButton(
            header_frame,
            text="✕",
            command=self.destroy,
            width=30,
            height=30,
            font=("Arial", 16),
            fg_color="#e74c3c",
            hover_color="#c0392b"
        )
        close_btn.pack(side="right")
        
        # Win rate section
        win_rate = self.analysis_data.get('win_probability', 0.5) * 100
        win_color = "#2ecc71" if win_rate > 60 else "#e74c3c" if win_rate < 40 else "#f39c12"
        
        win_frame = ctk.CTkFrame(main_frame, fg_color="#16213e", corner_radius=10)
        win_frame.pack(fill="x", padx=15, pady=5)
        
        win_label = ctk.CTkLabel(
            win_frame,
            text=f"WIN RATE: {win_rate:.0f}%",
            font=("Arial Black", 24),
            text_color=win_color
        )
        win_label.pack(pady=10)
        
        # Key advice
        advice_frame = ctk.CTkFrame(main_frame, fg_color="#0f3460", corner_radius=10)
        advice_frame.pack(fill="x", padx=15, pady=5)
        
        key_advice = self.analysis_data.get('key_advice', ['No specific advice'])[0]
        advice_label = ctk.CTkLabel(
            advice_frame,
            text=f"💡 {key_advice}",
            font=("Arial", 14),
            text_color="#ecf0f1",
            wraplength=400
        )
        advice_label.pack(pady=10)
        
        # Item priorities
        items_frame = ctk.CTkFrame(main_frame, fg_color="#16213e", corner_radius=10)
        items_frame.pack(fill="x", padx=15, pady=(5, 15))
        
        items_title = ctk.CTkLabel(
            items_frame,
            text="🛡️ PRIORITY ITEMS",
            font=("Arial", 12, "bold"),
            text_color="#95a5a6"
        )
        items_title.pack(pady=(10, 5))
        
        item_priorities = self.analysis_data.get('item_priorities', ['Meditation Cloak - Priority 9'])
        for item in item_priorities[:2]:  # Show top 2 items
            item_label = ctk.CTkLabel(
                items_frame,
                text=item,
                font=("Arial", 11),
                text_color="#3498db"
            )
            item_label.pack()
        
        items_frame.pack_configure(pady=(5, 15))
    
    def start_drag(self, event):
        """Start dragging the overlay"""
        self.x = event.x
        self.y = event.y
    
    def on_drag(self, event):
        """Handle dragging the overlay"""
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

class AssaultBrainApp(ctk.CTk):
    """Main application with integrated analysis system"""
    
    def __init__(self):
        super().__init__()
        
        # Window Configuration
        self.title("SMITE 2 Assault Brain")
        self.geometry("900x650")
        self.minsize(800, 600)
        
        # Set window icon
        if os.path.exists("assets/icon.ico"):
            self.iconbitmap("assets/icon.ico")
        
        # Center window on screen
        self.center_window()
        
        # Initialize analysis system
        self.init_analysis_system()
        
        # Initialize variables
        self.monitoring_active = False
        self.settings = self.load_settings()
        self.analysis_history = []
        self.current_overlay = None
        
        # Create UI
        self.create_widgets()
        
        # Setup hotkeys
        self.setup_hotkeys()
        
        # Protocol for window close
        self.protocol("WM_DELETE_WINDOW", self.hide_to_tray)
        
        # Update UI with system status
        self.update_system_status()
    
    def init_analysis_system(self):
        """Initialize the analysis system components"""
        try:
            # Hardware detection
            self.hardware = HardwareProfile.detect()
            logger.info(f"Hardware: {self.hardware.performance_tier} tier, {self.hardware.ram_gb:.1f}GB RAM")
            
            # Analysis components
            self.items_scraper = EnhancedItemsScraper()
            self.data_manager = SmiteDataManager()
            
            # Voice system
            self.voice_system = VoiceSystem()
            
            self.analysis_ready = True
            logger.info("Analysis system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize analysis system: {e}")
            self.analysis_ready = False
            self.hardware = None
            self.voice_system = None
    
    def center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Create all UI widgets"""
        # Main container
        main_container = ctk.CTkFrame(self, corner_radius=0)
        main_container.pack(fill="both", expand=True)
        
        # Header Section
        self.create_header(main_container)
        
        # Content Area with Tabs
        self.create_content_area(main_container)
        
        # Status Bar
        self.create_status_bar(main_container)
    
    def create_header(self, parent):
        """Create header with logo and title"""
        header_frame = ctk.CTkFrame(parent, height=100, corner_radius=0, fg_color="#1a1a2e")
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Logo and Title Container
        title_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_container.pack(expand=True)
        
        # Game-style title with icon
        title_label = ctk.CTkLabel(
            title_container,
            text="⚔️ SMITE 2 ASSAULT BRAIN ⚔️",
            font=("Bebas Neue", 42, "bold"),
            text_color="#f39c12"
        )
        title_label.pack(pady=(20, 5))
        
        # Subtitle with system info
        hardware_info = f"{self.hardware.performance_tier.title()} Mode" if self.hardware else "System Loading"
        subtitle_label = ctk.CTkLabel(
            title_container,
            text=f"Professional Team Analysis & Counter Building • {hardware_info}",
            font=("Arial", 14),
            text_color="#95a5a6"
        )
        subtitle_label.pack()
    
    def create_content_area(self, parent):
        """Create tabbed content area"""
        # Tab container
        self.tab_view = ctk.CTkTabview(parent, corner_radius=10)
        self.tab_view.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create tabs
        self.home_tab = self.tab_view.add("🏠 Home")
        self.analysis_tab = self.tab_view.add("📊 Analysis")
        self.settings_tab = self.tab_view.add("⚙️ Settings")
        self.about_tab = self.tab_view.add("ℹ️ About")
        
        # Set default tab
        self.tab_view.set("🏠 Home")
        
        # Populate tabs
        self.create_home_tab()
        self.create_analysis_tab()
        self.create_settings_tab()
        self.create_about_tab()
    
    def create_home_tab(self):
        """Create home tab content"""
        # Status Section
        status_frame = ctk.CTkFrame(self.home_tab, fg_color="#16213e", corner_radius=15)
        status_frame.pack(fill="x", padx=20, pady=20)
        
        # Big status indicator
        self.status_icon = ctk.CTkLabel(
            status_frame,
            text="🟢" if self.monitoring_active else "🔴",
            font=("Arial", 48)
        )
        self.status_icon.pack(pady=(20, 10))
        
        status_text = "MONITORING ACTIVE" if self.monitoring_active else "MONITORING INACTIVE"
        if not self.analysis_ready:
            status_text = "ANALYSIS SYSTEM LOADING..."
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text=status_text,
            font=("Arial", 24, "bold"),
            text_color="#2ecc71" if self.monitoring_active else "#e74c3c"
        )
        self.status_label.pack(pady=(0, 20))
        
        # Control Buttons
        button_frame = ctk.CTkFrame(self.home_tab, fg_color="transparent")
        button_frame.pack(pady=20)
        
        # Start/Stop Button
        self.toggle_btn = ctk.CTkButton(
            button_frame,
            text="▶ START MONITORING" if not self.monitoring_active else "⏸ STOP MONITORING",
            command=self.toggle_monitoring,
            width=250,
            height=60,
            font=("Arial Black", 18),
            fg_color="#e74c3c" if not self.monitoring_active else "#27ae60",
            hover_color="#c0392b" if not self.monitoring_active else "#229954",
            corner_radius=10
        )
        self.toggle_btn.grid(row=0, column=0, padx=10)
        
        # Quick Analysis Button
        self.quick_analysis_btn = ctk.CTkButton(
            button_frame,
            text="⚡ QUICK ANALYSIS",
            command=self.quick_analysis,
            width=250,
            height=60,
            font=("Arial Black", 18),
            fg_color="#3498db",
            hover_color="#2980b9",
            corner_radius=10
        )
        self.quick_analysis_btn.grid(row=0, column=1, padx=10)
        
        # Info Cards
        info_container = ctk.CTkFrame(self.home_tab, fg_color="transparent")
        info_container.pack(fill="x", padx=20, pady=20)
        
        # Create info cards with real data
        cards_data = [
            ("🎮", "Hotkey", f"{self.settings.get('hotkey', 'F1')}", "Press in champion select"),
            ("📊", "Analyses", str(len(self.analysis_history)), "Team compositions analyzed"),
            ("🎯", "Hardware", f"{self.hardware.performance_tier.title()}" if self.hardware else "Loading", 
             f"{self.hardware.ram_gb:.0f}GB RAM" if self.hardware else "Detecting..."),
            ("🎤", "Voice", f"{self.settings.get('voice_personality', 'Casual')}", "Voice coaching style")
        ]
        
        for i, (icon, title, value, desc) in enumerate(cards_data):
            card = self.create_info_card(info_container, icon, title, value, desc)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
            info_container.grid_columnconfigure(i, weight=1)
    
    def create_info_card(self, parent, icon, title, value, description):
        """Create an info card widget"""
        card = ctk.CTkFrame(parent, fg_color="#0f3460", corner_radius=15)
        
        # Icon
        icon_label = ctk.CTkLabel(card, text=icon, font=("Arial", 32))
        icon_label.pack(pady=(15, 5))
        
        # Title
        title_label = ctk.CTkLabel(card, text=title, font=("Arial", 12), text_color="#95a5a6")
        title_label.pack()
        
        # Value
        value_label = ctk.CTkLabel(card, text=value, font=("Arial Black", 20), text_color="#f39c12")
        value_label.pack(pady=5)
        
        # Description
        desc_label = ctk.CTkLabel(card, text=description, font=("Arial", 10), text_color="#7f8c8d")
        desc_label.pack(pady=(0, 15))
        
        return card
    
    def create_analysis_tab(self):
        """Create analysis history tab"""
        # Header
        header_label = ctk.CTkLabel(
            self.analysis_tab,
            text="Recent Analyses",
            font=("Arial Black", 24),
            text_color="#f39c12"
        )
        header_label.pack(pady=20)
        
        # Analysis list frame
        self.analysis_list_frame = ctk.CTkScrollableFrame(self.analysis_tab, fg_color="#16213e", corner_radius=15)
        self.analysis_list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Update analysis display
        self.update_analysis_display()
    
    def update_analysis_display(self):
        """Update the analysis history display"""
        # Clear existing widgets
        for widget in self.analysis_list_frame.winfo_children():
            widget.destroy()
        
        if not self.analysis_history:
            empty_label = ctk.CTkLabel(
                self.analysis_list_frame,
                text="No analyses yet. Press F1 in champion select or use Quick Analysis!",
                font=("Arial", 16),
                text_color="#7f8c8d"
            )
            empty_label.pack(pady=50)
        else:
            # Show recent analyses
            for i, analysis in enumerate(reversed(self.analysis_history[-10:])):  # Last 10
                self.create_analysis_card(self.analysis_list_frame, analysis, i)
    
    def create_analysis_card(self, parent, analysis, index):
        """Create an analysis result card"""
        card = ctk.CTkFrame(parent, fg_color="#0f3460", corner_radius=10)
        card.pack(fill="x", padx=10, pady=5)
        
        # Header with timestamp
        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(10, 5))
        
        time_label = ctk.CTkLabel(
            header_frame,
            text=f"Analysis #{len(self.analysis_history) - index} - {analysis.get('timestamp', 'Unknown')}",
            font=("Arial", 12),
            text_color="#95a5a6"
        )
        time_label.pack(side="left")
        
        win_rate = analysis.get('win_probability', 0.5) * 100
        win_label = ctk.CTkLabel(
            header_frame,
            text=f"{win_rate:.0f}% Win Rate",
            font=("Arial Black", 14),
            text_color="#2ecc71" if win_rate > 60 else "#e74c3c" if win_rate < 40 else "#f39c12"
        )
        win_label.pack(side="right")
        
        # Teams
        teams_frame = ctk.CTkFrame(card, fg_color="transparent")
        teams_frame.pack(fill="x", padx=15, pady=5)
        
        team1_text = " • ".join(analysis.get('team1', []))
        team2_text = " • ".join(analysis.get('team2', []))
        
        teams_label = ctk.CTkLabel(
            teams_frame,
            text=f"Your Team: {team1_text}\nEnemy Team: {team2_text}",
            font=("Arial", 11),
            text_color="#ecf0f1",
            justify="left"
        )
        teams_label.pack(anchor="w")
        
        # Key advice
        if analysis.get('key_advice'):
            advice_label = ctk.CTkLabel(
                card,
                text=f"💡 {analysis['key_advice'][0]}",
                font=("Arial", 12, "bold"),
                text_color="#3498db"
            )
            advice_label.pack(padx=15, pady=(0, 10), anchor="w")
    
    def create_settings_tab(self):
        """Create settings tab with voice options"""
        # Settings container
        settings_container = ctk.CTkScrollableFrame(self.settings_tab)
        settings_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Hotkey Settings
        hotkey_frame = self.create_settings_section(settings_container, "⌨️ Hotkey Settings")
        
        hotkey_label = ctk.CTkLabel(hotkey_frame, text="Analysis Hotkey:", font=("Arial", 14))
        hotkey_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        self.hotkey_button = ctk.CTkButton(
            hotkey_frame,
            text=self.settings.get('hotkey', 'F1'),
            command=self.change_hotkey,
            width=100,
            height=35,
            font=("Arial", 14, "bold")
        )
        self.hotkey_button.grid(row=1, column=1, padx=20, pady=10)
        
        # Display Settings
        display_frame = self.create_settings_section(settings_container, "🖥️ Display Settings")
        
        display_label = ctk.CTkLabel(display_frame, text="Analysis Display:", font=("Arial", 14))
        display_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        self.display_menu = ctk.CTkOptionMenu(
            display_frame,
            values=["Desktop Overlay", "Quick Popup", "Voice Only"],
            command=self.change_display_mode,
            button_color="#f39c12",
            button_hover_color="#e67e22"
        )
        self.display_menu.set(self.settings.get('display_mode', 'Desktop Overlay'))
        self.display_menu.grid(row=1, column=1, padx=20, pady=10)
        
        # Voice Settings
        voice_frame = self.create_settings_section(settings_container, "🔊 Voice Settings")
        
        voice_label = ctk.CTkLabel(voice_frame, text="Voice Coaching:", font=("Arial", 14))
        voice_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        self.voice_switch = ctk.CTkSwitch(
            voice_frame,
            text="",
            command=self.toggle_voice,
            button_color="#f39c12",
            progress_color="#f39c12"
        )
        self.voice_switch.grid(row=1, column=1, padx=20, pady=10)
        if self.settings.get('voice_enabled', True):
            self.voice_switch.select()
        
        # Voice personality selection
        personality_label = ctk.CTkLabel(voice_frame, text="Voice Style:", font=("Arial", 14))
        personality_label.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        
        self.personality_menu = ctk.CTkOptionMenu(
            voice_frame,
            values=["Professional", "Casual", "Hype", "Tactical"],
            command=self.change_voice_personality,
            button_color="#f39c12",
            button_hover_color="#e67e22"
        )
        self.personality_menu.set(self.settings.get('voice_personality', 'Casual'))
        self.personality_menu.grid(row=2, column=1, padx=20, pady=10)
        
        # Test voice button
        test_voice_btn = ctk.CTkButton(
            voice_frame,
            text="🎤 Test Voice",
            command=self.test_voice,
            width=120,
            height=35,
            font=("Arial", 12, "bold"),
            fg_color="#9b59b6",
            hover_color="#8e44ad"
        )
        test_voice_btn.grid(row=2, column=2, padx=10, pady=10)
        
        # Volume slider
        volume_label = ctk.CTkLabel(voice_frame, text="Volume:", font=("Arial", 14))
        volume_label.grid(row=3, column=0, padx=20, pady=10, sticky="w")
        
        self.volume_slider = ctk.CTkSlider(
            voice_frame,
            from_=0,
            to=100,
            command=self.update_volume,
            button_color="#f39c12",
            progress_color="#f39c12"
        )
        self.volume_slider.set(self.settings.get('volume', 75))
        self.volume_slider.grid(row=3, column=1, padx=20, pady=10, sticky="ew")
        
        self.volume_label = ctk.CTkLabel(voice_frame, text=f"{int(self.settings.get('volume', 75))}%", font=("Arial", 14))
        self.volume_label.grid(row=3, column=2, padx=10, pady=10)
        
        # Discord Settings
        discord_frame = self.create_settings_section(settings_container, "💬 Discord Integration")
        
        webhook_label = ctk.CTkLabel(discord_frame, text="Webhook URL:", font=("Arial", 14))
        webhook_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        self.webhook_entry = ctk.CTkEntry(
            discord_frame,
            placeholder_text="https://discord.com/api/webhooks/...",
            width=300,
            height=35,
            font=("Arial", 12)
        )
        self.webhook_entry.grid(row=1, column=1, padx=20, pady=10, sticky="ew")
        if self.settings.get('discord_webhook'):
            self.webhook_entry.insert(0, self.settings.get('discord_webhook'))
        
        # Save button
        save_btn = ctk.CTkButton(
            discord_frame,
            text="Save",
            command=self.save_discord_settings,
            width=80,
            height=35,
            font=("Arial", 12, "bold"),
            fg_color="#27ae60",
            hover_color="#229954"
        )
        save_btn.grid(row=1, column=2, padx=10, pady=10)
    
    def create_settings_section(self, parent, title):
        """Create a settings section frame"""
        section = ctk.CTkFrame(parent, fg_color="#16213e", corner_radius=15)
        section.pack(fill="x", padx=0, pady=10)
        
        # Section title
        title_label = ctk.CTkLabel(
            section,
            text=title,
            font=("Arial Black", 18),
            text_color="#f39c12"
        )
        title_label.grid(row=0, column=0, columnspan=3, padx=20, pady=(15, 10), sticky="w")
        
        return section
    
    def create_about_tab(self):
        """Create about tab"""
        # Logo and version
        logo_frame = ctk.CTkFrame(self.about_tab, fg_color="transparent")
        logo_frame.pack(pady=30)
        
        app_icon = ctk.CTkLabel(
            logo_frame,
            text="⚔️",
            font=("Arial", 72)
        )
        app_icon.pack()
        
        version_label = ctk.CTkLabel(
            logo_frame,
            text="SMITE 2 Assault Brain v1.0.0",
            font=("Arial Black", 24),
            text_color="#f39c12"
        )
        version_label.pack(pady=10)
        
        # Description
        desc_text = """Professional team composition analysis and counter-building advisor
for SMITE 2 Assault mode. Get instant insights, smart item recommendations,
and voice coaching to dominate your matches."""
        
        desc_label = ctk.CTkLabel(
            self.about_tab,
            text=desc_text,
            font=("Arial", 14),
            text_color="#95a5a6",
            justify="center"
        )
        desc_label.pack(pady=20)
        
        # System info
        if self.hardware:
            system_info = f"""Hardware: {self.hardware.performance_tier.title()} ({self.hardware.ram_gb:.0f}GB RAM, {self.hardware.cpu_cores} cores)
Analysis System: {'Ready' if self.analysis_ready else 'Loading...'}
Voice System: {'Available' if self.voice_system else 'Not Available'}"""
        else:
            system_info = "System information loading..."
        
        system_label = ctk.CTkLabel(
            self.about_tab,
            text=system_info,
            font=("Arial", 12),
            text_color="#7f8c8d",
            justify="center"
        )
        system_label.pack(pady=10)
        
        # Links
        links_frame = ctk.CTkFrame(self.about_tab, fg_color="transparent")
        links_frame.pack(pady=20)
        
        github_btn = ctk.CTkButton(
            links_frame,
            text="📦 GitHub",
            command=lambda: webbrowser.open("https://github.com/liam5322/Smite-Assault-Advisor"),
            width=150,
            height=40,
            font=("Arial", 14, "bold"),
            fg_color="#333333",
            hover_color="#555555"
        )
        github_btn.grid(row=0, column=0, padx=10)
        
        discord_btn = ctk.CTkButton(
            links_frame,
            text="💬 Discord",
            command=lambda: webbrowser.open("https://discord.gg/yourinvite"),
            width=150,
            height=40,
            font=("Arial", 14, "bold"),
            fg_color="#7289da",
            hover_color="#5b6eae"
        )
        discord_btn.grid(row=0, column=1, padx=10)
    
    def create_status_bar(self, parent):
        """Create status bar at bottom"""
        self.status_bar = ctk.CTkFrame(parent, height=30, corner_radius=0, fg_color="#0f1419")
        self.status_bar.pack(fill="x", side="bottom")
        
        # Status text
        self.status_text = ctk.CTkLabel(
            self.status_bar,
            text="Ready" if self.analysis_ready else "Loading analysis system...",
            font=("Arial", 11),
            text_color="#7f8c8d"
        )
        self.status_text.pack(side="left", padx=10)
        
        # Connection indicator
        connection_status = "● Analysis: Ready" if self.analysis_ready else "● Analysis: Loading"
        self.connection_label = ctk.CTkLabel(
            self.status_bar,
            text=connection_status,
            font=("Arial", 11),
            text_color="#2ecc71" if self.analysis_ready else "#f39c12"
        )
        self.connection_label.pack(side="right", padx=10)
    
    def update_system_status(self):
        """Update system status indicators"""
        if self.analysis_ready:
            self.status_text.configure(text="Ready")
            self.connection_label.configure(text="● Analysis: Ready", text_color="#2ecc71")
        else:
            self.status_text.configure(text="Loading analysis system...")
            self.connection_label.configure(text="● Analysis: Loading", text_color="#f39c12")
    
    def toggle_monitoring(self):
        """Toggle monitoring on/off"""
        if not self.analysis_ready:
            messagebox.showwarning("Not Ready", "Analysis system is still loading. Please wait...")
            return
        
        self.monitoring_active = not self.monitoring_active
        
        if self.monitoring_active:
            self.status_icon.configure(text="🟢")
            self.status_label.configure(text="MONITORING ACTIVE", text_color="#2ecc71")
            self.toggle_btn.configure(
                text="⏸ STOP MONITORING",
                fg_color="#27ae60",
                hover_color="#229954"
            )
            self.update_status("Monitoring started - Press F1 in champion select")
        else:
            self.status_icon.configure(text="🔴")
            self.status_label.configure(text="MONITORING INACTIVE", text_color="#e74c3c")
            self.toggle_btn.configure(
                text="▶ START MONITORING",
                fg_color="#e74c3c",
                hover_color="#c0392b"
            )
            self.update_status("Monitoring stopped")
    
    def quick_analysis(self):
        """Open quick analysis dialog"""
        if not self.analysis_ready:
            messagebox.showwarning("Not Ready", "Analysis system is still loading. Please wait...")
            return
        
        dialog = QuickAnalysisDialog(self)
        dialog.grab_set()
    
    def perform_analysis(self, team1, team2):
        """Perform actual analysis using our system"""
        try:
            # Use our existing analysis system
            analysis = self.data_manager.quick_analyze(team1, team2)
            
            # Get item recommendations
            recommended_items = self.items_scraper.get_assault_recommendations(team2, team1)
            item_priorities = [
                f"🔥 {item.name} ({item.cost}g) - Priority {item.assault_priority}"
                for item in recommended_items[:3]
            ]
            
            # Create analysis result
            result = {
                'team1': team1,
                'team2': team2,
                'win_probability': analysis.win_probability,
                'confidence': analysis.confidence,
                'key_advice': analysis.key_advice,
                'item_priorities': item_priorities,
                'voice_summary': analysis.voice_summary,
                'timestamp': datetime.now().strftime("%H:%M:%S")
            }
            
            # Add to history
            self.analysis_history.append(result)
            
            # Update display
            self.update_analysis_display()
            
            # Show results based on display mode
            self.show_analysis_result(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            messagebox.showerror("Analysis Error", f"Analysis failed: {str(e)}")
            return None
    
    def show_analysis_result(self, analysis):
        """Show analysis result based on display mode"""
        display_mode = self.settings.get('display_mode', 'Desktop Overlay')
        
        if display_mode == 'Desktop Overlay':
            # Close existing overlay
            if self.current_overlay:
                self.current_overlay.destroy()
            
            # Show new overlay
            self.current_overlay = AnalysisOverlay(self, analysis)
        
        elif display_mode == 'Quick Popup':
            # Show quick popup
            self.show_quick_popup(analysis)
        
        # Voice coaching (if enabled)
        if self.settings.get('voice_enabled', True) and self.voice_system:
            self.voice_system.speak_analysis(analysis)
    
    def show_quick_popup(self, analysis):
        """Show quick popup with analysis"""
        win_rate = analysis.get('win_probability', 0.5) * 100
        key_advice = analysis.get('key_advice', [''])[0]
        
        popup_text = f"Win Rate: {win_rate:.0f}%\n\n💡 {key_advice}"
        
        messagebox.showinfo("Analysis Complete", popup_text)
    
    def setup_hotkeys(self):
        """Setup global hotkeys"""
        try:
            import keyboard
            hotkey = self.settings.get('hotkey', 'F1')
            keyboard.clear_all_hotkeys()
            keyboard.add_hotkey(hotkey.lower(), self.on_hotkey_pressed)
            logger.info(f"Hotkey {hotkey} registered")
        except Exception as e:
            logger.error(f"Failed to register hotkey: {e}")
    
    def on_hotkey_pressed(self):
        """Handle hotkey press"""
        if self.monitoring_active and self.analysis_ready:
            self.update_status("Analyzing team composition...")
            # For now, show the quick analysis dialog
            # In a full implementation, this would capture the screen
            self.after(100, self.quick_analysis)
    
    def change_hotkey(self):
        """Change hotkey dialog"""
        dialog = HotkeyDialog(self)
        dialog.grab_set()
    
    def change_display_mode(self, mode):
        """Change display mode"""
        self.settings['display_mode'] = mode
        self.save_settings()
        self.update_status(f"Display mode changed to: {mode}")
    
    def toggle_voice(self):
        """Toggle voice coaching"""
        self.settings['voice_enabled'] = self.voice_switch.get()
        self.save_settings()
    
    def change_voice_personality(self, personality):
        """Change voice personality"""
        self.settings['voice_personality'] = personality
        self.save_settings()
        
        # Update voice system personality
        if self.voice_system:
            self.voice_system.set_personality(personality.lower())
    
    def test_voice(self):
        """Test current voice settings"""
        if not self.voice_system:
            messagebox.showwarning("Voice Not Available", "Voice system is not available")
            return
        
        personality = self.settings.get('voice_personality', 'Casual')
        self.voice_system.test_voice(personality.lower())
    
    def update_volume(self, value):
        """Update volume setting"""
        self.settings['volume'] = int(value)
        self.volume_label.configure(text=f"{int(value)}%")
        self.save_settings()
    
    def save_discord_settings(self):
        """Save Discord webhook"""
        webhook = self.webhook_entry.get()
        if webhook:
            self.settings['discord_webhook'] = webhook
            self.save_settings()
            self.update_status("Discord webhook saved")
            messagebox.showinfo("Success", "Discord webhook saved successfully!")
        else:
            messagebox.showwarning("Warning", "Please enter a valid webhook URL")
    
    def hide_to_tray(self):
        """Hide window to system tray"""
        self.withdraw()
    
    def load_settings(self):
        """Load settings from file"""
        settings_file = "config/settings.json"
        default_settings = {
            "hotkey": "F1",
            "voice_enabled": True,
            "voice_personality": "Casual",
            "volume": 75,
            "display_mode": "Desktop Overlay",
            "discord_webhook": "",
            "start_with_windows": False,
            "theme": "dark"
        }
        
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    default_settings.update(loaded_settings)
            except Exception as e:
                logger.error(f"Failed to load settings: {e}")
        
        return default_settings
    
    def save_settings(self):
        """Save settings to file"""
        os.makedirs("config", exist_ok=True)
        try:
            with open("config/settings.json", 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
    
    def update_status(self, message):
        """Update status bar message"""
        self.status_text.configure(text=message)

class QuickAnalysisDialog(ctk.CTkToplevel):
    """Quick analysis dialog for manual team input"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.parent = parent
        self.title("Quick Analysis")
        self.geometry("600x500")
        self.resizable(False, False)
        
        # Center the dialog
        self.transient(parent)
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create dialog widgets"""
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="Enter Team Compositions",
            font=("Arial Black", 20),
            text_color="#f39c12"
        )
        title_label.pack(pady=20)
        
        # Teams frame
        teams_frame = ctk.CTkFrame(self, fg_color="transparent")
        teams_frame.pack(fill="both", expand=True, padx=20)
        
        # Your team
        your_team_label = ctk.CTkLabel(
            teams_frame,
            text="Your Team",
            font=("Arial", 16, "bold"),
            text_color="#3498db"
        )
        your_team_label.grid(row=0, column=0, pady=10)
        
        # Enemy team
        enemy_team_label = ctk.CTkLabel(
            teams_frame,
            text="Enemy Team",
            font=("Arial", 16, "bold"),
            text_color="#e74c3c"
        )
        enemy_team_label.grid(row=0, column=1, pady=10, padx=50)
        
        # God entries
        self.your_team_entries = []
        self.enemy_team_entries = []
        
        for i in range(5):
            # Your team entry
            your_entry = ctk.CTkEntry(
                teams_frame,
                placeholder_text=f"God {i+1}",
                width=200,
                height=35,
                font=("Arial", 12)
            )
            your_entry.grid(row=i+1, column=0, pady=5)
            self.your_team_entries.append(your_entry)
            
            # Enemy team entry
            enemy_entry = ctk.CTkEntry(
                teams_frame,
                placeholder_text=f"God {i+1}",
                width=200,
                height=35,
                font=("Arial", 12)
            )
            enemy_entry.grid(row=i+1, column=1, pady=5, padx=50)
            self.enemy_team_entries.append(enemy_entry)
        
        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=20)
        
        analyze_btn = ctk.CTkButton(
            button_frame,
            text="📊 Analyze",
            command=self.analyze,
            width=150,
            height=40,
            font=("Arial", 14, "bold"),
            fg_color="#27ae60",
            hover_color="#229954"
        )
        analyze_btn.grid(row=0, column=0, padx=10)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            width=150,
            height=40,
            font=("Arial", 14, "bold"),
            fg_color="#7f8c8d",
            hover_color="#5d6d7e"
        )
        cancel_btn.grid(row=0, column=1, padx=10)
    
    def analyze(self):
        """Perform analysis"""
        # Get team compositions
        your_team = [entry.get().strip() for entry in self.your_team_entries if entry.get().strip()]
        enemy_team = [entry.get().strip() for entry in self.enemy_team_entries if entry.get().strip()]
        
        if len(your_team) != 5 or len(enemy_team) != 5:
            messagebox.showwarning("Invalid Input", "Please enter all 5 gods for each team")
            return
        
        # Perform analysis using parent's analysis system
        result = self.parent.perform_analysis(your_team, enemy_team)
        
        if result:
            self.destroy()
            # Switch to analysis tab to show results
            self.parent.tab_view.set("📊 Analysis")

class HotkeyDialog(ctk.CTkToplevel):
    """Dialog for changing hotkey"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.parent = parent
        self.title("Change Hotkey")
        self.geometry("400x200")
        self.resizable(False, False)
        
        # Center the dialog
        self.transient(parent)
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create dialog widgets"""
        # Instructions
        instruction_label = ctk.CTkLabel(
            self,
            text="Press any key to set as hotkey",
            font=("Arial", 16),
            text_color="#95a5a6"
        )
        instruction_label.pack(pady=30)
        
        # Current key display
        self.key_label = ctk.CTkLabel(
            self,
            text="Waiting for input...",
            font=("Arial Black", 24),
            text_color="#f39c12"
        )
        self.key_label.pack(pady=10)
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            self,
            text="Cancel",
            command=self.destroy,
            width=100,
            height=35,
            font=("Arial", 12, "bold"),
            fg_color="#7f8c8d",
            hover_color="#5d6d7e"
        )
        cancel_btn.pack(pady=20)
        
        # Bind key press
        self.bind("<KeyPress>", self.on_key_press)
        self.focus_set()
    
    def on_key_press(self, event):
        """Handle key press"""
        key = event.keysym
        if key in ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12']:
            self.parent.settings['hotkey'] = key
            self.parent.save_settings()
            self.parent.hotkey_button.configure(text=key)
            self.parent.setup_hotkeys()
            messagebox.showinfo("Success", f"Hotkey changed to {key}")
            self.destroy()
        else:
            self.key_label.configure(text=f"{key} - Use F1-F12 keys only")

if __name__ == "__main__":
    # Check if another instance is running
    try:
        import psutil
        current_pid = os.getpid()
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if 'SMITE2AssaultBrain' in proc.info['name'] and proc.info['pid'] != current_pid:
                    messagebox.showinfo("Already Running", "SMITE 2 Assault Brain is already running!")
                    sys.exit(0)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except ImportError:
        pass
    
    # Create and run app
    app = AssaultBrainApp()
    app.mainloop()