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
class HardwareProfile:
    """Hardware capability profile"""
    tier: str  # "minimal", "standard", "maximum"
    ram_gb: float
    cpu_cores: int
    gpu_available: bool
    recommended_model: str
    max_context: int
    description: str

@dataclass
class LLMModel:
    """Local LLM model configuration"""
    name: str
    size_gb: float
    min_ram_gb: float
    context_length: int
    download_url: str
    capabilities: List[str]
    performance_tier: str

class LocalLLMBrain:
    def __init__(self):
        self.hardware_profile = self.detect_hardware()
        self.available_models = self.get_available_models()
        self.current_model = None
        self.llm_process = None
        self.api_port = 11434  # Ollama default
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def detect_hardware(self) -> HardwareProfile:
        """Detect hardware capabilities and recommend tier"""
        # Get system info
        ram_gb = psutil.virtual_memory().total / (1024**3)
        cpu_cores = psutil.cpu_count()
        
        # Check for GPU (basic detection)
        gpu_available = self.has_gpu()
        
        # Determine tier based on hardware
        if ram_gb >= 16 and cpu_cores >= 8:
            tier = "maximum"
            model = "qwen2.5:7b"
            context = 8192
            desc = "High-end system - Full AI capabilities"
        elif ram_gb >= 8 and cpu_cores >= 4:
            tier = "standard" 
            model = "qwen2.5:3b"
            context = 4096
            desc = "Mid-range system - Good AI performance"
        else:
            tier = "minimal"
            model = "tinyllama:1.1b"
            context = 2048
            desc = "Budget system - Basic AI assistance"
        
        return HardwareProfile(
            tier=tier,
            ram_gb=ram_gb,
            cpu_cores=cpu_cores,
            gpu_available=gpu_available,
            recommended_model=model,
            max_context=context,
            description=desc
        )
    
    def has_gpu(self) -> bool:
        """Check if GPU is available"""
        try:
            # Try nvidia-smi
            subprocess.run(["nvidia-smi"], capture_output=True, check=True)
            return True
        except:
            try:
                # Try AMD GPU detection
                result = subprocess.run(["lspci"], capture_output=True, text=True)
                return "VGA" in result.stdout and ("AMD" in result.stdout or "NVIDIA" in result.stdout)
            except:
                return False
    
    def get_available_models(self) -> Dict[str, LLMModel]:
        """Get available local LLM models"""
        return {
            "tinyllama": LLMModel(
                name="tinyllama:1.1b",
                size_gb=0.6,
                min_ram_gb=2.0,
                context_length=2048,
                download_url="https://ollama.ai/library/tinyllama",
                capabilities=["basic_reasoning", "text_generation"],
                performance_tier="minimal"
            ),
            "qwen2.5-0.5b": LLMModel(
                name="qwen2.5:0.5b",
                size_gb=0.4,
                min_ram_gb=1.5,
                context_length=2048,
                download_url="https://ollama.ai/library/qwen2.5",
                capabilities=["reasoning", "analysis", "gaming_advice"],
                performance_tier="minimal"
            ),
            "qwen2.5-1.5b": LLMModel(
                name="qwen2.5:1.5b",
                size_gb=1.0,
                min_ram_gb=3.0,
                context_length=4096,
                download_url="https://ollama.ai/library/qwen2.5",
                capabilities=["advanced_reasoning", "strategic_analysis", "personality"],
                performance_tier="standard"
            ),
            "qwen2.5-3b": LLMModel(
                name="qwen2.5:3b",
                size_gb=2.0,
                min_ram_gb=6.0,
                context_length=4096,
                download_url="https://ollama.ai/library/qwen2.5",
                capabilities=["expert_analysis", "complex_reasoning", "humor", "coaching"],
                performance_tier="standard"
            ),
            "qwen2.5-7b": LLMModel(
                name="qwen2.5:7b",
                size_gb=4.5,
                min_ram_gb=12.0,
                context_length=8192,
                download_url="https://ollama.ai/library/qwen2.5",
                capabilities=["expert_analysis", "advanced_coaching", "personality", "memes"],
                performance_tier="maximum"
            )
        }
    
    def get_recommended_model(self) -> LLMModel:
        """Get recommended model for current hardware"""
        model_name = self.hardware_profile.recommended_model.replace(":", "-")
        return self.available_models.get(model_name, self.available_models["tinyllama"])
    
    def install_ollama(self) -> bool:
        """Install Ollama if not present"""
        try:
            # Check if ollama is already installed
            subprocess.run(["ollama", "--version"], capture_output=True, check=True)
            self.logger.info("✅ Ollama already installed")
            return True
        except:
            self.logger.info("📦 Installing Ollama...")
            
            system = platform.system().lower()
            
            if system == "linux":
                # Install on Linux
                install_cmd = "curl -fsSL https://ollama.ai/install.sh | sh"
                result = subprocess.run(install_cmd, shell=True, capture_output=True, text=True)
                return result.returncode == 0
            
            elif system == "windows":
                self.logger.info("🪟 Please download Ollama from: https://ollama.ai/download/windows")
                return False
            
            elif system == "darwin":  # macOS
                self.logger.info("🍎 Please download Ollama from: https://ollama.ai/download/mac")
                return False
            
            return False
    
    def download_model(self, model: LLMModel) -> bool:
        """Download and setup model"""
        self.logger.info(f"📥 Downloading {model.name} ({model.size_gb:.1f}GB)...")
        
        try:
            # Pull model with ollama
            result = subprocess.run(
                ["ollama", "pull", model.name],
                capture_output=True,
                text=True,
                timeout=1800  # 30 minute timeout
            )
            
            if result.returncode == 0:
                self.logger.info(f"✅ {model.name} downloaded successfully")
                return True
            else:
                self.logger.error(f"❌ Failed to download {model.name}: {result.stderr}")
                return False
        
        except subprocess.TimeoutExpired:
            self.logger.error("❌ Download timeout - check internet connection")
            return False
        except Exception as e:
            self.logger.error(f"❌ Download error: {e}")
            return False
    
    def start_llm_server(self, model: LLMModel) -> bool:
        """Start local LLM server"""
        try:
            # Start ollama serve in background
            self.llm_process = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for server to start
            time.sleep(3)
            
            # Test connection
            if self.test_llm_connection():
                self.current_model = model
                self.logger.info(f"🚀 LLM server started with {model.name}")
                return True
            else:
                self.stop_llm_server()
                return False
        
        except Exception as e:
            self.logger.error(f"❌ Failed to start LLM server: {e}")
            return False
    
    def test_llm_connection(self) -> bool:
        """Test LLM API connection"""
        try:
            response = requests.get(f"http://localhost:{self.api_port}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def stop_llm_server(self):
        """Stop LLM server"""
        if self.llm_process:
            self.llm_process.terminate()
            self.llm_process = None
            self.current_model = None
            self.logger.info("🛑 LLM server stopped")
    
    def generate_assault_analysis(self, team1: List[str], team2: List[str], 
                                win_probability: float, items: List[str]) -> str:
        """Generate intelligent Assault analysis using local LLM"""
        if not self.current_model:
            return "LLM not available - using basic analysis"
        
        # Create context-aware prompt
        prompt = self.create_assault_prompt(team1, team2, win_probability, items)
        
        try:
            response = requests.post(
                f"http://localhost:{self.api_port}/api/generate",
                json={
                    "model": self.current_model.name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 200
                    }
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "Analysis failed")
            else:
                return "LLM analysis unavailable"
        
        except Exception as e:
            self.logger.error(f"LLM generation error: {e}")
            return "LLM analysis failed"
    
    def create_assault_prompt(self, team1: List[str], team2: List[str], 
                            win_probability: float, items: List[str]) -> str:
        """Create intelligent prompt for Assault analysis"""
        
        # Adapt prompt complexity based on model capability
        if self.hardware_profile.tier == "minimal":
            # Simple prompt for tiny models
            return f"""SMITE 2 Assault: {', '.join(team1)} vs {', '.join(team2)}
Win rate: {win_probability:.0%}
Key items: {', '.join(items[:2])}

Give 1 short tip:"""
        
        elif self.hardware_profile.tier == "standard":
            # Medium complexity prompt
            return f"""SMITE 2 Assault Analysis:
Your team: {', '.join(team1)}
Enemy team: {', '.join(team2)}
Win probability: {win_probability:.1%}
Priority items: {', '.join(items[:3])}

Provide 2-3 strategic tips for Assault mode (no backing, team fights, sustain focus):"""
        
        else:
            # Full complexity for high-end systems
            return f"""You are a SMITE 2 Assault expert analyzing this matchup:

YOUR TEAM: {', '.join(team1)}
ENEMY TEAM: {', '.join(team2)}
WIN PROBABILITY: {win_probability:.1%}
PRIORITY ITEMS: {', '.join(items)}

ASSAULT CONTEXT:
- No backing to base (sustain is king)
- Constant team fights
- Meditation timing crucial
- Anti-heal wins games vs healers

Provide expert analysis with:
1. Key strategic advice (2-3 points)
2. Item priority explanation
3. Team fight approach
4. One tactical tip

Keep it concise but insightful. Add some personality but stay focused on winning."""
    
    def generate_voice_coaching(self, situation: str, personality: str = "hype") -> str:
        """Generate voice coaching lines"""
        if not self.current_model:
            return "Let's go team!"
        
        prompts = {
            "hype": f"Generate an excited gaming coach line for: {situation}. Keep it short and energetic!",
            "calm": f"Generate calm strategic advice for: {situation}. Professional tone.",
            "funny": f"Generate a humorous but helpful comment about: {situation}. Gaming humor."
        }
        
        prompt = prompts.get(personality, prompts["hype"])
        
        try:
            response = requests.post(
                f"http://localhost:{self.api_port}/api/generate",
                json={
                    "model": self.current_model.name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.8, "max_tokens": 50}
                },
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "Let's dominate!").strip()
            
        except:
            pass
        
        # Fallback responses
        fallbacks = {
            "hype": ["LET'S GO!", "Time to dominate!", "You got this!"],
            "calm": ["Focus on objectives", "Play smart", "Coordinate abilities"],
            "funny": ["Time to int... I mean win!", "Carry mode activated!", "Ez game ez life"]
        }
        
        import random
        return random.choice(fallbacks.get(personality, fallbacks["hype"]))
    
    def setup_auto_install(self) -> bool:
        """Automatically setup the best model for this hardware"""
        self.logger.info(f"🔧 Setting up LLM for {self.hardware_profile.tier} hardware")
        self.logger.info(f"💾 RAM: {self.hardware_profile.ram_gb:.1f}GB, CPU: {self.hardware_profile.cpu_cores} cores")
        
        # Install Ollama
        if not self.install_ollama():
            self.logger.error("❌ Failed to install Ollama")
            return False
        
        # Get recommended model
        model = self.get_recommended_model()
        self.logger.info(f"🎯 Recommended model: {model.name} ({model.size_gb:.1f}GB)")
        
        # Check if we have enough RAM
        if self.hardware_profile.ram_gb < model.min_ram_gb:
            self.logger.warning(f"⚠️ Low RAM - trying smaller model")
            model = self.available_models["qwen2.5-0.5b"]
        
        # Download model
        if not self.download_model(model):
            # Try fallback to tinyllama
            self.logger.info("🔄 Trying fallback model...")
            model = self.available_models["tinyllama"]
            if not self.download_model(model):
                return False
        
        # Start server
        return self.start_llm_server(model)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current LLM status"""
        return {
            "hardware_tier": self.hardware_profile.tier,
            "ram_gb": self.hardware_profile.ram_gb,
            "cpu_cores": self.hardware_profile.cpu_cores,
            "gpu_available": self.hardware_profile.gpu_available,
            "current_model": self.current_model.name if self.current_model else None,
            "server_running": self.llm_process is not None,
            "api_available": self.test_llm_connection()
        }

def main():
    """Demo the local LLM brain"""
    brain = LocalLLMBrain()
    
    print("🧠 SMITE 2 Local LLM Brain")
    print("=" * 40)
    print(f"Hardware: {brain.hardware_profile.description}")
    print(f"Recommended: {brain.hardware_profile.recommended_model}")
    
    # Auto-setup
    print("\n🚀 Setting up LLM...")
    if brain.setup_auto_install():
        print("✅ LLM ready!")
        
        # Test analysis
        print("\n🎯 Testing analysis...")
        analysis = brain.generate_assault_analysis(
            ["Zeus", "Ares", "Neith", "Ra", "Ymir"],
            ["Artemis", "Fenrir", "Kukulkan", "Geb", "Janus"],
            0.65,
            ["Divine Ruin", "Meditation Cloak", "Spectral Armor"]
        )
        print(f"Analysis: {analysis}")
        
        # Test voice coaching
        print("\n🎤 Testing voice coaching...")
        coaching = brain.generate_voice_coaching("enemy has healers", "hype")
        print(f"Coaching: {coaching}")
        
    else:
        print("❌ LLM setup failed")
    
    # Show status
    status = brain.get_status()
    print(f"\n📊 Status: {json.dumps(status, indent=2)}")
    
    brain.stop_llm_server()

if __name__ == "__main__":
    main()