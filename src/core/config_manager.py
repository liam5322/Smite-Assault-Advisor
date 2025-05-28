"""
Configuration management with hardware-adaptive settings
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from .hardware_detector import HardwareDetector, PerformanceTier

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages application configuration with hardware adaptation"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path(__file__).parent.parent.parent / 'config' / 'settings.yaml'
        self.hardware_detector = HardwareDetector()
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration with hardware-adaptive defaults"""
        # Get hardware-recommended config
        recommended_config = self.hardware_detector.get_recommended_config()
        
        # Default configuration
        default_config = {
            # Hardware-adaptive settings
            'performance_tier': self.hardware_detector.recommended_tier.value,
            'ocr_engine': recommended_config['ocr_engine'],
            'gpu_acceleration': recommended_config['gpu_acceleration'],
            'update_rate': recommended_config['update_rate'],
            'image_scale': recommended_config['image_scale'],
            'max_threads': recommended_config['max_threads'],
            'cache_size': recommended_config['cache_size'],
            
            # Display settings
            'monitor': 1,
            'overlay_position': 'top-right',
            'overlay_opacity': 0.85,
            'overlay_scale': 1.0,
            'auto_hide_in_menu': True,
            
            # Game-specific settings
            'resolution': '1920x1080',
            'ocr_confidence': 0.7,
            'fuzzy_match_threshold': 80,
            
            # Feature toggles (hardware-dependent)
            'features': recommended_config['features'],
            
            # Advanced settings
            'debug_mode': False,
            'save_screenshots': False,
            'log_level': 'INFO',
            
            # Hotkeys
            'hotkeys': {
                'toggle_overlay': 'F1',
                'force_scan': 'F2',
                'cycle_position': 'F3',
                'toggle_debug': 'F4'
            },
            
            # OCR regions (will be auto-adjusted for resolution)
            'ocr_regions': {
                'loading_team1': {'x': 50, 'y': 200, 'width': 400, 'height': 600},
                'loading_team2': {'x': 1470, 'y': 200, 'width': 400, 'height': 600},
                'loading_indicator': {'x': 860, 'y': 50, 'width': 200, 'height': 100},
                'tab_items': {'x': 300, 'y': 200, 'width': 1320, 'height': 600}
            }
        }
        
        # Load user configuration if exists
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    user_config = yaml.safe_load(f) or {}
                    
                # Merge user config with defaults
                default_config.update(user_config)
                logger.info("Loaded user configuration")
                
            except Exception as e:
                logger.warning(f"Failed to load user config: {e}, using defaults")
                
        # Validate and adjust config for current hardware
        self._validate_config(default_config)
        
        return default_config
        
    def _validate_config(self, config: Dict[str, Any]):
        """Validate configuration against current hardware"""
        # Handle auto values
        if config.get('performance_tier') == 'auto':
            config['performance_tier'] = self.hardware_detector.recommended_tier.value
            
        # Check if selected performance tier is viable
        tier = PerformanceTier(config.get('performance_tier', 'standard'))
        validation = self.hardware_detector.validate_dependencies(tier)
        
        if not validation['ocr_engine']:
            logger.warning("Selected OCR engine not available, falling back to tesseract")
            config['ocr_engine'] = 'tesseract'
            
        if config['gpu_acceleration'] and not validation['gpu_support']:
            logger.warning("GPU acceleration requested but not available")
            config['gpu_acceleration'] = False
            
        # Adjust update rate based on system performance
        if self.hardware_detector.system_info['cpu_count'] < 4:
            config['update_rate'] = max(config['update_rate'], 1.5)
            logger.info("Adjusted update rate for lower-end CPU")
            
        # Adjust image scale for memory constraints
        memory_gb = self.hardware_detector.system_info['memory_gb']
        if memory_gb < 8:
            config['image_scale'] = min(config['image_scale'], 0.75)
            logger.info("Reduced image scale for memory constraints")
            
    def save_config(self):
        """Save current configuration to file"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, indent=2)
            logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with dot notation support"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
                
        return value
        
    def set(self, key: str, value: Any):
        """Set configuration value with dot notation support"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
            
        config[keys[-1]] = value
        
    def get_performance_options(self) -> Dict[str, Dict[str, Any]]:
        """Get available performance tier options for user selection"""
        return self.hardware_detector.get_tier_options()
        
    def set_performance_tier(self, tier: str):
        """Change performance tier and update related settings"""
        try:
            new_tier = PerformanceTier(tier)
            recommended_config = self.hardware_detector._get_tier_config(new_tier)
            
            # Update performance-related settings
            self.config['performance_tier'] = tier
            self.config['ocr_engine'] = recommended_config['ocr_engine']
            self.config['gpu_acceleration'] = recommended_config['gpu_acceleration']
            self.config['update_rate'] = recommended_config['update_rate']
            
            # Update features based on tier
            tier_features = {
                'minimal': {
                    'advanced_analysis': False,
                    'voice_output': False,
                    'ml_predictions': False,
                    'real_time_tracking': False
                },
                'standard': {
                    'advanced_analysis': True,
                    'voice_output': False,
                    'ml_predictions': False,
                    'real_time_tracking': True
                },
                'maximum': {
                    'advanced_analysis': True,
                    'voice_output': True,
                    'ml_predictions': True,
                    'real_time_tracking': True
                }
            }
            
            self.config['features'].update(tier_features.get(tier, {}))
            
            logger.info(f"Performance tier changed to: {tier}")
            
        except ValueError:
            logger.error(f"Invalid performance tier: {tier}")
            
    def get_ocr_regions(self) -> Dict[str, Dict[str, int]]:
        """Get OCR regions adjusted for current resolution"""
        regions = self.config['ocr_regions'].copy()
        resolution = self.config['resolution']
        
        # Parse resolution
        try:
            width, height = map(int, resolution.split('x'))
        except ValueError:
            width, height = 1920, 1080  # Default
            
        # Scale regions if not 1920x1080
        if width != 1920 or height != 1080:
            scale_x = width / 1920
            scale_y = height / 1080
            
            for region_name, region in regions.items():
                regions[region_name] = {
                    'x': int(region['x'] * scale_x),
                    'y': int(region['y'] * scale_y),
                    'width': int(region['width'] * scale_x),
                    'height': int(region['height'] * scale_y)
                }
                
        return regions
        
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled and supported by hardware"""
        if not self.config['features'].get(feature, False):
            return False
            
        # Additional hardware checks
        if feature == 'gpu_acceleration':
            return self.hardware_detector.system_info['gpu_available']
        elif feature == 'ml_predictions':
            return self.hardware_detector.can_run_feature('ml_predictions')
        elif feature == 'voice_output':
            return self.hardware_detector.can_run_feature('voice_output')
            
        return True
        
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information for diagnostics"""
        return {
            'hardware': self.hardware_detector.system_info,
            'recommended_tier': self.hardware_detector.recommended_tier.value,
            'current_tier': self.config['performance_tier'],
            'features_enabled': {k: v for k, v in self.config['features'].items() if v},
            'validation': self.hardware_detector.validate_dependencies(
                PerformanceTier(self.config['performance_tier'])
            )
        }