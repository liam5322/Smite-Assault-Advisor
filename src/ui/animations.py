"""
Smooth animation system for UI components
"""

import tkinter as tk
import math
import time
from typing import Callable, Dict, Any, Optional
from threading import Thread
import logging

logger = logging.getLogger(__name__)

class EasingFunctions:
    """Collection of easing functions for smooth animations"""
    
    @staticmethod
    def linear(t: float) -> float:
        return t
    
    @staticmethod
    def ease_in_quad(t: float) -> float:
        return t * t
    
    @staticmethod
    def ease_out_quad(t: float) -> float:
        return 1 - (1 - t) * (1 - t)
    
    @staticmethod
    def ease_in_out_quad(t: float) -> float:
        return 2 * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 2) / 2
    
    @staticmethod
    def ease_out_bounce(t: float) -> float:
        n1 = 7.5625
        d1 = 2.75
        
        if t < 1 / d1:
            return n1 * t * t
        elif t < 2 / d1:
            t -= 1.5 / d1
            return n1 * t * t + 0.75
        elif t < 2.5 / d1:
            t -= 2.25 / d1
            return n1 * t * t + 0.9375
        else:
            t -= 2.625 / d1
            return n1 * t * t + 0.984375
    
    @staticmethod
    def ease_out_elastic(t: float) -> float:
        c4 = (2 * math.pi) / 3
        return 0 if t == 0 else 1 if t == 1 else pow(2, -10 * t) * math.sin((t * 10 - 0.75) * c4) + 1

class AnimationManager:
    """Manages smooth animations for UI components"""
    
    def __init__(self):
        self.active_animations = {}
        self.animation_id_counter = 0
        
    def animate(self, 
                widget: tk.Widget,
                property_name: str,
                start_value: Any,
                end_value: Any,
                duration: int = 300,
                easing: str = 'ease_out_quad',
                callback: Optional[Callable] = None) -> int:
        """Start a smooth animation"""
        
        animation_id = self.animation_id_counter
        self.animation_id_counter += 1
        
        # Get easing function
        easing_func = getattr(EasingFunctions, easing, EasingFunctions.ease_out_quad)
        
        # Store animation info
        self.active_animations[animation_id] = {
            'widget': widget,
            'property': property_name,
            'start_value': start_value,
            'end_value': end_value,
            'duration': duration,
            'easing_func': easing_func,
            'callback': callback,
            'start_time': time.time() * 1000,  # Convert to milliseconds
            'active': True
        }
        
        # Start animation loop
        self._animate_step(animation_id)
        
        return animation_id
    
    def _animate_step(self, animation_id: int):
        """Execute one step of animation"""
        if animation_id not in self.active_animations:
            return
            
        anim = self.active_animations[animation_id]
        if not anim['active']:
            return
            
        current_time = time.time() * 1000
        elapsed = current_time - anim['start_time']
        progress = min(elapsed / anim['duration'], 1.0)
        
        # Apply easing
        eased_progress = anim['easing_func'](progress)
        
        # Calculate current value
        if isinstance(anim['start_value'], (int, float)):
            # Numeric interpolation
            current_value = anim['start_value'] + (anim['end_value'] - anim['start_value']) * eased_progress
        elif isinstance(anim['start_value'], str) and anim['start_value'].startswith('#'):
            # Color interpolation
            current_value = self._interpolate_color(anim['start_value'], anim['end_value'], eased_progress)
        else:
            # Direct value assignment for non-interpolatable types
            current_value = anim['end_value'] if progress >= 1.0 else anim['start_value']
        
        # Apply value to widget
        try:
            if anim['property'] == 'alpha':
                # Special handling for transparency
                self._set_widget_alpha(anim['widget'], current_value)
            elif anim['property'] == 'geometry':
                # Special handling for position/size
                anim['widget'].geometry(current_value)
            else:
                # Standard property setting
                anim['widget'].config(**{anim['property']: current_value})
        except tk.TclError:
            # Widget was destroyed
            self.stop_animation(animation_id)
            return
        
        # Continue or finish animation
        if progress >= 1.0:
            self.stop_animation(animation_id)
            if anim['callback']:
                anim['callback']()
        else:
            # Schedule next frame
            anim['widget'].after(16, lambda: self._animate_step(animation_id))  # ~60 FPS
    
    def _interpolate_color(self, start_color: str, end_color: str, progress: float) -> str:
        """Interpolate between two hex colors"""
        # Remove # and convert to RGB
        start_rgb = tuple(int(start_color[i:i+2], 16) for i in (1, 3, 5))
        end_rgb = tuple(int(end_color[i:i+2], 16) for i in (1, 3, 5))
        
        # Interpolate each channel
        current_rgb = tuple(
            int(start_rgb[i] + (end_rgb[i] - start_rgb[i]) * progress)
            for i in range(3)
        )
        
        # Convert back to hex
        return f"#{current_rgb[0]:02x}{current_rgb[1]:02x}{current_rgb[2]:02x}"
    
    def _set_widget_alpha(self, widget: tk.Widget, alpha: float):
        """Set widget transparency (if supported)"""
        try:
            # This works for toplevel windows
            if hasattr(widget, 'wm_attributes'):
                widget.wm_attributes('-alpha', alpha)
        except tk.TclError:
            pass
    
    def stop_animation(self, animation_id: int):
        """Stop a specific animation"""
        if animation_id in self.active_animations:
            self.active_animations[animation_id]['active'] = False
            del self.active_animations[animation_id]
    
    def stop_all_animations(self):
        """Stop all active animations"""
        for animation_id in list(self.active_animations.keys()):
            self.stop_animation(animation_id)

