"""
Hardware-adaptive screen capture functionality
"""

import mss
import numpy as np
from PIL import Image
import cv2
import logging
from typing import Tuple, Optional, Dict, Any
import time

logger = logging.getLogger(__name__)

class ScreenCapture:
    """High-performance screen capture with adaptive optimization"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.sct = mss.mss()
        self.monitor_number = config.get('monitor', 1)
        self.monitor = self.sct.monitors[self.monitor_number]
        self.image_scale = config.get('image_scale', 1.0)
        
        # Performance optimization
        self.last_capture_time = 0
        self.min_capture_interval = 1.0 / 60  # Max 60 FPS
        
        # Cache for regions
        self.region_cache = {}
        
        logger.info(f"Screen capture initialized for monitor {self.monitor_number}")
        logger.info(f"Monitor resolution: {self.monitor['width']}x{self.monitor['height']}")
        logger.info(f"Image scale: {self.image_scale}")
        
    async def capture(self) -> np.ndarray:
        """Capture full screen with rate limiting"""
        current_time = time.time()
        
        # Rate limiting for performance
        if current_time - self.last_capture_time < self.min_capture_interval:
            await self._async_sleep(self.min_capture_interval - (current_time - self.last_capture_time))
            
        screenshot = self.sct.grab(self.monitor)
        img = self._process_screenshot(screenshot)
        
        self.last_capture_time = time.time()
        return img
        
    async def capture_region(self, x: int, y: int, width: int, height: int) -> np.ndarray:
        """Capture specific region with caching"""
        region_key = f"{x}_{y}_{width}_{height}"
        
        # Use cached region definition if available
        if region_key not in self.region_cache:
            self.region_cache[region_key] = {
                'left': self.monitor['left'] + x,
                'top': self.monitor['top'] + y,
                'width': width,
                'height': height
            }
            
        region = self.region_cache[region_key]
        screenshot = self.sct.grab(region)
        return self._process_screenshot(screenshot)
        
    def _process_screenshot(self, screenshot) -> np.ndarray:
        """Process screenshot with hardware-adaptive optimizations"""
        # Convert to numpy array
        img = np.array(screenshot)
        
        # Convert BGRA to RGB (remove alpha channel)
        if img.shape[2] == 4:
            img = img[:, :, [2, 1, 0]]  # BGRA to RGB
        elif img.shape[2] == 3:
            img = img[:, :, [2, 1, 0]]  # BGR to RGB
            
        # Apply image scaling for performance
        if self.image_scale != 1.0:
            new_height = int(img.shape[0] * self.image_scale)
            new_width = int(img.shape[1] * self.image_scale)
            img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
        return img
        
    def capture_regions_batch(self, regions: Dict[str, Dict[str, int]]) -> Dict[str, np.ndarray]:
        """Capture multiple regions in a single operation for efficiency"""
        results = {}
        
        for region_name, region_coords in regions.items():
            try:
                x, y = region_coords['x'], region_coords['y']
                width, height = region_coords['width'], region_coords['height']
                
                # Adjust coordinates for image scaling
                if self.image_scale != 1.0:
                    x = int(x * self.image_scale)
                    y = int(y * self.image_scale)
                    width = int(width * self.image_scale)
                    height = int(height * self.image_scale)
                
                region = {
                    'left': self.monitor['left'] + x,
                    'top': self.monitor['top'] + y,
                    'width': width,
                    'height': height
                }
                
                screenshot = self.sct.grab(region)
                results[region_name] = self._process_screenshot(screenshot)
                
            except Exception as e:
                logger.warning(f"Failed to capture region {region_name}: {e}")
                results[region_name] = None
                
        return results
        
    def save_screenshot(self, img: np.ndarray, filename: str):
        """Save screenshot for debugging"""
        try:
            Image.fromarray(img).save(filename)
            logger.debug(f"Screenshot saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save screenshot: {e}")
            
    def get_monitor_info(self) -> Dict[str, Any]:
        """Get monitor information"""
        return {
            'number': self.monitor_number,
            'width': self.monitor['width'],
            'height': self.monitor['height'],
            'left': self.monitor['left'],
            'top': self.monitor['top']
        }
        
    def detect_resolution(self) -> Tuple[int, int]:
        """Detect actual game resolution by looking for UI elements"""
        # This is a simplified implementation
        # In practice, you'd analyze the screenshot to find game UI boundaries
        return self.monitor['width'], self.monitor['height']
        
    async def _async_sleep(self, duration: float):
        """Async sleep for rate limiting"""
        import asyncio
        await asyncio.sleep(duration)
        
    def optimize_for_performance(self, performance_tier: str):
        """Adjust capture settings based on performance tier"""
        if performance_tier == 'minimal':
            self.image_scale = 0.5
            self.min_capture_interval = 1.0 / 30  # 30 FPS max
        elif performance_tier == 'standard':
            self.image_scale = 0.75
            self.min_capture_interval = 1.0 / 45  # 45 FPS max
        else:  # maximum
            self.image_scale = 1.0
            self.min_capture_interval = 1.0 / 60  # 60 FPS max
            
        logger.info(f"Screen capture optimized for {performance_tier} performance")
        
    def clear_cache(self):
        """Clear region cache to free memory"""
        self.region_cache.clear()
        logger.debug("Screen capture cache cleared")