"""
Hardware detection and performance tier selection
"""

import psutil
import platform
import subprocess
import logging
from enum import Enum
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class PerformanceTier(Enum):
    """Performance tiers based on hardware capabilities"""
    MINIMAL = "minimal"      # Low-end systems, CPU-only
    STANDARD = "standard"    # Mid-range systems, some GPU acceleration
    MAXIMUM = "maximum"      # High-end systems, full GPU acceleration

class HardwareDetector:
    """Detects system hardware and recommends optimal configuration"""
    
    def __init__(self):
        self.system_info = self._gather_system_info()
        self.recommended_tier = self._determine_performance_tier()
        
    def _gather_system_info(self) -> Dict[str, Any]:
        """Gather comprehensive system information"""
        info = {
            'cpu_count': psutil.cpu_count(),
            'cpu_freq': psutil.cpu_freq().max if psutil.cpu_freq() else 0,
            'memory_gb': psutil.virtual_memory().total / (1024**3),
            'platform': platform.system(),
            'architecture': platform.architecture()[0],
            'gpu_available': self._detect_gpu(),
            'gpu_memory_gb': self._get_gpu_memory(),
        }
        
        logger.info(f"System detected: {info}")
        return info
        
    def _detect_gpu(self) -> bool:
        """Detect if GPU acceleration is available"""
        try:
            # Try to detect NVIDIA GPU
            result = subprocess.run(['nvidia-smi'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            if result.returncode == 0:
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
            
        try:
            # Try to detect AMD GPU (simplified)
            import torch
            if torch.cuda.is_available():
                return True
        except ImportError:
            pass
            
        return False
        
    def _get_gpu_memory(self) -> float:
        """Get GPU memory in GB"""
        if not self.system_info.get('gpu_available', False):
            return 0.0
            
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=memory.total', '--format=csv,noheader,nounits'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            if result.returncode == 0:
                memory_mb = int(result.stdout.strip())
                return memory_mb / 1024  # Convert to GB
        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
            pass
            
        return 0.0
        
    def _determine_performance_tier(self) -> PerformanceTier:
        """Determine optimal performance tier based on hardware"""
        cpu_count = self.system_info['cpu_count']
        memory_gb = self.system_info['memory_gb']
        gpu_available = self.system_info['gpu_available']
        gpu_memory_gb = self.system_info['gpu_memory_gb']
        
        # High-end system criteria
        if (cpu_count >= 8 and 
            memory_gb >= 16 and 
            gpu_available and 
            gpu_memory_gb >= 4):
            return PerformanceTier.MAXIMUM
            
        # Mid-range system criteria
        elif (cpu_count >= 4 and 
              memory_gb >= 8 and 
              (gpu_available or cpu_count >= 6)):
            return PerformanceTier.STANDARD
            
        # Low-end system
        else:
            return PerformanceTier.MINIMAL
            
    def get_recommended_config(self) -> Dict[str, Any]:
        """Get recommended configuration for detected hardware"""
        configs = {
            PerformanceTier.MINIMAL: {
                'ocr_engine': 'tesseract',
                'gpu_acceleration': False,
                'update_rate': 2.0,  # Slower updates
                'image_scale': 0.5,  # Smaller images
                'max_threads': 2,
                'cache_size': 50,
                'features': {
                    'advanced_analysis': False,
                    'voice_output': False,
                    'ml_predictions': False,
                    'real_time_tracking': False
                }
            },
            PerformanceTier.STANDARD: {
                'ocr_engine': 'easyocr',
                'gpu_acceleration': self.system_info['gpu_available'],
                'update_rate': 1.0,
                'image_scale': 0.75,
                'max_threads': 4,
                'cache_size': 100,
                'features': {
                    'advanced_analysis': True,
                    'voice_output': False,
                    'ml_predictions': False,
                    'real_time_tracking': True
                }
            },
            PerformanceTier.MAXIMUM: {
                'ocr_engine': 'easyocr',
                'gpu_acceleration': True,
                'update_rate': 0.5,  # Fastest updates
                'image_scale': 1.0,  # Full resolution
                'max_threads': 8,
                'cache_size': 200,
                'features': {
                    'advanced_analysis': True,
                    'voice_output': True,
                    'ml_predictions': True,
                    'real_time_tracking': True
                }
            }
        }
        
        return configs[self.recommended_tier]
        
    def can_run_feature(self, feature: str) -> bool:
        """Check if system can run a specific feature"""
        config = self.get_recommended_config()
        return config['features'].get(feature, False)
        
    def get_tier_options(self) -> Dict[str, Dict[str, Any]]:
        """Get all available tier options for user selection"""
        all_configs = {}
        
        for tier in PerformanceTier:
            # Check if tier is viable for this system
            if tier == PerformanceTier.MAXIMUM and not self.system_info['gpu_available']:
                continue  # Skip maximum if no GPU
            if tier == PerformanceTier.STANDARD and self.system_info['memory_gb'] < 4:
                continue  # Skip standard if very low memory
                
            all_configs[tier.value] = self._get_tier_config(tier)
            
        return all_configs
        
    def _get_tier_config(self, tier: PerformanceTier) -> Dict[str, Any]:
        """Get configuration for specific tier"""
        configs = {
            PerformanceTier.MINIMAL: {
                'name': 'Minimal Performance',
                'description': 'Basic functionality for low-end systems',
                'requirements': 'CPU: 2+ cores, RAM: 4+ GB',
                'ocr_engine': 'tesseract',
                'gpu_acceleration': False,
                'update_rate': 2.0,
                'features_enabled': ['basic_analysis', 'simple_overlay']
            },
            PerformanceTier.STANDARD: {
                'name': 'Standard Performance', 
                'description': 'Full functionality with good performance',
                'requirements': 'CPU: 4+ cores, RAM: 8+ GB',
                'ocr_engine': 'easyocr',
                'gpu_acceleration': self.system_info['gpu_available'],
                'update_rate': 1.0,
                'features_enabled': ['advanced_analysis', 'enhanced_overlay', 'real_time_tracking']
            },
            PerformanceTier.MAXIMUM: {
                'name': 'Maximum Performance',
                'description': 'All features with GPU acceleration',
                'requirements': 'CPU: 8+ cores, RAM: 16+ GB, GPU: 4+ GB VRAM',
                'ocr_engine': 'easyocr',
                'gpu_acceleration': True,
                'update_rate': 0.5,
                'features_enabled': ['all_features', 'ml_predictions', 'voice_output']
            }
        }
        
        return configs[tier]
        
    def validate_dependencies(self, tier: PerformanceTier) -> Dict[str, bool]:
        """Validate that required dependencies are available for tier"""
        validation = {
            'base_requirements': True,  # Always assume basic deps are available
            'ocr_engine': False,
            'gpu_support': False,
            'advanced_features': False
        }
        
        # Check OCR engine availability
        if tier == PerformanceTier.MINIMAL:
            try:
                import pytesseract
                validation['ocr_engine'] = True
            except ImportError:
                pass
        else:
            try:
                import easyocr
                validation['ocr_engine'] = True
            except ImportError:
                # Fallback to tesseract
                try:
                    import pytesseract
                    validation['ocr_engine'] = True
                except ImportError:
                    pass
                    
        # Check GPU support
        if tier in [PerformanceTier.STANDARD, PerformanceTier.MAXIMUM]:
            try:
                import torch
                validation['gpu_support'] = torch.cuda.is_available()
            except ImportError:
                validation['gpu_support'] = False
                
        # Check advanced features
        if tier == PerformanceTier.MAXIMUM:
            try:
                import transformers
                validation['advanced_features'] = True
            except ImportError:
                validation['advanced_features'] = False
                
        return validation
        
    def get_installation_commands(self, tier: PerformanceTier) -> list:
        """Get pip install commands for specific tier"""
        commands = []
        
        if tier == PerformanceTier.MINIMAL:
            commands.append("pip install -r requirements-minimal.txt")
        elif tier == PerformanceTier.STANDARD:
            commands.append("pip install -r requirements.txt")
            if self.system_info['gpu_available']:
                commands.append("pip install easyocr")
        else:  # MAXIMUM
            commands.append("pip install -r requirements.txt")
            commands.append("pip install -r requirements-gpu.txt")
            
        return commands