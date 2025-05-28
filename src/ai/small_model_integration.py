#!/usr/bin/env python3
"""
Small AI Model Integration for SMITE 2 Assault Advisor
Optimized for lightweight models like Qwen 0.6B, TinyLlama 1.1B, etc.
Uses structured prompts and minimal context to work within token limits
"""

import json
import sqlite3
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging
try:
    from .lightweight_advisor import LightweightAssaultAdvisor, TeamAnalysis
except ImportError:
    from lightweight_advisor import LightweightAssaultAdvisor, TeamAnalysis

# Optional imports for different model backends
try:
    import transformers
    from transformers import AutoTokenizer, AutoModelForCausalLM
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

try:
    import ollama
    HAS_OLLAMA = True
except ImportError:
    HAS_OLLAMA = False

@dataclass
class ModelConfig:
    """Configuration for small AI models"""
    model_name: str
    max_tokens: int
    temperature: float
    backend: str  # 'transformers', 'ollama', 'api'
    context_limit: int
    
class SmallModelAssaultAdvisor:
    """
    AI advisor that uses small language models for natural language responses
    while leveraging the structured database for accurate game data
    """
    
    def __init__(self, model_config: ModelConfig = None, db_path: str = "../../assets/smite2_comprehensive.db"):
        self.logger = logging.getLogger(__name__)
        
        # Initialize the lightweight advisor for structured data
        self.data_advisor = LightweightAssaultAdvisor(db_path)
        
        # Default model configuration for small models
        if model_config is None:
            model_config = ModelConfig(
                model_name="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
                max_tokens=256,
                temperature=0.3,
                backend="transformers",
                context_limit=2048
            )
        
        self.model_config = model_config
        self.model = None
        self.tokenizer = None
        
        # Initialize the model
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the small AI model based on configuration"""
        try:
            if self.model_config.backend == "transformers" and HAS_TRANSFORMERS:
                self._init_transformers_model()
            elif self.model_config.backend == "ollama" and HAS_OLLAMA:
                self._init_ollama_model()
            else:
                self.logger.warning("No AI model backend available, falling back to rule-based responses")
                self.model = None
        except Exception as e:
            self.logger.error(f"Failed to initialize model: {e}")
            self.model = None
    
    def _init_transformers_model(self):
        """Initialize Transformers-based model"""
        self.logger.info(f"Loading model: {self.model_config.model_name}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_config.model_name,
            trust_remote_code=True
        )
        
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_config.model_name,
            trust_remote_code=True,
            torch_dtype="auto",
            device_map="auto" if self._has_gpu() else "cpu"
        )
        
        # Add padding token if missing
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
    
    def _init_ollama_model(self):
        """Initialize Ollama-based model"""
        self.logger.info(f"Using Ollama model: {self.model_config.model_name}")
        # Ollama client will be used directly in generate method
        self.model = "ollama"
    
    def _has_gpu(self) -> bool:
        """Check if GPU is available"""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False
    
    def get_natural_language_advice(self, team_gods: List[str], 
                                  enemy_gods: List[str] = None,
                                  specific_question: str = None) -> str:
        """
        Get natural language advice using the small AI model
        
        Args:
            team_gods: Your team composition
            enemy_gods: Enemy team composition (optional)
            specific_question: Specific question to answer (optional)
            
        Returns:
            Natural language advice string
        """
        # Get structured analysis first
        analysis = self.data_advisor.analyze_team_composition(team_gods)
        quick_recs = self.data_advisor.get_quick_recommendations(team_gods)
        
        # Create minimal context prompt
        context = self._create_minimal_prompt(analysis, quick_recs, enemy_gods, specific_question)
        
        # Generate response
        if self.model is None:
            return self._fallback_response(analysis, quick_recs)
        
        try:
            response = self._generate_response(context)
            return self._post_process_response(response)
        except Exception as e:
            self.logger.error(f"Model generation failed: {e}")
            return self._fallback_response(analysis, quick_recs)
    
    def _create_minimal_prompt(self, analysis: TeamAnalysis, quick_recs: Dict[str, Any],
                              enemy_gods: List[str] = None, question: str = None) -> str:
        """Create a minimal, structured prompt for small models"""
        
        # Base team info (keep very concise)
        team_info = f"""Team: {analysis.overall_score}/10, {quick_recs['healer_status']}, {quick_recs['damage_balance']}
