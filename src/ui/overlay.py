"""
Smooth, thematic overlay UI for SMITE 2 Assault Brain
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, Any, Optional, List
import math
import time
from .themes import UIThemes, get_theme_styles, get_god_role_colors, get_animation_config
from .animations import AnimatedWidget, AnimationManager, SmoothProgressBar

logger = logging.getLogger(__name__)

class AssaultOverlay(tk.Toplevel, AnimatedWidget):
    """Main overlay window with smooth animations and thematic design"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        AnimatedWidget.__init__(self)
        
        self.config = config
        self.theme_name = config.get('theme', 'divine_dark')
        self.theme = getattr(UIThemes, self.theme_name.upper(), UIThemes.DIVINE_DARK)
        self.styles = get_theme_styles(self.theme)
        self.role_colors = get_god_role_colors(self.theme)
        self.animation_config = get_animation_config()
        
        # State tracking
        self.current_analysis = None
        self.current_builds = None
        self.is_visible = True
        self.last_update_time = 0
        
        # Animation states
        self.fade_animation_id = None
        self.pulse_animation_id = None
        
        self._setup_window()
        self._create_widgets()
        self._setup_bindings()
        
        logger.info(f"Assault overlay initialized with theme: {self.theme_name}")
        
    def _setup_window(self):
        """Configure the overlay window with smooth styling"""
        # Window properties
        self.title("SMITE 2 Assault Brain")
        self.wm_attributes('-topmost', True)
        self.wm_attributes('-alpha', self.config.get('overlay_opacity', 0.85))
        
        # Remove window decorations for clean overlay look
        self.overrideredirect(True)
        
        # Configure window styling
        self.configure(**self.styles['overlay_window'])
        
        # Position and size
        self._calculate_position()
        
        # Make window click-through in some areas (advanced feature)
        self._setup_click_through()
        
    def _calculate_position(self):
        """Calculate optimal overlay position"""
        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Overlay dimensions
        overlay_width = 420
        overlay_height = 350
        
        # Position based on config
        position = self.config.get('overlay_position', 'top-right')
        margin = 20
        
        if position == 'top-right':
            x = screen_width - overlay_width - margin
            y = margin
        elif position == 'top-left':
            x = margin
            y = margin
        elif position == 'bottom-right':
            x = screen_width - overlay_width - margin
            y = screen_height - overlay_height - margin
        elif position == 'bottom-left':
            x = margin
            y = screen_height - overlay_height - margin
        else:
            # Center
            x = (screen_width - overlay_width) // 2
            y = (screen_height - overlay_height) // 2
            
        self.geometry(f'{overlay_width}x{overlay_height}+{x}+{y}')
        
    def _setup_click_through(self):
        """Setup click-through behavior for non-interactive areas"""
        # This is a simplified implementation
        # In practice, you'd use platform-specific APIs for true click-through
        pass
        
    def _create_widgets(self):
        """Create all overlay widgets with smooth styling"""
        # Main container with rounded corners effect
        self.main_frame = tk.Frame(self, **self.styles['main_frame'])
        self.main_frame.pack(fill='both', expand=True, padx=3, pady=3)
        
        # Header section
        self._create_header()
        
        # Win probability section
        self._create_win_probability_section()
        
        # Analysis section
        self._create_analysis_section()
        
        # Build suggestion section
        self._create_build_section()
        
        # Footer with controls
        self._create_footer()
        
    def _create_header(self):
        """Create animated header with SMITE branding"""
        header_frame = tk.Frame(self.main_frame, **self.styles['card_frame'])
        header_frame.pack(fill='x', pady=(0, 8))
        
        # Title with gradient effect (simulated)
        title_frame = tk.Frame(header_frame, bg=self.theme.surface)
        title_frame.pack(fill='x', padx=10, pady=8)
        
        # Main title
        self.title_label = tk.Label(
            title_frame,
            text="⚔️ ASSAULT BRAIN",
            **self.styles['title_large']
        )
        self.title_label.pack()
        
        # Subtitle with status
        self.status_label = tk.Label(
            title_frame,
            text="Analyzing battlefield...",
            **self.styles['body_small']
        )
        self.status_label.pack()
        
        # Animated status indicator
        self.status_indicator = tk.Canvas(
            title_frame,
            width=12, height=12,
            bg=self.theme.surface,
            highlightthickness=0
        )
        self.status_indicator.pack(pady=2)
        self._animate_status_indicator()
        
    def _create_win_probability_section(self):
        """Create win probability display with smooth progress bar"""
        prob_frame = tk.Frame(self.main_frame, **self.styles['card_frame'])
        prob_frame.pack(fill='x', pady=(0, 8))
        
        # Section title
        prob_title = tk.Label(
            prob_frame,
            text="🎯 WIN PROBABILITY",
            **self.styles['title_small']
        )
        prob_title.pack(pady=(8, 4))
        
        # Probability display
        self.prob_label = tk.Label(
            prob_frame,
            text="Calculating...",
            **self.styles['win_probability_medium']
        )
        self.prob_label.pack(pady=4)
        
        # Smooth progress bar
        self.prob_progress = SmoothProgressBar(
            prob_frame,
            width=300, height=8,
            bg=self.theme.background,
            highlightthickness=0
        )
        self.prob_progress.pack(pady=(4, 8))
        
    def _create_analysis_section(self):
        """Create team analysis section with smooth scrolling"""
        analysis_frame = tk.Frame(self.main_frame, **self.styles['card_frame'])
        analysis_frame.pack(fill='both', expand=True, pady=(0, 8))
        
        # Section title
        analysis_title = tk.Label(
            analysis_frame,
            text="📊 TEAM ANALYSIS",
            **self.styles['title_small']
        )
        analysis_title.pack(pady=(8, 4))
        
        # Scrollable text area with custom styling
        text_frame = tk.Frame(analysis_frame, bg=self.theme.surface)
        text_frame.pack(fill='both', expand=True, padx=8, pady=(0, 8))
        
        # Custom scrollbar
        scrollbar = tk.Scrollbar(text_frame, **self.styles['scrollbar'])
        scrollbar.pack(side='right', fill='y')
        
        # Analysis text widget
        self.analysis_text = tk.Text(
            text_frame,
            height=6,
            width=45,
            yscrollcommand=scrollbar.set,
            **self.styles['text_widget']
        )
        self.analysis_text.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.analysis_text.yview)
        
        # Configure text tags for colored output
        self._configure_text_tags()
        
    def _create_build_section(self):
        """Create build suggestion section"""
        build_frame = tk.Frame(self.main_frame, **self.styles['card_frame'])
        build_frame.pack(fill='x', pady=(0, 8))
        
        # Section title
        build_title = tk.Label(
            build_frame,
            text="🛡️ BUILD TIPS",
            **self.styles['title_small']
        )
        build_title.pack(pady=(8, 4))
        
        # Build suggestion label
        self.build_label = tk.Label(
            build_frame,
            text="",
            **self.styles['body_text'],
            wraplength=380,
            justify='left'
        )
        self.build_label.pack(pady=(0, 8), padx=8)
        
    def _create_footer(self):
        """Create footer with controls and theme toggle"""
        footer_frame = tk.Frame(self.main_frame, bg=self.theme.surface)
        footer_frame.pack(fill='x')
        
        # Control buttons
        controls_frame = tk.Frame(footer_frame, bg=self.theme.surface)
        controls_frame.pack(side='left', padx=8, pady=4)
        
        # Theme toggle button
        self.theme_btn = tk.Button(
            controls_frame,
            text="🌙",
            command=self._toggle_theme,
            **self.styles['secondary_button'],
            width=3
        )
        self.theme_btn.pack(side='left', padx=2)
        
        # Position cycle button
        self.position_btn = tk.Button(
            controls_frame,
            text="📍",
            command=self._cycle_position,
            **self.styles['secondary_button'],
            width=3
        )
        self.position_btn.pack(side='left', padx=2)
        
        # Minimize button
        self.minimize_btn = tk.Button(
            controls_frame,
            text="➖",
            command=self._toggle_minimize,
            **self.styles['secondary_button'],
            width=3
        )
        self.minimize_btn.pack(side='left', padx=2)
        
        # Version info
        version_label = tk.Label(
            footer_frame,
            text="v1.0.0",
            **self.styles['body_small']
        )
        version_label.pack(side='right', padx=8, pady=4)
        
    def _configure_text_tags(self):
        """Configure text tags for colored analysis output"""
        self.analysis_text.tag_config('heading', 
                                    foreground=self.theme.primary, 
                                    font=('Segoe UI', 11, 'bold'))
        self.analysis_text.tag_config('strength', 
                                    foreground=self.theme.success, 
                                    font=('Segoe UI', 10))
        self.analysis_text.tag_config('weakness', 
                                    foreground=self.theme.error, 
                                    font=('Segoe UI', 10))
        self.analysis_text.tag_config('neutral', 
                                    foreground=self.theme.text_secondary, 
                                    font=('Segoe UI', 10))
        self.analysis_text.tag_config('highlight', 
                                    foreground=self.theme.accent, 
                                    font=('Segoe UI', 10, 'bold'))
        
        # Role-specific colors
        for role, color in self.role_colors.items():
            self.analysis_text.tag_config(f'role_{role.lower()}', 
                                        foreground=color, 
                                        font=('Segoe UI', 10, 'bold'))
            
    def _setup_bindings(self):
        """Setup event bindings for smooth interactions"""
        # Hover effects
        self._setup_hover_effects()
        
        # Keyboard shortcuts
        self.bind('<Key-F1>', lambda e: self._toggle_visibility())
        self.bind('<Key-F2>', lambda e: self._force_refresh())
        self.bind('<Key-F3>', lambda e: self._cycle_position())
        self.bind('<Key-F4>', lambda e: self._toggle_debug())
        
        # Mouse interactions
        self.bind('<Button-1>', self._on_click)
        self.bind('<B1-Motion>', self._on_drag)
        self.bind('<ButtonRelease-1>', self._on_release)
        
        # Focus management
        self.focus_set()
        
    def _setup_hover_effects(self):
        """Setup smooth hover effects for interactive elements"""
        buttons = [self.theme_btn, self.position_btn, self.minimize_btn]
        
        for button in buttons:
            button.bind('<Enter>', lambda e, b=button: self._on_button_hover(b, True))
            button.bind('<Leave>', lambda e, b=button: self._on_button_hover(b, False))
            
    def _on_button_hover(self, button: tk.Button, entering: bool):
        """Handle smooth button hover animations"""
        if entering:
            # Brighten button
            button.configure(bg=self.theme.secondary)
            self.animation_manager.pulse_color(self.theme.accent, duration=200)
        else:
            # Return to normal
            button.configure(bg=self.styles['secondary_button']['bg'])
            
    def _animate_status_indicator(self):
        """Animate the status indicator with smooth pulsing"""
        def pulse():
            # Create pulsing circle
            self.status_indicator.delete("all")
            
            # Calculate pulse size based on time
            t = time.time() * 2  # Speed multiplier
            size = 4 + 2 * math.sin(t)
            
            # Draw pulsing circle
            x, y = 6, 6
            self.status_indicator.create_oval(
                x - size, y - size, x + size, y + size,
                fill=self.theme.success, outline=""
            )
            
            # Schedule next frame
            self.after(50, pulse)
            
        pulse()
        
    def update_analysis(self, analysis: Dict[str, Any], builds: Dict[str, Any]):
        """Update overlay with new analysis data using smooth animations"""
        self.current_analysis = analysis
        self.current_builds = builds
        
        # Update win probability with animation
        win_prob = analysis.get('win_probability', 0.5)
        self._update_win_probability(win_prob)
        
        # Update analysis text with smooth transitions
        self._update_analysis_text(analysis)
        
        # Update build suggestions
        self._update_build_suggestions(builds)
        
        # Update status
        self.status_label.configure(text="Analysis complete ✓")
        
        # Pulse overlay to indicate update
        self.pulse_color(self.theme.accent, duration=500)
        
        self.last_update_time = time.time()
        
    def _update_win_probability(self, probability: float):
        """Update win probability with smooth animation and color changes"""
        # Animate progress bar
        self.prob_progress.set_progress(probability, animate=True)
        
        # Update text with color coding
        percentage = int(probability * 100)
        
        if probability >= 0.7:
            style_key = 'win_probability_high'
            emoji = "🔥"
        elif probability >= 0.4:
            style_key = 'win_probability_medium'
            emoji = "⚖️"
        else:
            style_key = 'win_probability_low'
            emoji = "⚠️"
            
        self.prob_label.configure(
            text=f"{emoji} {percentage}% WIN CHANCE",
            **self.styles[style_key]
        )
        
    def _update_analysis_text(self, analysis: Dict[str, Any]):
        """Update analysis text with smooth scrolling and colored formatting"""
        # Clear existing text
        self.analysis_text.delete('1.0', tk.END)
        
        # Add strengths
        if analysis.get('team1_strengths'):
            self.analysis_text.insert(tk.END, "💪 STRENGTHS\n", 'heading')
            for strength in analysis['team1_strengths']:
                self.analysis_text.insert(tk.END, f"  ✓ {strength}\n", 'strength')
            self.analysis_text.insert(tk.END, "\n")
            
        # Add weaknesses
        if analysis.get('team1_weaknesses'):
            self.analysis_text.insert(tk.END, "⚠️ WEAKNESSES\n", 'heading')
            for weakness in analysis['team1_weaknesses']:
                self.analysis_text.insert(tk.END, f"  ✗ {weakness}\n", 'weakness')
            self.analysis_text.insert(tk.END, "\n")
            
        # Add key factors
        if analysis.get('key_factors'):
            self.analysis_text.insert(tk.END, "🎯 KEY FACTORS\n", 'heading')
            for factor in analysis['key_factors']:
                self.analysis_text.insert(tk.END, f"  → {factor}\n", 'highlight')
                
        # Smooth scroll to top
        self.analysis_text.see('1.0')
        
    def _update_build_suggestions(self, builds: Dict[str, Any]):
        """Update build suggestions with priority highlighting"""
        if not builds:
            self.build_label.configure(text="No build suggestions available")
            return
            
        # Get first god's build (simplified for MVP)
        first_god = list(builds.keys())[0]
        build = builds[first_god]
        
        if build.get('tips'):
            tip = build['tips'][0]
            
            # Color code based on priority
            if 'ANTIHEAL' in tip.upper():
                color = self.theme.error
                icon = "🚫"
            elif 'BEADS' in tip.upper():
                color = self.theme.warning
                icon = "🔮"
            else:
                color = self.theme.text_primary
                icon = "💡"
                
            self.build_label.configure(
                text=f"{icon} {tip}",
                fg=color
            )
        else:
            self.build_label.configure(text="Build analysis in progress...")
            
    def _toggle_theme(self):
        """Smoothly transition between themes"""
        # Cycle through available themes
        themes = ['divine_dark', 'celestial_light', 'pantheon_contrast']
        current_index = themes.index(self.theme_name)
        new_theme_name = themes[(current_index + 1) % len(themes)]
        
        # Update theme
        self.theme_name = new_theme_name
        self.theme = getattr(UIThemes, new_theme_name.upper())
        self.styles = get_theme_styles(self.theme)
        self.role_colors = get_god_role_colors(self.theme)
        
        # Animate theme transition
        self.fade_out(duration=150, callback=lambda: self._apply_new_theme())
        
    def _apply_new_theme(self):
        """Apply new theme to all widgets"""
        # Update all widget styles
        self.configure(**self.styles['overlay_window'])
        self.main_frame.configure(**self.styles['main_frame'])
        
        # Update text tags
        self._configure_text_tags()
        
        # Re-apply current analysis with new colors
        if self.current_analysis:
            self._update_analysis_text(self.current_analysis)
            
        # Fade back in
        self.fade_in(duration=150)
        
        logger.info(f"Theme changed to: {self.theme_name}")
        
    def _cycle_position(self):
        """Smoothly move overlay to next position"""
        positions = ['top-right', 'top-left', 'bottom-left', 'bottom-right']
        current_pos = self.config.get('overlay_position', 'top-right')
        
        try:
            current_index = positions.index(current_pos)
            new_position = positions[(current_index + 1) % len(positions)]
        except ValueError:
            new_position = 'top-right'
            
        self.config['overlay_position'] = new_position
        
        # Animate to new position
        self.slide_in_from_right(duration=300)
        self._calculate_position()
        
    def _toggle_minimize(self):
        """Toggle minimized state with smooth animation"""
        if hasattr(self, '_minimized') and self._minimized:
            # Restore
            self.fade_in(duration=200)
            self._minimized = False
            self.minimize_btn.configure(text="➖")
        else:
            # Minimize
            self.fade_out(duration=200)
            self._minimized = True
            self.minimize_btn.configure(text="➕")
            
    def _toggle_visibility(self):
        """Toggle overlay visibility"""
        if self.is_visible:
            self.fade_out(duration=200, callback=self.withdraw)
            self.is_visible = False
        else:
            self.deiconify()
            self.fade_in(duration=200)
            self.is_visible = True
            
    def _force_refresh(self):
        """Force refresh analysis"""
        self.status_label.configure(text="Refreshing analysis...")
        self.pulse_color(self.theme.secondary, duration=300)
        
    def _toggle_debug(self):
        """Toggle debug mode"""
        debug_mode = not self.config.get('debug_mode', False)
        self.config['debug_mode'] = debug_mode
        
        if debug_mode:
            self.status_label.configure(text="Debug mode enabled")
        else:
            self.status_label.configure(text="Debug mode disabled")
            
    def _on_click(self, event):
        """Handle mouse click for dragging"""
        self.start_x = event.x
        self.start_y = event.y
        
    def _on_drag(self, event):
        """Handle window dragging"""
        x = self.winfo_x() + (event.x - self.start_x)
        y = self.winfo_y() + (event.y - self.start_y)
        self.geometry(f"+{x}+{y}")
        
    def _on_release(self, event):
        """Handle mouse release"""
        pass
        
    def clear(self):
        """Clear overlay content with smooth animation"""
        self.fade_out(duration=150, callback=self._clear_content)
        
    def _clear_content(self):
        """Clear all content"""
        self.prob_label.configure(text="Waiting for match...")
        self.prob_progress.set_progress(0, animate=False)
        self.analysis_text.delete('1.0', tk.END)
        self.build_label.configure(text="")
        self.status_label.configure(text="Monitoring for games...")
        
        self.fade_in(duration=150)
        
    def show(self):
        """Show overlay with entrance animation"""
        self.deiconify()
        self.slide_in_from_right(duration=400)
        self.is_visible = True
        
    def hide(self):
        """Hide overlay with exit animation"""
        self.fade_out(duration=300, callback=self.withdraw)
        self.is_visible = False
        
    def destroy(self):
        """Clean up and destroy overlay"""
        self.animation_manager.stop_all_animations()
        super().destroy()