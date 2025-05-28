"""
Thematic UI styling for SMITE 2 Assault Brain
"""

from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class ColorScheme:
    """Color scheme for UI themes"""
    primary: str
    secondary: str
    accent: str
    background: str
    surface: str
    text_primary: str
    text_secondary: str
    success: str
    warning: str
    error: str
    overlay_bg: str
    border: str
    shadow: str

class UIThemes:
    """Collection of UI themes for the application"""
    
    # SMITE-inspired Dark Theme (Default)
    DIVINE_DARK = ColorScheme(
        primary="#FFD700",        # Divine Gold
        secondary="#4A90E2",      # Mystic Blue
        accent="#FF6B35",         # Phoenix Orange
        background="#0A0A0A",     # Deep Black
        surface="#1A1A1A",       # Dark Surface
        text_primary="#FFFFFF",   # Pure White
        text_secondary="#B0B0B0", # Light Gray
        success="#00FF88",        # Victory Green
        warning="#FFB347",        # Caution Orange
        error="#FF4444",          # Defeat Red
        overlay_bg="#000000CC",   # Semi-transparent black
        border="#333333",         # Dark Border
        shadow="#00000080"        # Shadow
    )
    
    # Light Theme for accessibility
    CELESTIAL_LIGHT = ColorScheme(
        primary="#1E3A8A",        # Royal Blue
        secondary="#7C3AED",      # Purple
        accent="#DC2626",         # Red
        background="#F8FAFC",     # Light Gray
        surface="#FFFFFF",        # White
        text_primary="#1F2937",   # Dark Gray
        text_secondary="#6B7280", # Medium Gray
        success="#059669",        # Green
        warning="#D97706",        # Orange
        error="#DC2626",          # Red
        overlay_bg="#FFFFFFCC",   # Semi-transparent white
        border="#E5E7EB",         # Light Border
        shadow="#00000020"        # Light Shadow
    )
    
    # High contrast theme
    PANTHEON_CONTRAST = ColorScheme(
        primary="#00FFFF",        # Cyan
        secondary="#FF00FF",      # Magenta
        accent="#FFFF00",         # Yellow
        background="#000000",     # Black
        surface="#111111",        # Very Dark Gray
        text_primary="#FFFFFF",   # White
        text_secondary="#CCCCCC", # Light Gray
        success="#00FF00",        # Bright Green
        warning="#FFA500",        # Orange
        error="#FF0000",          # Bright Red
        overlay_bg="#000000DD",   # Dark overlay
        border="#FFFFFF",         # White Border
        shadow="#FFFFFF40"        # Light Shadow
    )