Strategy: {analysis.recommended_strategy}
Items: {', '.join(quick_recs['must_buy_items'])}"""
        
        # Add enemy info if available
        enemy_info = ""
        if enemy_gods:
            enemy_analysis = self.data_advisor.analyze_team_composition(enemy_gods)
            enemy_info = f"\nEnemy: {enemy_analysis.overall_score}/10, {'Healer' if enemy_analysis.has_healer else 'No healer'}"
        
        # Add specific question
        question_part = f"\nQ: {question}" if question else ""
        
        # Create prompt optimized for small models
        prompt = f"""SMITE 2 Assault Advice:
{team_info}{enemy_info}{question_part}

Give brief, actionable advice (max 100 words):"""
        
        return prompt
    
    def _generate_response(self, prompt: str) -> str:
        """Generate response using the configured model"""
        if self.model_config.backend == "transformers" and self.model:
            return self._generate_transformers_response(prompt)
        elif self.model_config.backend == "ollama":
            return self._generate_ollama_response(prompt)
        else:
            raise Exception("No valid model backend")
    
    def _generate_transformers_response(self, prompt: str) -> str:
        """Generate response using Transformers model"""
        inputs = self.tokenizer.encode(prompt, return_tensors="pt")
        
        # Ensure we don't exceed context limit
        if inputs.shape[1] > self.model_config.context_limit - self.model_config.max_tokens:
            # Truncate input to fit
            max_input = self.model_config.context_limit - self.model_config.max_tokens
            inputs = inputs[:, -max_input:]
        
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_new_tokens=self.model_config.max_tokens,
                temperature=self.model_config.temperature,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode only the new tokens
        response = self.tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
        return response.strip()
    
    def _generate_ollama_response(self, prompt: str) -> str:
        """Generate response using Ollama"""
        response = ollama.generate(
            model=self.model_config.model_name,
            prompt=prompt,
            options={
                'temperature': self.model_config.temperature,
                'num_predict': self.model_config.max_tokens
            }
        )
        return response['response'].strip()
    
    def _post_process_response(self, response: str) -> str:
        """Clean up and validate the model response"""
        # Remove any incomplete sentences
        sentences = response.split('.')
        if len(sentences) > 1 and len(sentences[-1].strip()) < 10:
            response = '.'.join(sentences[:-1]) + '.'
        
        # Ensure reasonable length
        if len(response) > 500:
            response = response[:500] + "..."
        
        return response.strip()
    
    def _fallback_response(self, analysis: TeamAnalysis, quick_recs: Dict[str, Any]) -> str:
        """Generate rule-based response when AI model is unavailable"""
        response_parts = []
        
        # Team rating
        if analysis.overall_score >= 8:
            response_parts.append("Strong team composition!")
        elif analysis.overall_score >= 6:
            response_parts.append("Decent team with some weaknesses.")
        else:
            response_parts.append("Challenging team - play carefully.")
        
        # Key advice
        if analysis.has_healer:
            response_parts.append("Use your healer advantage - play for sustain.")
        else:
            response_parts.append("No healer - prioritize lifesteal and sustain items.")
        
        # Strategy
        response_parts.append(f"Strategy: {analysis.recommended_strategy}")
        
        # Items
        response_parts.append(f"Priority items: {', '.join(quick_recs['must_buy_items'][:2])}.")
        
        return " ".join(response_parts)
    
    def get_god_specific_advice(self, god_name: str, team_gods: List[str]) -> str:
        """Get specific advice for playing a particular god"""
        try:
            # Get structured recommendation
            god_rec = self.data_advisor.get_god_build_recommendation(god_name, team_gods)
            
            # Create focused prompt
            prompt = f"""SMITE 2 Assault - Playing {god_name}:
Build: {' → '.join(god_rec.build_order[:3])}
Role: {god_rec.playstyle_notes[:100]}