class AnimatedWidget:
    """Mixin class to add animation capabilities to widgets"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.animation_manager = AnimationManager()
        
    def fade_in(self, duration: int = 300, callback: Optional[Callable] = None):
        """Fade in the widget"""
        if hasattr(self, 'wm_attributes'):
            self.wm_attributes('-alpha', 0)
            return self.animation_manager.animate(
                self, 'alpha', 0, 1, duration, 'ease_out_quad', callback
            )
    
    def fade_out(self, duration: int = 300, callback: Optional[Callable] = None):
        """Fade out the widget"""
        if hasattr(self, 'wm_attributes'):
            return self.animation_manager.animate(
                self, 'alpha', 1, 0, duration, 'ease_out_quad', callback
            )
    
    def slide_in_from_right(self, duration: int = 250, callback: Optional[Callable] = None):
        """Slide widget in from the right"""
        if hasattr(self, 'geometry'):
            # Get current geometry
            self.update_idletasks()
            width = self.winfo_width()
            height = self.winfo_height()
            screen_width = self.winfo_screenwidth()
            
            # Start position (off-screen right)
            start_x = screen_width
            end_x = screen_width - width - 20
            y = 20
            
            start_geometry = f"{width}x{height}+{start_x}+{y}"
            end_geometry = f"{width}x{height}+{end_x}+{y}"
            
            self.geometry(start_geometry)
            return self.animation_manager.animate(
                self, 'geometry', start_geometry, end_geometry, duration, 'ease_out_quad', callback
            )
    
    def pulse_color(self, color: str, duration: int = 1000, callback: Optional[Callable] = None):
        """Pulse the widget's background color"""
        original_color = self.cget('bg')
        
        def pulse_back():
            self.animation_manager.animate(
                self, 'bg', color, original_color, duration // 2, 'ease_out_quad', callback
            )
        
        return self.animation_manager.animate(
            self, 'bg', original_color, color, duration // 2, 'ease_out_quad', pulse_back
        )
    
    def bounce_in(self, duration: int = 400, callback: Optional[Callable] = None):
        """Bounce in animation"""
        if hasattr(self, 'wm_attributes'):
            self.wm_attributes('-alpha', 0)
            
            def show_bounce():
                self.animation_manager.animate(
                    self, 'alpha', 0, 1, duration, 'ease_out_bounce', callback
                )
            
            # Small delay before bounce
            self.after(50, show_bounce)

class SmoothProgressBar:
    """Smooth animated progress bar"""
    
    def __init__(self, parent, width=200, height=20, **kwargs):
        self.canvas = tk.Canvas(parent, width=width, height=height, **kwargs)
        self.width = width
        self.height = height
        self.progress = 0.0
        self.target_progress = 0.0
        self.animation_manager = AnimationManager()
        
        # Draw initial progress bar
        self._draw_progress_bar()
    
    def _draw_progress_bar(self):
        """Draw the progress bar"""
        self.canvas.delete("all")
        
        # Background
        self.canvas.create_rectangle(
            0, 0, self.width, self.height,
            fill="#333333", outline="#555555", width=1
        )
        
        # Progress fill
        fill_width = self.width * self.progress
        if fill_width > 0:
            # Gradient effect (simplified)
            color = self._get_progress_color(self.progress)
            self.canvas.create_rectangle(
                0, 0, fill_width, self.height,
                fill=color, outline=""
            )
    
    def _get_progress_color(self, progress: float) -> str:
        """Get color based on progress value"""
        if progress < 0.3:
            return "#FF4444"  # Red
        elif progress < 0.7:
            return "#FFB347"  # Orange
        else:
            return "#00FF88"  # Green
    
    def set_progress(self, value: float, animate: bool = True):
        """Set progress value with optional animation"""
        self.target_progress = max(0.0, min(1.0, value))
        
        if animate:
            self.animation_manager.animate(
                self, 'progress', self.progress, self.target_progress,
                duration=500, easing='ease_out_quad',
                callback=self._draw_progress_bar
            )
        else:
            self.progress = self.target_progress
            self._draw_progress_bar()
    
    def pack(self, **kwargs):
        """Pack the canvas"""
        self.canvas.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the canvas"""
        self.canvas.grid(**kwargs)