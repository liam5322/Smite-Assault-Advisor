#!/usr/bin/env python3
"""
🤖 Local LLM Brain for SMITE 2 Assault Advisor
Hardware-adaptive AI with automatic model selection
"""

import os
import json
import logging
import psutil
import subprocess
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Union
from pathlib import Path
import requests

logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """LLM model configuration"""
    name: str
    size_mb: int
    ram_requirement_gb: float
    vram_requirement_gb: float
    performance_tier: str
    download_url: str
    
    def can_run(self, ram_gb: float, vram_gb: float = 0) -> bool:
        """Check if model can run on current hardware"""
        return ram_gb >= self.ram_requirement_gb

class LocalLLMBrain:
    """Local LLM integration with hardware adaptation"""
    
    # Model configurations (from smallest to largest)
    MODELS = [
        ModelConfig(
            name="qwen-0.5b-chat-q4_0",
            size_mb=395,
            ram_requirement_gb=2.0,
            vram_requirement_gb=0,
            performance_tier="minimal",
            download_url="https://huggingface.co/Qwen/Qwen-0.5B-Chat-GGUF/resolve/main/qwen-0_5b-chat-q4_0.gguf"
        ),
        ModelConfig(
            name="tinyllama-1.1b-chat-q4_k_m",
            size_mb=650,
            ram_requirement_gb=4.0,
            vram_requirement_gb=0,
            performance_tier="standard",
            download_url="https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.q4_k_m.gguf"
        ),
        ModelConfig(
            name="qwen-1.8b-chat-q4_k_m",
            size_mb=1100,
            ram_requirement_gb=6.0,
            vram_requirement_gb=0,
            performance_tier="standard",
            download_url="https://huggingface.co/Qwen/Qwen-1.8B-Chat-GGUF/resolve/main/qwen-1_8b-chat-q4_k_m.gguf"
        ),
        ModelConfig(
            name="mistral-7b-instruct-q6_k",
            size_mb=5800,
            ram_requirement_gb=12.0,
            vram_requirement_gb=6.0,
            performance_tier="maximum",
            download_url="https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.q6_k.gguf"
        )
    ]
    
    def __init__(self):
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)
        
        self.hardware_info = self._detect_hardware()
        self.selected_model = self._select_best_model()
        self.ollama_running = False
        
        logger.info(f"🤖 LLM Brain initialized")
        logger.info(f"💾 Available RAM: {self.hardware_info['ram_gb']:.1f}GB")
        logger.info(f"🎯 Selected model: {self.selected_model.name}")
    
    def _detect_hardware(self) -> Dict:
        """Detect available hardware resources"""
        ram_gb = psutil.virtual_memory().total / (1024**3)
        available_ram_gb = psutil.virtual_memory().available / (1024**3)
        
        # Try to detect VRAM (basic detection)
        vram_gb = 0
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                vram_gb = max(gpu.memoryTotal / 1024 for gpu in gpus)
        except ImportError:
            pass
        
        return {
            'ram_gb': ram_gb,
            'available_ram_gb': available_ram_gb,
            'vram_gb': vram_gb,
            'cpu_cores': psutil.cpu_count()
        }
    
    def _select_best_model(self) -> ModelConfig:
        """Select best model for current hardware"""
        available_ram = self.hardware_info['available_ram_gb']
        
        # Find largest model that fits
        for model in reversed(self.MODELS):
            if model.can_run(available_ram):
                logger.info(f"✅ Selected {model.name} (requires {model.ram_requirement_gb}GB, have {available_ram:.1f}GB)")
                return model
        
        # Fallback to smallest model
        logger.warning(f"⚠️ Low RAM detected, using smallest model")
        return self.MODELS[0]
    
    def setup_ollama(self) -> bool:
        """Setup Ollama for local LLM inference"""
        try:
            # Check if Ollama is installed
            result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("Ollama not installed. Please install from https://ollama.ai/")
                return False
            
            logger.info(f"✅ Ollama detected: {result.stdout.strip()}")
            
            # Start Ollama service
            self._start_ollama_service()
            
            # Download/setup model
            return self._setup_model()
            
        except FileNotFoundError:
            logger.error("Ollama not found. Install with: curl -fsSL https://ollama.ai/install.sh | sh")
            return False
    
    def _start_ollama_service(self):
        """Start Ollama service in background"""
        try:
            # Check if already running
            response = requests.get('http://localhost:11434/api/tags', timeout=2)
            if response.status_code == 200:
                logger.info("✅ Ollama service already running")
                self.ollama_running = True
                return
        except requests.exceptions.RequestException:
            pass
        
        # Start Ollama service
        logger.info("🚀 Starting Ollama service...")
        subprocess.Popen(['ollama', 'serve'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait for service to start
        for _ in range(10):
            try:
                response = requests.get('http://localhost:11434/api/tags', timeout=2)
                if response.status_code == 200:
                    logger.info("✅ Ollama service started")
                    self.ollama_running = True
                    return
            except requests.exceptions.RequestException:
                time.sleep(1)
        
        logger.error("❌ Failed to start Ollama service")
    
    def _setup_model(self) -> bool:
        """Download and setup the selected model"""
        if not self.ollama_running:
            return False
        
        try:
            # Check if model already exists
            response = requests.get('http://localhost:11434/api/tags')
            existing_models = [model['name'] for model in response.json().get('models', [])]
            
            model_name = self.selected_model.name
            if model_name in existing_models:
                logger.info(f"✅ Model {model_name} already available")
                return True
            
            # Pull model
            logger.info(f"📥 Downloading {model_name} ({self.selected_model.size_mb}MB)...")
            
            pull_data = {'name': model_name}
            response = requests.post('http://localhost:11434/api/pull', json=pull_data, stream=True)
            
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if 'status' in data:
                        logger.info(f"📥 {data['status']}")
                    if data.get('status') == 'success':
                        logger.info(f"✅ Model {model_name} ready!")
                        return True
            
        except Exception as e:
            logger.error(f"❌ Model setup failed: {e}")
            return False
    
    def generate_assault_tip(self, context: Dict) -> str:
        """Generate Assault-specific tip using local LLM"""
        if not self.ollama_running:
            return self._fallback_tip(context)
        
        try:
            # Prepare prompt
            prompt = self._create_assault_prompt(context)
            
            # Generate response
            response = requests.post('http://localhost:11434/api/generate', json={
                'model': self.selected_model.name,
                'prompt': prompt,
                'stream': False,
                'options': {
                    'temperature': 0.7,
                    'max_tokens': 100,
                    'top_p': 0.9
                }
            }, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
        
        return self._fallback_tip(context)
    
    def _create_assault_prompt(self, context: Dict) -> str:
        """Create Assault-specific prompt"""
        team1 = context.get('team1', [])
        team2 = context.get('team2', [])
        win_rate = context.get('win_probability', 0.5) * 100
        
        prompt = f"""You are a SMITE 2 Assault expert. Analyze this team composition:

Your Team: {', '.join(team1)}
Enemy Team: {', '.join(team2)}
Win Probability: {win_rate:.0f}%

Give ONE concise tip (max 20 words) focusing on:
- Counter-building priorities
- Team fight positioning
- Sustain management in Assault mode

Tip:"""
        
        return prompt
    
    def _fallback_tip(self, context: Dict) -> str:
        """Fallback tips when LLM unavailable"""
        team2 = context.get('team2', [])
        
        # Simple rule-based tips
        healers = ['aphrodite', 'ra', 'neith', 'cupid', 'sobek']
        hunters = ['artemis', 'apollo', 'anhur', 'cupid', 'neith']
        
        has_healers = any(god.lower() in healers for god in team2)
        has_hunters = any(god.lower() in hunters for god in team2)
        
        if has_healers:
            return "Buy anti-heal immediately - Divine Ruin or Brawler's Beat Stick"
        elif has_hunters:
            return "Consider Spectral Armor against their crit potential"
        else:
            return "Focus on team positioning and Meditation timing"

def main():
    """Test the Local LLM Brain"""
    print("🤖 Local LLM Brain Test")
    print("=" * 40)
    
    # Initialize
    llm_brain = LocalLLMBrain()
    
    # Setup Ollama
    if llm_brain.setup_ollama():
        print("✅ LLM setup complete!")
        
        # Test generation
        context = {
            'team1': ['Zeus', 'Ares', 'Apollo', 'Thor', 'Ymir'],
            'team2': ['Aphrodite', 'Ra', 'Kukulkan', 'Neith', 'Janus'],
            'win_probability': 0.45
        }
        
        print("\n🎯 Generating tip...")
        tip = llm_brain.generate_assault_tip(context)
        print(f"💡 Tip: {tip}")
    else:
        print("❌ LLM setup failed, using fallback mode")

if __name__ == "__main__":
    main()