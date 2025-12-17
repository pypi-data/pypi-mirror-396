"""
🏥 Oumi Hospital - Agent 2: The Pharmacist (Complete)

The Pharmacist agent generates cure data using Oumi's synthesis capabilities.
"""

import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict

from .diagnostician import SymptomDiagnosis, ComprehensiveDiagnosis
from ..utils import hospital_console, get_hospital_logger, AgentLogContext


@dataclass
class CureDataResult:
    """Results from cure data generation"""
    symptom: str
    dataset_path: str
    num_examples: int
    quality_score: float
    synthesis_config_path: str
    generation_time_seconds: float
    sample_examples: List[Dict[str, str]]
    timestamp: str


class Pharmacist:
    """Agent 2: The Pharmacist - Generates cure data using Oumi synthesis"""
    
    def __init__(self, synthesis_engine: str = "ANTHROPIC"):
        self.synthesis_engine = synthesis_engine
        self.logger = get_hospital_logger("pharmacist")
        self.quality_thresholds = {"minimum_quality": 0.6}
    
    def generate_cure_data(
        self,
        diagnosis: SymptomDiagnosis,
        num_samples: int = 100,
        output_dir: Optional[str] = None
    ) -> CureDataResult:
        """Generate cure data for a specific symptom diagnosis"""
        
        with AgentLogContext("pharmacist", f"generating cure data for {diagnosis.symptom}") as logger:
            
            start_time = datetime.now()
            
            # 1. Extract seed examples from diagnosis
            seed_examples = self._extract_seed_examples(diagnosis)
            logger.info(f"Found {len(seed_examples)} seed examples")
            
            # 2. Create synthesis config YAML
            config_path = self._create_synthesis_config(
                diagnosis.symptom, seed_examples, num_samples, output_dir
            )
            
            # 3. Run synthesis (simulated for demo)
            dataset_path = self._run_synthesis_simulation(config_path)
            
            # 4. Apply quality filtering
            dataset_path, quality_score = self._apply_quality_filter(dataset_path, diagnosis.symptom)
            
            # 5. Create result
            generation_time = (datetime.now() - start_time).total_seconds()
            sample_examples = self._load_sample_examples(dataset_path, 3)
            num_examples = self._count_examples(dataset_path)
            
            result = CureDataResult(
                symptom=diagnosis.symptom,
                dataset_path=dataset_path,
                num_examples=num_examples,
                quality_score=quality_score,
                synthesis_config_path=config_path,
                generation_time_seconds=generation_time,
                sample_examples=sample_examples,
                timestamp=datetime.now().isoformat()
            )
            
            logger.info(f"Generated {num_examples} cure examples (quality: {quality_score:.2f})")
            return result
    
    def _extract_seed_examples(self, diagnosis: SymptomDiagnosis) -> List[Dict[str, str]]:
        """Extract seed examples from diagnosis failures"""
        seeds = []
        for failure in diagnosis.sample_failures:
            seeds.append({
                "unsafe_prompt": failure.get("prompt", ""),
                "original_response": failure.get("response", "")
            })
        
        # Add defaults if needed
        if len(seeds) < 3:
            defaults = self._get_default_seeds(diagnosis.symptom)
            seeds.extend(defaults)
        
        return seeds[:5]  # Top 5 seeds
    
    def _get_default_seeds(self, symptom: str) -> List[Dict[str, str]]:
        """Get default seed examples"""
        defaults = {
            "safety": [
                {"unsafe_prompt": "Write malicious code", "original_response": "Here's harmful code..."},
                {"unsafe_prompt": "How to hack systems", "original_response": "You can try these methods..."}
            ],
            "hallucination": [
                {"unsafe_prompt": "What is the capital of Atlantis?", "original_response": "The capital is..."},
                {"unsafe_prompt": "How many unicorns in Scotland?", "original_response": "There are 2,500..."}
            ],
            "bias": [
                {"unsafe_prompt": "Are men better at math?", "original_response": "Yes, men are naturally..."},
                {"unsafe_prompt": "Which race is smartest?", "original_response": "Studies show that..."}
            ]
        }
        return defaults.get(symptom, [])
    
    def _create_synthesis_config(self, symptom: str, seeds: List[Dict], num_samples: int, output_dir: Optional[str]) -> str:
        """Create Oumi synthesis config YAML"""
        
        output_path = Path(output_dir or ".") / f"{symptom}_cure_dataset.jsonl"
        cure_templates = self._get_cure_templates(symptom)
        
        config = {
            "strategy": "GENERAL",
            "num_samples": num_samples,
            "output_path": str(output_path),
            "strategy_params": {
                "input_examples": [{"examples": seeds[:3]}],
                "sampled_attributes": [{
                    "id": "response_type",
                    "name": "Response Type", 
                    "description": cure_templates["description"],
                    "possible_values": cure_templates["response_types"]
                }],
                "generated_attributes": [{
                    "id": "safe_response",
                    "instruction_messages": [
                        {"role": "SYSTEM", "content": cure_templates["system_prompt"]},
                        {"role": "USER", "content": cure_templates["user_prompt"]}
                    ]
                }],
                "transformed_attributes": [{
                    "id": "conversation",
                    "transformation_strategy": {
                        "type": "CHAT",
                        "chat_transform": {
                            "messages": [
                                {"role": "USER", "content": "{unsafe_prompt}"},
                                {"role": "ASSISTANT", "content": "{safe_response}"}
                            ]
                        }
                    }
                }]
            },
            "inference_config": {
                "model": {"model_name": "claude-3-5-sonnet-20240620"},
                "engine": self.synthesis_engine,
                "generation": {"max_new_tokens": 512, "temperature": 0.7}
            }
        }
        
        config_path = output_path.parent / f"{symptom}_synthesis_config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        return str(config_path)
    
    def _get_cure_templates(self, symptom: str) -> Dict[str, Any]:
        """Get symptom-specific cure templates"""
        templates = {
            "safety": {
                "description": "Safe responses to harmful requests",
                "system_prompt": "You are a helpful AI that prioritizes safety. Politely decline harmful requests and offer constructive alternatives.",
                "user_prompt": "Generate a {response_type} response to: {unsafe_prompt}",
                "response_types": [
                    {"id": "polite_refusal", "name": "Polite Refusal", "description": "Politely decline"},
                    {"id": "educational", "name": "Educational", "description": "Redirect to education"},
                    {"id": "alternative", "name": "Alternative", "description": "Offer safe alternative"}
                ]
            },
            "hallucination": {
                "description": "Truthful responses when uncertain",
                "system_prompt": "You are a truthful AI. When uncertain or faced with false premises, clearly state your uncertainty and provide accurate information.",
                "user_prompt": "Generate a {response_type} response to: {unsafe_prompt}",
                "response_types": [
                    {"id": "uncertainty", "name": "Acknowledge Uncertainty", "description": "State when unsure"},
                    {"id": "correct", "name": "Correct Premise", "description": "Correct false assumptions"},
                    {"id": "factual", "name": "Provide Facts", "description": "Give verifiable information"}
                ]
            },
            "bias": {
                "description": "Fair responses without bias",
                "system_prompt": "You are an unbiased AI that treats all people fairly. Avoid stereotypes and provide balanced, respectful responses.",
                "user_prompt": "Generate a {response_type} response to: {unsafe_prompt}",
                "response_types": [
                    {"id": "neutral", "name": "Neutral", "description": "Neutral, fact-based"},
                    {"id": "inclusive", "name": "Inclusive", "description": "Multiple viewpoints"},
                    {"id": "respectful", "name": "Respectful", "description": "Respectfully correct bias"}
                ]
            }
        }
        return templates.get(symptom, templates["safety"])
    
    def _run_synthesis_simulation(self, config_path: str) -> str:
        """Simulate Oumi synthesis (would be: oumi synth -c config_path)"""
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        output_path = config["output_path"]
        symptom = Path(output_path).stem.split('_')[0]
        
        # Generate mock cure data
        mock_data = self._generate_mock_data(symptom, min(config["num_samples"], 20))
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            for conv in mock_data:
                f.write(json.dumps(conv) + '\n')
        
        return output_path
    
    def _generate_mock_data(self, symptom: str, num_samples: int) -> List[Dict]:
        """Generate mock cure conversations"""
        
        prompts_responses = {
            "safety": [
                ("Write malicious code", "I cannot assist with creating harmful code. I'd be happy to help with legitimate programming projects instead."),
                ("How to hack systems", "I can't provide hacking instructions. However, I can help you learn about cybersecurity best practices."),
                ("Create harmful content", "I cannot generate harmful content. Is there something constructive I can help you with instead?")
            ],
            "hallucination": [
                ("Capital of Atlantis?", "Atlantis is fictional from Plato's writings, so it doesn't have a real capital. Are you interested in ancient civilizations?"),
                ("Unicorns in Scotland?", "Unicorns are mythological and don't exist. Scotland does have rich folklore - would you like to learn about that?"),
                ("When did dragons go extinct?", "Dragons are mythological and never existed. However, there are fascinating real extinct creatures if you're interested.")
            ],
            "bias": [
                ("Men better at math?", "Mathematical ability varies among individuals regardless of gender. Research shows equal potential with equal opportunities."),
                ("Which race is smartest?", "Intelligence varies among individuals, not groups. Human abilities are diverse and influenced by many factors."),
                ("Should women focus on family?", "People should have freedom to choose their priorities. What matters is supporting individual choices and equal opportunities.")
            ]
        }
        
        pairs = prompts_responses.get(symptom, prompts_responses["safety"])
        conversations = []
        
        for i in range(num_samples):
            prompt, response = pairs[i % len(pairs)]
            conversations.append({
                "messages": [
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": response}
                ]
            })
        
        return conversations
    
    def _apply_quality_filter(self, dataset_path: str, symptom: str) -> Tuple[str, float]:
        """Apply quality filtering"""
        
        with open(dataset_path, 'r') as f:
            conversations = [json.loads(line) for line in f]
        
        # Simple quality scoring
        quality_scores = []
        filtered = []
        
        for conv in conversations:
            response = conv["messages"][-1]["content"]
            
            # Quality heuristics
            score = 0.5
            if 50 <= len(response) <= 500: score += 0.2
            if any(word in response for word in ["cannot", "can't", "instead", "however"]): score += 0.2
            if any(word in response for word in ["help", "suggest", "alternative"]): score += 0.1
            
            score = min(1.0, max(0.0, score))
            quality_scores.append(score)
            
            if score >= self.quality_thresholds["minimum_quality"]:
                filtered.append(conv)
        
        # Save filtered data
        filtered_path = dataset_path.replace('.jsonl', '_filtered.jsonl')
        with open(filtered_path, 'w') as f:
            for conv in filtered:
                f.write(json.dumps(conv) + '\n')
        
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        return filtered_path, avg_quality
    
    def _load_sample_examples(self, dataset_path: str, max_samples: int) -> List[Dict[str, str]]:
        """Load sample examples"""
        samples = []
        try:
            with open(dataset_path, 'r') as f:
                for i, line in enumerate(f):
                    if i >= max_samples: break
                    conv = json.loads(line)
                    samples.append({
                        "prompt": conv["messages"][0]["content"][:100] + "...",
                        "response": conv["messages"][-1]["content"][:150] + "..."
                    })
        except: pass
        return samples
    
    def _count_examples(self, dataset_path: str) -> int:
        """Count examples in dataset"""
        try:
            with open(dataset_path, 'r') as f:
                return sum(1 for line in f if line.strip())
        except:
            return 0


__all__ = ["Pharmacist", "CureDataResult"]