def get_theme_styles(theme: ColorScheme) -> Dict[str, Any]:
    """Generate complete style dictionary for a theme"""
    return {
        # Main window styles
        'main_window': {
            'bg': theme.background,
            'fg': theme.text_primary,
            'relief': 'flat',
            'bd': 0
        },
        
        # Overlay window styles
        'overlay_window': {
            'bg': theme.overlay_bg,
            'fg': theme.text_primary,
            'relief': 'flat',
            'bd': 0
        },
        
        # Frame styles
        'main_frame': {
            'bg': theme.surface,
            'fg': theme.text_primary,
            'relief': 'flat',
            'bd': 2,
            'highlightbackground': theme.border,
            'highlightthickness': 1
        },
        
        'card_frame': {
            'bg': theme.surface,
            'fg': theme.text_primary,
            'relief': 'raised',
            'bd': 1,
            'highlightbackground': theme.border,
            'highlightthickness': 1
        },
        
        # Text styles
        'title_large': {
            'font': ('Segoe UI', 20, 'bold'),
            'fg': theme.primary,
            'bg': theme.surface
        },
        
        'title_medium': {
            'font': ('Segoe UI', 16, 'bold'),
            'fg': theme.primary,
            'bg': theme.surface
        },
        
        'title_small': {
            'font': ('Segoe UI', 14, 'bold'),
            'fg': theme.text_primary,
            'bg': theme.surface
        },
        
        'body_text': {
            'font': ('Segoe UI', 11),
            'fg': theme.text_primary,
            'bg': theme.surface
        },
        
        'body_small': {
            'font': ('Segoe UI', 10),
            'fg': theme.text_secondary,
            'bg': theme.surface
        },
        
        'monospace': {
            'font': ('Consolas', 10),
            'fg': theme.text_primary,
            'bg': theme.surface
        },
        
        # Status text colors
        'success_text': {
            'font': ('Segoe UI', 12, 'bold'),
            'fg': theme.success,
            'bg': theme.surface
        },
        
        'warning_text': {
            'font': ('Segoe UI', 12, 'bold'),
            'fg': theme.warning,
            'bg': theme.surface
        },
        
        'error_text': {
            'font': ('Segoe UI', 12, 'bold'),
            'fg': theme.error,
            'bg': theme.surface
        },
        
        # Button styles
        'primary_button': {
            'font': ('Segoe UI', 11, 'bold'),
            'fg': theme.background,
            'bg': theme.primary,
            'activeforeground': theme.background,
            'activebackground': theme.secondary,
            'relief': 'flat',
            'bd': 0,
            'padx': 20,
            'pady': 8,
            'cursor': 'hand2'
        },
        
        'secondary_button': {
            'font': ('Segoe UI', 11),
            'fg': theme.text_primary,
            'bg': theme.surface,
            'activeforeground': theme.text_primary,
            'activebackground': theme.border,
            'relief': 'flat',
            'bd': 1,
            'highlightbackground': theme.border,
            'padx': 15,
            'pady': 6,
            'cursor': 'hand2'
        },
        
        # Input styles
        'entry': {
            'font': ('Segoe UI', 11),
            'fg': theme.text_primary,
            'bg': theme.background,
            'insertbackground': theme.text_primary,
            'selectbackground': theme.secondary,
            'selectforeground': theme.text_primary,
            'relief': 'flat',
            'bd': 2,
            'highlightbackground': theme.border,
            'highlightthickness': 1
        },
        
        'text_widget': {
            'font': ('Segoe UI', 10),
            'fg': theme.text_primary,
            'bg': theme.background,
            'insertbackground': theme.text_primary,
            'selectbackground': theme.secondary,
            'selectforeground': theme.text_primary,
            'relief': 'flat',
            'bd': 0,
            'wrap': 'word',
            'padx': 10,
            'pady': 8
        },
        
        # Progress bar styles
        'progress_bar': {
            'style': 'Custom.Horizontal.TProgressbar'
        },
        
        # Scrollbar styles
        'scrollbar': {
            'bg': theme.surface,
            'troughcolor': theme.background,
            'activebackground': theme.secondary,
            'relief': 'flat',
            'bd': 0,
            'width': 12
        },
        
        # Special overlay styles
        'win_probability_high': {
            'font': ('Segoe UI', 16, 'bold'),
            'fg': theme.success,
            'bg': theme.surface
        },
        
        'win_probability_medium': {
            'font': ('Segoe UI', 16, 'bold'),
            'fg': theme.warning,
            'bg': theme.surface
        },
        
        'win_probability_low': {
            'font': ('Segoe UI', 16, 'bold'),
            'fg': theme.error,
            'bg': theme.surface
        },
        
        # Animation colors for smooth transitions
        'animation': {
            'fade_in_color': theme.primary,
            'fade_out_color': theme.background,
            'pulse_color': theme.accent,
            'highlight_color': theme.secondary
        }
    }

def get_god_role_colors(theme: ColorScheme) -> Dict[str, str]:
    """Get colors for different god roles"""
    return {
        'Tank': theme.primary,      # Gold for tanks
        'Warrior': theme.error,     # Red for warriors
        'Mage': theme.secondary,    # Blue for mages
        'Hunter': theme.success,    # Green for hunters
        'Assassin': theme.accent,   # Orange for assassins
        'Support': theme.warning    # Yellow for supports
    }

def get_animation_config() -> Dict[str, Any]:
    """Get animation configuration for smooth UI transitions"""
    return {
        'fade_duration': 300,       # milliseconds
        'slide_duration': 250,      # milliseconds
        'pulse_duration': 1000,     # milliseconds
        'bounce_duration': 400,     # milliseconds
        'easing': 'ease_out',       # easing function
        'fps': 60                   # target FPS for animations
    }