Give specific tips for playing {god_name} in assault (max 80 words):"""
            
            if self.model:
                try:
                    response = self._generate_response(prompt)
                    return self._post_process_response(response)
                except:
                    pass
            
            # Fallback
            return f"Playing {god_name}: {god_rec.playstyle_notes} Build order: {' → '.join(god_rec.build_order[:4])}."
            
        except Exception as e:
            return f"Unable to provide specific advice for {god_name}. Focus on your role and build sustain items."
    
    def get_item_explanation(self, item_name: str, context: str = "") -> str:
        """Get explanation of why an item is recommended"""
        cursor = self.data_advisor.conn.cursor()
        cursor.execute("SELECT * FROM items WHERE name = ?", (item_name,))
        item = cursor.fetchone()
        
        if not item:
            return f"Item '{item_name}' not found in database."
        
        # Create explanation prompt
        prompt = f"""SMITE 2 Item: {item_name}
Priority: {item['assault_priority']}
Utility: {item['assault_utility'][:100]}
{context}

Explain why this item is good in assault (max 60 words):"""
        
        if self.model:
            try:
                response = self._generate_response(prompt)
                return self._post_process_response(response)
            except:
                pass
        
        # Fallback
        return f"{item_name}: {item['assault_utility']} Priority: {item['assault_priority']}."
    
    def close(self):
        """Clean up resources"""
        if self.data_advisor:
            self.data_advisor.close()
        
        # Clear model from memory
        self.model = None
        self.tokenizer = None

# Factory function for easy model creation
def create_assault_advisor(model_name: str = "auto", backend: str = "auto") -> SmallModelAssaultAdvisor:
    """
    Factory function to create an assault advisor with optimal settings
    
    Args:
        model_name: Model to use ('auto', 'tinyllama', 'qwen', or specific model name)
        backend: Backend to use ('auto', 'transformers', 'ollama')
        
    Returns:
        Configured SmallModelAssaultAdvisor
    """
    
    # Auto-detect backend
    if backend == "auto":
        if HAS_OLLAMA:
            backend = "ollama"
        elif HAS_TRANSFORMERS:
            backend = "transformers"
        else:
            backend = "none"
    
    # Configure model based on name
    if model_name == "auto":
        if backend == "ollama":
            model_name = "tinyllama"  # Ollama model name
        else:
            model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    elif model_name == "tinyllama":
        if backend == "ollama":
            model_name = "tinyllama"
        else:
            model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    elif model_name == "qwen":
        if backend == "ollama":
            model_name = "qwen:0.5b"
        else:
            model_name = "Qwen/Qwen2-0.5B-Instruct"
    
    # Create configuration
    config = ModelConfig(
        model_name=model_name,
        max_tokens=128,  # Keep small for fast response
        temperature=0.3,  # Low temperature for consistent advice
        backend=backend,
        context_limit=2048 if "tinyllama" in model_name.lower() else 4096
    )
    
    return SmallModelAssaultAdvisor(config)

# Example usage and testing
if __name__ == "__main__":
    print("🤖 Initializing Small Model Assault Advisor...")
    
    # Create advisor (will fall back to rule-based if no models available)
    advisor = create_assault_advisor()
    
    # Test team
    test_team = ["Ra", "Ares", "Zeus", "Ah Muzen Cab", "Agni"]
    enemy_team = ["Anubis", "Sobek", "Apollo", "Bellona", "Hercules"]
    
    print("\n💬 Getting natural language advice...")
    advice = advisor.get_natural_language_advice(test_team, enemy_team)
    print(f"Advice: {advice}")
    
    print("\n🎯 Getting god-specific advice...")
    god_advice = advisor.get_god_specific_advice("Ra", test_team)
    print(f"Ra advice: {god_advice}")
    
    print("\n🛡️ Getting item explanation...")
    item_explanation = advisor.get_item_explanation("Amanita Charm", "Team has healer")
    print(f"Amanita Charm: {item_explanation}")
    
    advisor.close()
    print("\n✅ Small model integration test complete!")