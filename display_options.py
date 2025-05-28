#!/usr/bin/env python3
"""
🖥️ Display Options for SMITE 2 Assault Brain
Multiple display modes with user customization
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
import time
import logging
from typing import Dict, Optional
import win10toast

logger = logging.getLogger(__name__)

class DisplayManager:
    """Manages different display modes for analysis results"""
    
    def __init__(self, parent_app):
        self.parent = parent_app
        self.current_overlay = None
        self.toast_notifier = None
        
        # Initialize toast notifier for Windows notifications
        try:
            self.toast_notifier = win10toast.ToastNotifier()
        except Exception as e:
            logger.warning(f"Toast notifications not available: {e}")
    
    def show_analysis(self, analysis_data: Dict, settings: Dict):
        """Show analysis based on user settings"""
        display_mode = settings.get('display_mode', 'Desktop Overlay')
        
        # Close any existing overlay
        if self.current_overlay:
            self.current_overlay.destroy()
            self.current_overlay = None
        
        # Show based on selected modes
        if display_mode == 'Desktop Overlay':
            self.show_desktop_overlay(analysis_data, settings)
        elif display_mode == 'Quick Popup':
            self.show_quick_popup(analysis_data)
        elif display_mode == 'System Notification':
            self.show_system_notification(analysis_data)
        elif display_mode == 'Minimal HUD':
            self.show_minimal_hud(analysis_data, settings)
        elif display_mode == 'Voice Only':
            pass  # Voice is handled separately
        elif display_mode == 'Silent Mode':
            pass  # No visual display
    
    def show_desktop_overlay(self, analysis_data: Dict, settings: Dict):
        """Show desktop overlay (like car dashboard)"""
        overlay_style = settings.get('overlay_style', 'Standard')
        
        if overlay_style == 'Minimal':
            self.current_overlay = MinimalOverlay(self.parent, analysis_data, settings)
        elif overlay_style == 'Compact':
            self.current_overlay = CompactOverlay(self.parent, analysis_data, settings)
        else:
            self.current_overlay = StandardOverlay(self.parent, analysis_data, settings)
    
    def show_quick_popup(self, analysis_data: Dict):
        """Show quick popup message"""
        win_rate = analysis_data.get('win_probability', 0.5) * 100
        key_advice = analysis_data.get('key_advice', [''])[0]
        
        popup_text = f"🎯 Win Rate: {win_rate:.0f}%\n\n💡 {key_advice}"
        
        # Create custom popup
        popup = QuickPopup(self.parent, popup_text)
    
    def show_system_notification(self, analysis_data: Dict):
        """Show Windows system notification"""
        if not self.toast_notifier:
            return
        
        win_rate = analysis_data.get('win_probability', 0.5) * 100
        key_advice = analysis_data.get('key_advice', [''])[0]
        
        title = f"SMITE 2 Analysis - {win_rate:.0f}% Win Rate"
        message = key_advice
        
        try:
            self.toast_notifier.show_toast(
                title,
                message,
                duration=5,
                icon_path="assets/icon.ico" if os.path.exists("assets/icon.ico") else None
            )
        except Exception as e:
            logger.error(f"Failed to show notification: {e}")
    
    def show_minimal_hud(self, analysis_data: Dict, settings: Dict):
        """Show minimal HUD overlay"""
        self.current_overlay = MinimalHUD(self.parent, analysis_data, settings)

class StandardOverlay(ctk.CTkToplevel):
    """Standard desktop overlay - full information"""
    
    def __init__(self, parent, analysis_data, settings):
        super().__init__(parent)
        
        self.analysis_data = analysis_data
        self.settings = settings
        
        # Configure window
        self.geometry("450x280+100+100")
        self.attributes("-topmost", True)
        self.attributes("-alpha", settings.get('overlay_opacity', 0.95))
        self.title("SMITE 2 Analysis")
        self.configure(fg_color="#1a1a2e")
        
        # Make draggable
        self.bind("<Button-1>", self.start_drag)
        self.bind("<B1-Motion>", self.on_drag)
        
        self.create_content()
        
        # Auto-close timer
        auto_close = settings.get('overlay_duration', 15)
        if auto_close > 0:
            self.after(auto_close * 1000, self.destroy)
    
    def create_content(self):
        """Create overlay content"""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(15, 10))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="⚔️ ASSAULT ANALYSIS",
            font=("Arial Black", 18),
            text_color="#f39c12"
        )
        title_label.pack(side="left")
        
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
        
        # Win rate
        win_rate = self.analysis_data.get('win_probability', 0.5) * 100
        win_color = "#2ecc71" if win_rate > 60 else "#e74c3c" if win_rate < 40 else "#f39c12"
        
        win_frame = ctk.CTkFrame(self, fg_color="#16213e", corner_radius=10)
        win_frame.pack(fill="x", padx=15, pady=5)
        
        win_label = ctk.CTkLabel(
            win_frame,
            text=f"WIN RATE: {win_rate:.0f}%",
            font=("Arial Black", 24),
            text_color=win_color
        )
        win_label.pack(pady=10)
        
        # Key advice
        advice_frame = ctk.CTkFrame(self, fg_color="#0f3460", corner_radius=10)
        advice_frame.pack(fill="x", padx=15, pady=5)
        
        key_advice = self.analysis_data.get('key_advice', ['No advice'])[0]
        advice_label = ctk.CTkLabel(
            advice_frame,
            text=f"💡 {key_advice}",
            font=("Arial", 14),
            text_color="#ecf0f1",
            wraplength=400
        )
        advice_label.pack(pady=10)
        
        # Items
        items_frame = ctk.CTkFrame(self, fg_color="#16213e", corner_radius=10)
        items_frame.pack(fill="x", padx=15, pady=(5, 15))
        
        items_title = ctk.CTkLabel(
            items_frame,
            text="🛡️ PRIORITY ITEMS",
            font=("Arial", 12, "bold"),
            text_color="#95a5a6"
        )
        items_title.pack(pady=(10, 5))
        
        item_priorities = self.analysis_data.get('item_priorities', [])
        for item in item_priorities[:2]:
            item_label = ctk.CTkLabel(
                items_frame,
                text=item,
                font=("Arial", 11),
                text_color="#3498db"
            )
            item_label.pack()
        
        items_frame.pack_configure(pady=(5, 15))
    
    def start_drag(self, event):
        self.x = event.x
        self.y = event.y
    
    def on_drag(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

class CompactOverlay(ctk.CTkToplevel):
    """Compact overlay - essential info only"""
    
    def __init__(self, parent, analysis_data, settings):
        super().__init__(parent)
        
        self.analysis_data = analysis_data
        
        # Configure window
        self.geometry("300x150+100+100")
        self.attributes("-topmost", True)
        self.attributes("-alpha", settings.get('overlay_opacity', 0.9))
        self.title("Analysis")
        self.configure(fg_color="#1a1a2e")
        
        # Make draggable
        self.bind("<Button-1>", self.start_drag)
        self.bind("<B1-Motion>", self.on_drag)
        
        self.create_content()
        
        # Auto-close
        auto_close = settings.get('overlay_duration', 10)
        if auto_close > 0:
            self.after(auto_close * 1000, self.destroy)
    
    def create_content(self):
        """Create compact content"""
        # Header with close
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="⚔️ ANALYSIS",
            font=("Arial Black", 14),
            text_color="#f39c12"
        )
        title_label.pack(side="left")
        
        close_btn = ctk.CTkButton(
            header_frame,
            text="✕",
            command=self.destroy,
            width=25,
            height=25,
            font=("Arial", 12),
            fg_color="#e74c3c"
        )
        close_btn.pack(side="right")
        
        # Win rate
        win_rate = self.analysis_data.get('win_probability', 0.5) * 100
        win_color = "#2ecc71" if win_rate > 60 else "#e74c3c" if win_rate < 40 else "#f39c12"
        
        win_label = ctk.CTkLabel(
            self,
            text=f"{win_rate:.0f}% WIN RATE",
            font=("Arial Black", 20),
            text_color=win_color
        )
        win_label.pack(pady=10)
        
        # Key advice (shortened)
        key_advice = self.analysis_data.get('key_advice', [''])[0]
        if len(key_advice) > 40:
            key_advice = key_advice[:37] + "..."
        
        advice_label = ctk.CTkLabel(
            self,
            text=f"💡 {key_advice}",
            font=("Arial", 12),
            text_color="#ecf0f1",
            wraplength=280
        )
        advice_label.pack(pady=(0, 15))
    
    def start_drag(self, event):
        self.x = event.x
        self.y = event.y
    
    def on_drag(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

class MinimalOverlay(ctk.CTkToplevel):
    """Minimal overlay - just win rate"""
    
    def __init__(self, parent, analysis_data, settings):
        super().__init__(parent)
        
        self.analysis_data = analysis_data
        
        # Configure window
        self.geometry("200x80+100+100")
        self.attributes("-topmost", True)
        self.attributes("-alpha", settings.get('overlay_opacity', 0.85))
        self.overrideredirect(True)  # No window decorations
        self.configure(fg_color="#1a1a2e")
        
        # Make draggable
        self.bind("<Button-1>", self.start_drag)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<Double-Button-1>", self.destroy)  # Double-click to close
        
        self.create_content()
        
        # Auto-close
        auto_close = settings.get('overlay_duration', 8)
        if auto_close > 0:
            self.after(auto_close * 1000, self.destroy)
    
    def create_content(self):
        """Create minimal content"""
        win_rate = self.analysis_data.get('win_probability', 0.5) * 100
        win_color = "#2ecc71" if win_rate > 60 else "#e74c3c" if win_rate < 40 else "#f39c12"
        
        # Win rate only
        win_label = ctk.CTkLabel(
            self,
            text=f"{win_rate:.0f}%",
            font=("Arial Black", 32),
            text_color=win_color
        )
        win_label.pack(expand=True)
        
        # Subtle hint
        hint_label = ctk.CTkLabel(
            self,
            text="Double-click to close",
            font=("Arial", 8),
            text_color="#7f8c8d"
        )
        hint_label.pack(side="bottom", pady=2)
    
    def start_drag(self, event):
        self.x = event.x
        self.y = event.y
    
    def on_drag(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

class MinimalHUD(ctk.CTkToplevel):
    """Minimal HUD - like car dashboard info"""
    
    def __init__(self, parent, analysis_data, settings):
        super().__init__(parent)
        
        self.analysis_data = analysis_data
        
        # Configure window - top-right corner
        screen_width = self.winfo_screenwidth()
        self.geometry(f"250x60+{screen_width-270}+20")
        self.attributes("-topmost", True)
        self.attributes("-alpha", settings.get('overlay_opacity', 0.8))
        self.overrideredirect(True)
        self.configure(fg_color="#000000")
        
        # Make draggable
        self.bind("<Button-1>", self.start_drag)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<Double-Button-1>", self.destroy)
        
        self.create_content()
        
        # Auto-close
        auto_close = settings.get('overlay_duration', 12)
        if auto_close > 0:
            self.after(auto_close * 1000, self.destroy)
    
    def create_content(self):
        """Create HUD content"""
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Left side - win rate
        win_rate = self.analysis_data.get('win_probability', 0.5) * 100
        win_color = "#00ff00" if win_rate > 60 else "#ff0000" if win_rate < 40 else "#ffff00"
        
        win_label = ctk.CTkLabel(
            main_frame,
            text=f"{win_rate:.0f}%",
            font=("Arial Black", 24),
            text_color=win_color
        )
        win_label.pack(side="left", padx=(10, 5))
        
        # Right side - key info
        info_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        info_frame.pack(side="right", fill="both", expand=True)
        
        # Priority item
        item_priorities = self.analysis_data.get('item_priorities', [])
        if item_priorities:
            item_text = item_priorities[0].split(' - ')[0].replace('🔥 ', '')
            if len(item_text) > 20:
                item_text = item_text[:17] + "..."
            
            item_label = ctk.CTkLabel(
                info_frame,
                text=item_text,
                font=("Arial", 10),
                text_color="#00ffff"
            )
            item_label.pack(anchor="e", pady=(5, 0))
        
        # Status
        status_label = ctk.CTkLabel(
            info_frame,
            text="ASSAULT BRAIN",
            font=("Arial", 8),
            text_color="#888888"
        )
        status_label.pack(anchor="e", pady=(0, 5))
    
    def start_drag(self, event):
        self.x = event.x
        self.y = event.y
    
    def on_drag(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

class QuickPopup(ctk.CTkToplevel):
    """Quick popup message"""
    
    def __init__(self, parent, message):
        super().__init__(parent)
        
        # Configure window
        self.geometry("350x200")
        self.attributes("-topmost", True)
        self.title("Analysis Complete")
        self.resizable(False, False)
        
        # Center on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
        
        self.create_content(message)
        
        # Auto-close after 4 seconds
        self.after(4000, self.destroy)
    
    def create_content(self, message):
        """Create popup content"""
        # Icon
        icon_label = ctk.CTkLabel(
            self,
            text="⚔️",
            font=("Arial", 48),
            text_color="#f39c12"
        )
        icon_label.pack(pady=(20, 10))
        
        # Message
        message_label = ctk.CTkLabel(
            self,
            text=message,
            font=("Arial", 14),
            text_color="#ecf0f1",
            justify="center"
        )
        message_label.pack(pady=10, padx=20)
        
        # Close button
        close_btn = ctk.CTkButton(
            self,
            text="OK",
            command=self.destroy,
            width=100,
            height=35,
            font=("Arial", 12, "bold"),
            fg_color="#3498db",
            hover_color="#2980b9"
        )
        close_btn.pack(pady=(10, 20))

class DisplaySettingsDialog(ctk.CTkToplevel):
    """Advanced display settings dialog"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.parent = parent
        self.title("Display Settings")
        self.geometry("500x600")
        self.resizable(False, False)
        
        # Center dialog
        self.transient(parent)
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create settings widgets"""
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="🖥️ Display Settings",
            font=("Arial Black", 20),
            text_color="#f39c12"
        )
        title_label.pack(pady=20)
        
        # Settings frame
        settings_frame = ctk.CTkScrollableFrame(self)
        settings_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Display mode
        mode_frame = ctk.CTkFrame(settings_frame, fg_color="#16213e", corner_radius=10)
        mode_frame.pack(fill="x", pady=10)
        
        mode_title = ctk.CTkLabel(
            mode_frame,
            text="Display Mode",
            font=("Arial", 16, "bold"),
            text_color="#f39c12"
        )
        mode_title.pack(pady=(15, 10))
        
        self.mode_var = ctk.StringVar(value=self.parent.settings.get('display_mode', 'Desktop Overlay'))
        
        modes = [
            ("Desktop Overlay", "Full overlay with all information"),
            ("Quick Popup", "Simple popup message"),
            ("System Notification", "Windows toast notification"),
            ("Minimal HUD", "Car dashboard style HUD"),
            ("Voice Only", "Audio feedback only"),
            ("Silent Mode", "No visual display")
        ]
        
        for mode, description in modes:
            mode_radio = ctk.CTkRadioButton(
                mode_frame,
                text=f"{mode} - {description}",
                variable=self.mode_var,
                value=mode,
                font=("Arial", 12),
                text_color="#ecf0f1"
            )
            mode_radio.pack(anchor="w", padx=20, pady=2)
        
        mode_frame.pack_configure(pady=(0, 15))
        
        # Overlay style (for overlay modes)
        style_frame = ctk.CTkFrame(settings_frame, fg_color="#16213e", corner_radius=10)
        style_frame.pack(fill="x", pady=10)
        
        style_title = ctk.CTkLabel(
            style_frame,
            text="Overlay Style",
            font=("Arial", 16, "bold"),
            text_color="#f39c12"
        )
        style_title.pack(pady=(15, 10))
        
        self.style_var = ctk.StringVar(value=self.parent.settings.get('overlay_style', 'Standard'))
        
        styles = [
            ("Standard", "Full information display"),
            ("Compact", "Essential information only"),
            ("Minimal", "Win rate only")
        ]
        
        for style, description in styles:
            style_radio = ctk.CTkRadioButton(
                style_frame,
                text=f"{style} - {description}",
                variable=self.style_var,
                value=style,
                font=("Arial", 12),
                text_color="#ecf0f1"
            )
            style_radio.pack(anchor="w", padx=20, pady=2)
        
        style_frame.pack_configure(pady=(0, 15))
        
        # Opacity slider
        opacity_frame = ctk.CTkFrame(settings_frame, fg_color="#16213e", corner_radius=10)
        opacity_frame.pack(fill="x", pady=10)
        
        opacity_title = ctk.CTkLabel(
            opacity_frame,
            text="Overlay Opacity",
            font=("Arial", 16, "bold"),
            text_color="#f39c12"
        )
        opacity_title.pack(pady=(15, 10))
        
        self.opacity_slider = ctk.CTkSlider(
            opacity_frame,
            from_=0.3,
            to=1.0,
            button_color="#f39c12",
            progress_color="#f39c12"
        )
        self.opacity_slider.set(self.parent.settings.get('overlay_opacity', 0.95))
        self.opacity_slider.pack(padx=20, pady=10)
        
        self.opacity_label = ctk.CTkLabel(
            opacity_frame,
            text=f"{int(self.opacity_slider.get() * 100)}%",
            font=("Arial", 12),
            text_color="#95a5a6"
        )
        self.opacity_label.pack(pady=(0, 15))
        
        # Duration slider
        duration_frame = ctk.CTkFrame(settings_frame, fg_color="#16213e", corner_radius=10)
        duration_frame.pack(fill="x", pady=10)
        
        duration_title = ctk.CTkLabel(
            duration_frame,
            text="Auto-Close Duration (seconds)",
            font=("Arial", 16, "bold"),
            text_color="#f39c12"
        )
        duration_title.pack(pady=(15, 10))
        
        self.duration_slider = ctk.CTkSlider(
            duration_frame,
            from_=0,
            to=30,
            button_color="#f39c12",
            progress_color="#f39c12"
        )
        self.duration_slider.set(self.parent.settings.get('overlay_duration', 15))
        self.duration_slider.pack(padx=20, pady=10)
        
        self.duration_label = ctk.CTkLabel(
            duration_frame,
            text=f"{int(self.duration_slider.get())}s (0 = manual close)",
            font=("Arial", 12),
            text_color="#95a5a6"
        )
        self.duration_label.pack(pady=(0, 15))
        
        # Update labels when sliders change
        self.opacity_slider.configure(command=self.update_opacity_label)
        self.duration_slider.configure(command=self.update_duration_label)
        
        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=20)
        
        test_btn = ctk.CTkButton(
            button_frame,
            text="🔍 Test Display",
            command=self.test_display,
            width=120,
            height=40,
            font=("Arial", 12, "bold"),
            fg_color="#9b59b6",
            hover_color="#8e44ad"
        )
        test_btn.grid(row=0, column=0, padx=10)
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="💾 Save",
            command=self.save_settings,
            width=120,
            height=40,
            font=("Arial", 12, "bold"),
            fg_color="#27ae60",
            hover_color="#229954"
        )
        save_btn.grid(row=0, column=1, padx=10)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            width=120,
            height=40,
            font=("Arial", 12, "bold"),
            fg_color="#7f8c8d",
            hover_color="#5d6d7e"
        )
        cancel_btn.grid(row=0, column=2, padx=10)
    
    def update_opacity_label(self, value):
        """Update opacity label"""
        self.opacity_label.configure(text=f"{int(float(value) * 100)}%")
    
    def update_duration_label(self, value):
        """Update duration label"""
        duration = int(float(value))
        text = f"{duration}s" if duration > 0 else "Manual close"
        self.duration_label.configure(text=text)
    
    def test_display(self):
        """Test current display settings"""
        # Create test analysis data
        test_analysis = {
            'win_probability': 0.67,
            'key_advice': ['Focus on team positioning and buy anti-heal items'],
            'item_priorities': [
                '🔥 Divine Ruin (2600g) - Priority 10',
                '🔥 Meditation Cloak (0g) - Priority 9'
            ]
        }
        
        # Create test settings
        test_settings = {
            'display_mode': self.mode_var.get(),
            'overlay_style': self.style_var.get(),
            'overlay_opacity': self.opacity_slider.get(),
            'overlay_duration': self.duration_slider.get()
        }
        
        # Show test display
        display_manager = DisplayManager(self.parent)
        display_manager.show_analysis(test_analysis, test_settings)
    
    def save_settings(self):
        """Save display settings"""
        self.parent.settings['display_mode'] = self.mode_var.get()
        self.parent.settings['overlay_style'] = self.style_var.get()
        self.parent.settings['overlay_opacity'] = self.opacity_slider.get()
        self.parent.settings['overlay_duration'] = self.duration_slider.get()
        
        self.parent.save_settings()
        messagebox.showinfo("Settings Saved", "Display settings have been saved!")
        self.destroy()

def main():
    """Test display options"""
    print("🖥️ Display Options Test")
    
    # Create test data
    test_analysis = {
        'win_probability': 0.73,
        'key_advice': ['Buy anti-heal immediately - they have Aphrodite and Ra'],
        'item_priorities': [
            '🔥 Divine Ruin (2600g) - Priority 10',
            '🔥 Brawler\'s Beat Stick (2300g) - Priority 10',
            '🔥 Meditation Cloak (0g) - Priority 9'
        ]
    }
    
    test_settings = {
        'display_mode': 'Desktop Overlay',
        'overlay_style': 'Standard',
        'overlay_opacity': 0.95,
        'overlay_duration': 15
    }
    
    # Create test app
    app = ctk.CTk()
    app.geometry("400x300")
    app.title("Display Test")
    
    # Test button
    def test_display():
        display_manager = DisplayManager(app)
        display_manager.show_analysis(test_analysis, test_settings)
    
    test_btn = ctk.CTkButton(
        app,
        text="Test Display",
        command=test_display,
        width=200,
        height=50,
        font=("Arial", 16)
    )
    test_btn.pack(expand=True)
    
    app.mainloop()

if __name__ == "__main__":
    main()