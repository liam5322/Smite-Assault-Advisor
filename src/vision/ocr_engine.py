"""
Adaptive OCR engine with multiple backend support
"""

import cv2
import numpy as np
from rapidfuzz import fuzz
import logging
from pathlib import Path
import json
from typing import List, Tuple, Dict, Any, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class OCRBackend(ABC):
    """Abstract base class for OCR backends"""
    
    @abstractmethod
    def read_text(self, image: np.ndarray) -> List[Tuple[str, float]]:
        """Read text from image, return list of (text, confidence) tuples"""
        pass
        
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this backend is available"""
        pass

class TesseractBackend(OCRBackend):
    """Lightweight Tesseract OCR backend"""
    
    def __init__(self):
        self.available = self._check_availability()
        if self.available:
            import pytesseract
            self.pytesseract = pytesseract
            
    def _check_availability(self) -> bool:
        try:
            import pytesseract
            # Test if tesseract is installed
            pytesseract.get_tesseract_version()
            return True
        except (ImportError, Exception):
            return False
            
    def is_available(self) -> bool:
        return self.available
        
    def read_text(self, image: np.ndarray) -> List[Tuple[str, float]]:
        """Read text using Tesseract"""
        if not self.available:
            return []
            
        try:
            # Get detailed data with confidence scores
            data = self.pytesseract.image_to_data(image, output_type=self.pytesseract.Output.DICT)
            
            results = []
            for i, text in enumerate(data['text']):
                if text.strip():  # Skip empty text
                    confidence = float(data['conf'][i]) / 100.0  # Convert to 0-1 range
                    if confidence > 0.3:  # Filter low confidence
                        results.append((text.strip(), confidence))
                        
            return results
            
        except Exception as e:
            logger.error(f"Tesseract OCR failed: {e}")
            return []

class EasyOCRBackend(OCRBackend):
    """Advanced EasyOCR backend with GPU support"""
    
    def __init__(self, gpu_enabled: bool = False):
        self.gpu_enabled = gpu_enabled
        self.available = self._check_availability()
        self.reader = None
        
        if self.available:
            self._initialize_reader()
            
    def _check_availability(self) -> bool:
        try:
            import easyocr
            return True
        except ImportError:
            return False
            
    def _initialize_reader(self):
        """Initialize EasyOCR reader"""
        try:
            import easyocr
            self.reader = easyocr.Reader(['en'], gpu=self.gpu_enabled)
            logger.info(f"EasyOCR initialized with GPU: {self.gpu_enabled}")
        except Exception as e:
            logger.error(f"Failed to initialize EasyOCR: {e}")
            self.available = False
            
    def is_available(self) -> bool:
        return self.available and self.reader is not None
        
    def read_text(self, image: np.ndarray) -> List[Tuple[str, float]]:
        """Read text using EasyOCR"""
        if not self.is_available():
            return []
            
        try:
            results = self.reader.readtext(image)
            return [(text, confidence) for (_, text, confidence) in results if confidence > 0.3]
            
        except Exception as e:
            logger.error(f"EasyOCR failed: {e}")
            return []

class OCREngine:
    """Adaptive OCR engine that selects best available backend"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.god_names = self._load_god_names()
        self.backend = self._initialize_backend()
        
        # OCR regions (will be adjusted by config manager)
        self.regions = config.get('ocr_regions', {})
        
        # Performance settings
        self.confidence_threshold = config.get('ocr_confidence', 0.7)
        self.fuzzy_threshold = config.get('fuzzy_match_threshold', 80)
        
        logger.info(f"OCR engine initialized with backend: {type(self.backend).__name__}")
        
    def _initialize_backend(self) -> OCRBackend:
        """Initialize the best available OCR backend"""
        preferred_engine = self.config.get('ocr_engine', 'easyocr')
        gpu_acceleration = self.config.get('gpu_acceleration', False)
        
        # Try preferred engine first
        if preferred_engine == 'easyocr':
            backend = EasyOCRBackend(gpu_enabled=gpu_acceleration)
            if backend.is_available():
                return backend
            logger.warning("EasyOCR not available, falling back to Tesseract")
            
        # Fallback to Tesseract
        backend = TesseractBackend()
        if backend.is_available():
            return backend
            
        # No OCR available
        logger.error("No OCR backend available!")
        raise RuntimeError("No OCR backend available")
        
    def _load_god_names(self) -> List[str]:
        """Load valid god names from database"""
        god_file = Path(__file__).parent.parent.parent / 'assets' / 'gods.json'
        
        # Comprehensive god list for SMITE 2
        default_gods = [
            'Achilles', 'Agni', 'Ah Muzen Cab', 'Ah Puch', 'Amaterasu', 'Anhur',
            'Anubis', 'Ao Kuang', 'Aphrodite', 'Apollo', 'Arachne', 'Ares',
            'Artemis', 'Artio', 'Athena', 'Awilix', 'Baba Yaga', 'Bacchus',
            'Bakasura', 'Baron Samedi', 'Bastet', 'Bellona', 'Cabrakan', 'Camazotz',
            'Cerberus', 'Cernunnos', 'Chaac', 'Chang\'e', 'Chernobog', 'Chiron',
            'Chronos', 'Cthulhu', 'Cu Chulainn', 'Cupid', 'Da Ji', 'Danzaburou',
            'Discordia', 'Erlang Shen', 'Eset', 'Fafnir', 'Fenrir', 'Freya',
            'Ganesha', 'Geb', 'Gilgamesh', 'Guan Yu', 'Hachiman', 'Hades',
            'He Bo', 'Heimdallr', 'Hel', 'Hera', 'Hercules', 'Horus',
            'Hou Yi', 'Hun Batz', 'Izanami', 'Janus', 'Jing Wei', 'Jormungandr',
            'Kali', 'Khepri', 'King Arthur', 'Kukulkan', 'Kumbhakarna', 'Kuzenbo',
            'Loki', 'Medusa', 'Mercury', 'Merlin', 'Morgan Le Fay', 'Mulan',
            'Ne Zha', 'Neith', 'Nemesis', 'Nike', 'Nox', 'Nu Wa',
            'Odin', 'Olorun', 'Osiris', 'Pele', 'Persephone', 'Poseidon',
            'Ra', 'Raijin', 'Rama', 'Ratatoskr', 'Ravana', 'Scylla',
            'Serqet', 'Set', 'Shiva', 'Skadi', 'Sobek', 'Sol',
            'Sun Wukong', 'Susano', 'Sylvanus', 'Terra', 'Thanatos', 'The Morrigan',
            'Thor', 'Thoth', 'Tiamat', 'Tsukuyomi', 'Tyr', 'Ullr',
            'Vamana', 'Vulcan', 'Xbalanque', 'Xing Tian', 'Yemoja', 'Ymir',
            'Yu Huang', 'Zeus', 'Zhong Kui'
        ]
        
        if god_file.exists():
            try:
                with open(god_file, 'r') as f:
                    data = json.load(f)
                    return data.get('gods', default_gods)
            except Exception as e:
                logger.warning(f"Failed to load god names: {e}")
                
        return default_gods
        
    def is_loading_screen(self, screenshot: np.ndarray) -> bool:
        """Detect if we're on the loading screen"""
        if 'loading_indicator' not in self.regions:
            return False
            
        region = self.regions['loading_indicator']
        x, y, w, h = region['x'], region['y'], region['width'], region['height']
        
        # Extract region
        region_img = screenshot[y:y+h, x:x+w]
        
        # Preprocess for better OCR
        processed = self._preprocess_for_ocr(region_img)
        
        # Run OCR
        results = self.backend.read_text(processed)
        
        # Look for loading screen indicators
        loading_keywords = ['ASSAULT', 'LOADING', 'MATCH', 'CONQUEST', 'ARENA']
        
        for text, confidence in results:
            if confidence > 0.6:
                text_upper = text.upper()
                for keyword in loading_keywords:
                    if keyword in text_upper:
                        logger.debug(f"Loading screen detected: '{text}' (confidence: {confidence:.2f})")
                        return True
                        
        return False
        
    def is_tab_screen(self, screenshot: np.ndarray) -> bool:
        """Detect if TAB screen (scoreboard) is open"""
        # Look for characteristic UI elements of the TAB screen
        gray = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)
        
        # TAB screen typically darkens the background
        mean_brightness = np.mean(gray)
        
        # Also look for grid patterns typical of item builds
        if mean_brightness < 60:  # Darkened screen
            # Look for item grid patterns in the center
            center_region = gray[200:800, 300:1620]
            
            # Detect grid-like structures (simplified)
            edges = cv2.Canny(center_region, 50, 150)
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
            
            if lines is not None and len(lines) > 10:
                return True
                
        return False
        
    def is_in_game(self, screenshot: np.ndarray) -> bool:
        """Detect if we're in an active game"""
        # Look for minimap in bottom right (typical SMITE UI)
        h, w = screenshot.shape[:2]
        minimap_region = screenshot[int(h*0.75):h, int(w*0.85):w]
        
        # Minimap has characteristic blue/green colors
        avg_color = np.mean(minimap_region, axis=(0, 1))
        
        # Check for blue/green dominance (water/jungle colors)
        blue_green_ratio = (avg_color[1] + avg_color[2]) / (avg_color[0] + 1)
        
        return blue_green_ratio > 1.2
        
    def extract_teams(self, screenshot: np.ndarray) -> Optional[Dict[str, List[str]]]:
        """Extract team compositions from loading screen"""
        teams = {'team1': [], 'team2': []}
        
        # Process each team's region
        for team, region_key in [('team1', 'loading_team1'), ('team2', 'loading_team2')]:
            if region_key not in self.regions:
                logger.warning(f"Region {region_key} not defined")
                continue
                
            region = self.regions[region_key]
            x, y, w, h = region['x'], region['y'], region['width'], region['height']
            
            # Extract and preprocess region
            region_img = screenshot[y:y+h, x:x+w]
            processed = self._preprocess_for_ocr(region_img)
            
            # Run OCR
            results = self.backend.read_text(processed)
            
            # Extract and match god names
            for text, confidence in results:
                if confidence > self.confidence_threshold:
                    god = self._match_god_name(text)
                    if god and god not in teams[team]:
                        teams[team].append(god)
                        logger.debug(f"Detected {god} for {team} (confidence: {confidence:.2f})")
                        
        # Validate team sizes
        if len(teams['team1']) == 5 and len(teams['team2']) == 5:
            logger.info(f"Teams detected - Team 1: {teams['team1']}, Team 2: {teams['team2']}")
            return teams
        else:
            logger.warning(f"Invalid team sizes: {len(teams['team1'])}v{len(teams['team2'])}")
            return None
            
    def _preprocess_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """Enhance image for better OCR results"""
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
            
        # Apply adaptive threshold for better text contrast
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(thresh)
        
        # Morphological operations to clean up text
        kernel = np.ones((2, 2), np.uint8)
        cleaned = cv2.morphologyEx(denoised, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
        
    def _match_god_name(self, text: str) -> Optional[str]:
        """Fuzzy match OCR text to god names"""
        text = text.strip()
        
        # Direct match first
        if text in self.god_names:
            return text
            
        # Clean text for better matching
        cleaned_text = ''.join(c for c in text if c.isalnum() or c.isspace()).strip()
        
        # Fuzzy match
        best_match = None
        best_score = 0
        
        for god in self.god_names:
            # Try multiple matching strategies
            scores = [
                fuzz.ratio(cleaned_text.lower(), god.lower()),
                fuzz.partial_ratio(cleaned_text.lower(), god.lower()),
                fuzz.token_sort_ratio(cleaned_text.lower(), god.lower())
            ]
            
            score = max(scores)
            if score > best_score and score >= self.fuzzy_threshold:
                best_score = score
                best_match = god
                
        if best_match:
            logger.debug(f"Matched '{text}' to '{best_match}' (score: {best_score})")
            
        return best_match
        
    def extract_items(self, screenshot: np.ndarray) -> Dict[str, List[str]]:
        """Extract item builds from TAB screen (future implementation)"""
        # Placeholder for item detection
        # This would analyze the item grid and identify items for each player
        return {}
        
    def get_backend_info(self) -> Dict[str, Any]:
        """Get information about current OCR backend"""
        return {
            'backend': type(self.backend).__name__,
            'available': self.backend.is_available(),
            'gpu_enabled': getattr(self.backend, 'gpu_enabled', False),
            'confidence_threshold': self.confidence_threshold,
            'fuzzy_threshold': self.fuzzy_threshold
        }