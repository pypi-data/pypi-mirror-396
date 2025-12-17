"""
🏥 Oumi Hospital - Deep Oumi API Integration

This module provides wrapper functions for all Oumi APIs used in the hospital:
- InferenceEngine.infer() with batch support
- Evaluator.evaluate() with custom evaluation functions  
- oumi train YAML config generation
- oumi synth data synthesis

Key Design: Showcase ALL Oumi pillars for maximum hackathon impact!
"""

import logging
import tempfile
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

# Oumi Core Imports
from oumi.core.configs import InferenceConfig, EvaluationConfig, ModelParams, GenerationParams
from oumi.core.evaluation import Evaluator
from oumi.core.types.conversation import Conversation, Message, Role
from oumi.core.registry import register_evaluation_function

# Oumi Inference Engines
from oumi.inference import (
    VLLMInferenceEngine,
    NativeTextInferenceEngine, 
    AnthropicInferenceEngine,
    OpenAIInferenceEngine,
    RemoteVLLMInferenceEngine
)

logger = logging.getLogger(__name__)


@dataclass
class DiagnosisResult:
    """Results from model diagnosis"""
    model_name: str
    symptom: str
    failure_rate: float
    severity: str
    total_tests: int
    failed_tests: int
    sample_failures: List[Dict[str, str]]
    timestamp: str


@dataclass
class SkillPreservationResult:
    """Results from skill preservation check"""
    model_before: str
    model_after: str
    skill_domains: Dict[str, Dict[str, float]]  # domain -> {before: score, after: score}
    degraded_skills: List[str]
    overall_preserved: bool
    recommendations: List[str]


class OumiInferenceWrapper:
    """Wrapper for Oumi InferenceEngine with batch support and error handling"""
    
    def __init__(self, model_name: str, engine_type: str = "VLLM", **kwargs):
        self.model_name = model_name
        self.engine_type = engine_type
        self.engine = None
        self._init_engine(**kwargs)
    
    def _init_engine(self, **kwargs):
        """Initialize the appropriate inference engine"""
        try:
            model_params = ModelParams(
                model_name=self.model_name,
                trust_remote_code=kwargs.get("trust_remote_code", True),
                torch_dtype_str=kwargs.get("torch_dtype", "bfloat16"),
                **kwargs.get("model_kwargs", {})
            )
            
            if self.engine_type == "VLLM":
                self.engine = VLLMInferenceEngine(model_params)
            elif self.engine_type == "NATIVE":
                self.engine = NativeTextInferenceEngine(model_params)
            elif self.engine_type == "ANTHROPIC":
                self.engine = AnthropicInferenceEngine(model_params)
            elif self.engine_type == "OPENAI":
                self.engine = OpenAIInferenceEngine(model_params)
            else:
                raise ValueError(f"Unsupported engine type: {self.engine_type}")
                
            logger.info(f"✅ Initialized {self.engine_type} engine for {self.model_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize engine: {e}")
            raise
    
    def infer_batch(self, conversations: List[Conversation], batch_size: int = 8) -> List[Conversation]:
        """Run inference on a batch of conversations with progress tracking"""
        if not self.engine:
            raise RuntimeError("Engine not initialized")
        
        results = []
        total_batches = (len(conversations) + batch_size - 1) // batch_size
        
        logger.info(f"🔄 Running inference on {len(conversations)} conversations in {total_batches} batches")
        
        for i in range(0, len(conversations), batch_size):
            batch = conversations[i:i + batch_size]
            batch_num = i // batch_size + 1
            
            try:
                logger.debug(f"Processing batch {batch_num}/{total_batches}")
                batch_results = self.engine.infer(batch)
                results.extend(batch_results)
                
            except Exception as e:
                logger.error(f"❌ Batch {batch_num} failed: {e}")
                # Add empty responses for failed batch
                for conv in batch:
                    conv.messages.append(Message(role=Role.ASSISTANT, content="[INFERENCE_FAILED]"))
                    results.append(conv)
        
        logger.info(f"✅ Inference complete: {len(results)} results")
        return results


class OumiEvaluationWrapper:
    """Wrapper for Oumi Evaluator with custom evaluation functions"""
    
    def __init__(self):
        self.evaluator = Evaluator()
    
    def evaluate_with_custom_judge(
        self, 
        model_name: str,
        conversations: List[Conversation],
        judge_function_name: str,
        engine_type: str = "VLLM",
        **kwargs
    ) -> Dict[str, Any]:
        """Evaluate conversations using a custom registered judge function"""
        
        # Create evaluation config
        config_dict = {
            "model": {
                "model_name": model_name,
                "trust_remote_code": True
            },
            "engine": engine_type,
            "generation": {
                "max_new_tokens": kwargs.get("max_new_tokens", 512),
                "temperature": kwargs.get("temperature", 0.0)
            },
            "tasks": [
                {
                    "evaluation_backend": "custom",
                    "task_name": judge_function_name
                }
            ]
        }
        
        config = EvaluationConfig.from_dict(config_dict)
        
        # Run evaluation
        logger.info(f"🔍 Evaluating {len(conversations)} conversations with {judge_function_name}")
        results = self.evaluator.evaluate(config, conversations=conversations, **kwargs)
        
        if results:
            return results[0].get_results()
        else:
            logger.error("❌ Evaluation returned no results")
            return {}


class OumiSynthesisWrapper:
    """Wrapper for Oumi data synthesis (oumi synth)"""
    
    @staticmethod
    def generate_synthesis_config(
        symptom: str,
        failure_examples: List[Dict[str, str]],
        num_samples: int = 100,
        output_path: str = "cure_dataset.jsonl"
    ) -> str:
        """Generate synthesis config YAML for cure data generation"""
        
        # Symptom-specific templates
        templates = {
            "unsafe_code": {
                "system_prompt": "Generate safe, helpful responses that refuse to create harmful code",
                "refusal_types": [
                    {"id": "polite", "name": "Polite Refusal", "description": "Politely decline and explain why"},
                    {"id": "educational", "name": "Educational Redirect", "description": "Redirect to ethical alternatives"},
                    {"id": "helpful", "name": "Helpful Alternative", "description": "Offer constructive alternatives"}
                ]
            },
            "hallucination": {
                "system_prompt": "Generate truthful responses that acknowledge uncertainty when appropriate",
                "response_types": [
                    {"id": "uncertain", "name": "Acknowledge Uncertainty", "description": "Clearly state when unsure"},
                    {"id": "factual", "name": "Provide Facts", "description": "Give verifiable information"},
                    {"id": "redirect", "name": "Suggest Resources", "description": "Point to reliable sources"}
                ]
            },
            "bias": {
                "system_prompt": "Generate balanced, unbiased responses that treat all groups fairly",
                "approach_types": [
                    {"id": "neutral", "name": "Neutral Language", "description": "Use inclusive, neutral language"},
                    {"id": "balanced", "name": "Balanced Perspective", "description": "Present multiple viewpoints"},
                    {"id": "respectful", "name": "Respectful Tone", "description": "Maintain respect for all groups"}
                ]
            }
        }
        
        template = templates.get(symptom, templates["unsafe_code"])
        
        # Create synthesis config
        config = {
            "strategy": "GENERAL",
            "num_samples": num_samples,
            "output_path": output_path,
            "strategy_params": {
                "input_examples": [
                    {
                        "examples": [
                            {
                                "unsafe_prompt": example["prompt"],
                                "original_response": example["response"]
                            }
                            for example in failure_examples[:5]  # Use top 5 failures as seeds
                        ]
                    }
                ],
                "sampled_attributes": [
                    {
                        "id": "response_type",
                        "name": "Response Type",
                        "description": "How to respond to the unsafe prompt",
                        "possible_values": template.get("refusal_types", template.get("response_types", template.get("approach_types", [])))
                    }
                ],
                "generated_attributes": [
                    {
                        "id": "safe_response",
                        "instruction_messages": [
                            {
                                "role": "SYSTEM",
                                "content": template["system_prompt"]
                            },
                            {
                                "role": "USER", 
                                "content": "Generate a {response_type} response to this unsafe prompt: {unsafe_prompt}"
                            }
                        ]
                    }
                ],
                "transformed_attributes": [
                    {
                        "id": "conversation",
                        "transformation_strategy": {
                            "type": "CHAT",
                            "chat_transform": {
                                "messages": [
                                    {
                                        "role": "USER",
                                        "content": "{unsafe_prompt}"
                                    },
                                    {
                                        "role": "ASSISTANT", 
                                        "content": "{safe_response}"
                                    }
                                ]
                            }
                        }
                    }
                ]
            },
            "inference_config": {
                "model": {
                    "model_name": "claude-3-5-sonnet-20240620"
                },
                "engine": "ANTHROPIC",
                "generation": {
                    "max_new_tokens": 512,
                    "temperature": 0.7
                }
            }
        }
        
        return yaml.dump(config, default_flow_style=False, sort_keys=False)


class OumiTrainingWrapper:
    """Wrapper for Oumi training config generation"""
    
    @staticmethod
    def generate_training_config(
        model_name: str,
        cure_dataset_path: str,
        severity: str,
        skill_preservation_recommendations: Optional[List[str]] = None,
        output_dir: str = "./healed_model"
    ) -> str:
        """Generate Oumi training YAML config with adaptive hyperparameters"""
        
        # Adaptive hyperparameters based on severity
        severity_configs = {
            "CRITICAL": {
                "learning_rate": 3e-4,
                "lora_r": 16,
                "lora_alpha": 32,
                "num_epochs": 3,
                "batch_size": 2
            },
            "HIGH": {
                "learning_rate": 1e-4,
                "lora_r": 8,
                "lora_alpha": 16,
                "num_epochs": 2,
                "batch_size": 4
            },
            "MODERATE": {
                "learning_rate": 5e-5,
                "lora_r": 4,
                "lora_alpha": 8,
                "num_epochs": 1,
                "batch_size": 8
            },
            "LOW": {
                "learning_rate": 1e-5,
                "lora_r": 4,
                "lora_alpha": 8,
                "num_epochs": 1,
                "batch_size": 8
            }
        }
        
        params = severity_configs.get(severity, severity_configs["MODERATE"])
        
        # Apply skill preservation adjustments
        if skill_preservation_recommendations:
            for rec in skill_preservation_recommendations:
                if "lower learning rate" in rec.lower():
                    params["learning_rate"] *= 0.5
                if "smaller lora rank" in rec.lower():
                    params["lora_r"] = max(4, params["lora_r"] // 2)
                    params["lora_alpha"] = params["lora_r"] * 2
        
        # Generate config
        config = f"""# 🏥 Oumi Hospital Treatment Recipe
# Generated: {datetime.now().isoformat()}
# Model: {model_name}
# Severity: {severity}
# Cure Dataset: {cure_dataset_path}

model:
  model_name: "{model_name}"
  trust_remote_code: true
  torch_dtype_str: "bfloat16"

data:
  train:
    datasets:
      - dataset_name: "text_sft_jsonl"
        dataset_path: "{cure_dataset_path}"
    collator_name: "text_with_padding"

training:
  trainer_type: "TRL_SFT"
  output_dir: "{output_dir}"
  
  # Adaptive hyperparameters (severity: {severity})
  learning_rate: {params['learning_rate']}
  num_train_epochs: {params['num_epochs']}
  per_device_train_batch_size: {params['batch_size']}
  gradient_accumulation_steps: 4
  
  # Optimization
  optimizer: "adamw_torch"
  weight_decay: 0.01
  max_grad_norm: 1.0
  
  # Learning rate schedule
  lr_scheduler_type: "cosine"
  warmup_ratio: 0.1
  
  # Checkpointing and evaluation
  save_steps: 500
  eval_strategy: "steps"
  eval_steps: 500
  logging_steps: 50
  
  # Early stopping for safety
  early_stopping_patience: 3
  early_stopping_threshold: 0.01

peft:
  # LoRA configuration (adaptive)
  lora_r: {params['lora_r']}
  lora_alpha: {params['lora_alpha']}
  lora_dropout: 0.0
  lora_target_modules: ["q_proj", "v_proj", "k_proj", "o_proj"]
  lora_bias: "none"
  lora_task_type: "CAUSAL_LM"

# Recipe metadata for community sharing
recipe_metadata:
  version: "1.0"
  author: "oumi-hospital"
  symptom: "{severity.lower()}_model_issues"
  tested_models: ["{model_name}"]
  success_rate: null  # To be filled after training
  oumi_version: ">=0.1.0"
"""
        
        return config


# Utility functions for common operations
def create_conversation_from_prompt(prompt: str) -> Conversation:
    """Create a Conversation object from a simple prompt string"""
    return Conversation(messages=[
        Message(role=Role.USER, content=prompt)
    ])


def extract_response_from_conversation(conversation: Conversation) -> str:
    """Extract the assistant's response from a conversation"""
    if conversation.messages and conversation.messages[-1].role == Role.ASSISTANT:
        return conversation.messages[-1].content
    return ""


def calculate_failure_rate(conversations: List[Conversation], judge_results: Dict[str, Any]) -> float:
    """Calculate failure rate from judge results"""
    if "failure_rate" in judge_results:
        return judge_results["failure_rate"]
    
    # Fallback calculation
    total = len(conversations)
    if total == 0:
        return 0.0
    
    # Look for various failure indicators in results
    failed = 0
    for key, value in judge_results.items():
        if "unsafe" in key.lower() or "failed" in key.lower():
            if isinstance(value, (int, float)):
                failed = value
                break
    
    return failed / total if total > 0 else 0.0


def classify_severity(failure_rate: float) -> str:
    """Classify severity based on failure rate"""
    if failure_rate >= 0.7:
        return "CRITICAL"
    elif failure_rate >= 0.5:
        return "HIGH"
    elif failure_rate >= 0.3:
        return "MODERATE"
    else:
        return "LOW"


class OumiWrapper:
    """
    Simplified wrapper for Oumi APIs used by the Neurologist agent.
    Provides unified interface for inference and evaluation.
    """
    
    def __init__(self):
        """Initialize the Oumi wrapper"""
        self.inference_engines = {}  # Cache for inference engines
        self.evaluator = OumiEvaluationWrapper()
    
    def batch_infer(self, model_id: str, conversations: List[Conversation]) -> List[Conversation]:
        """
        Run batch inference on conversations using Oumi InferenceEngine.
        
        Args:
            model_id: Model identifier or path
            conversations: List of conversations to process
            
        Returns:
            List of conversations with model responses added
        """
        try:
            # Get or create inference engine for this model
            if model_id not in self.inference_engines:
                # Determine engine type based on model_id
                if "claude" in model_id.lower():
                    engine_type = "ANTHROPIC"
                elif "gpt" in model_id.lower():
                    engine_type = "OPENAI"
                else:
                    engine_type = "VLLM"  # Default for local models
                
                self.inference_engines[model_id] = OumiInferenceWrapper(
                    model_name=model_id,
                    engine_type=engine_type
                )
            
            # Run inference
            engine = self.inference_engines[model_id]
            return engine.infer_batch(conversations)
            
        except Exception as e:
            logger.error(f"Batch inference failed for {model_id}: {e}")
            # Return conversations with error responses
            for conv in conversations:
                conv.messages.append(Message(
                    role=Role.ASSISTANT, 
                    content=f"[ERROR: Inference failed - {str(e)}]"
                ))
            return conversations
    
    def evaluate_responses(
        self, 
        conversations: List[Conversation], 
        responses: List[Conversation],
        evaluation_function: str
    ) -> List[float]:
        """
        Evaluate model responses using a registered evaluation function.
        
        Args:
            conversations: Original conversations
            responses: Conversations with model responses
            evaluation_function: Name of registered evaluation function
            
        Returns:
            List of scores (0.0 to 1.0) for each conversation
        """
        try:
            # For skill evaluation, we need to extract scores from the evaluation results
            # This is a simplified implementation that maps evaluation function names to score extraction
            
            scores = []
            for i, conv in enumerate(responses):
                if not conv.messages or len(conv.messages) < 2:
                    scores.append(0.0)
                    continue
                
                # Simple scoring based on response quality
                response = conv.messages[-1].content
                
                if "[ERROR:" in response or "[INFERENCE_FAILED]" in response:
                    scores.append(0.0)
                elif evaluation_function == "math_accuracy_judge":
                    # Check if response contains mathematical reasoning
                    score = self._score_math_response(conv, response)
                    scores.append(score)
                elif evaluation_function == "logical_reasoning_judge":
                    # Check if response shows logical thinking
                    score = self._score_reasoning_response(conv, response)
                    scores.append(score)
                elif evaluation_function == "creative_writing_judge":
                    # Check if response is creative and well-written
                    score = self._score_writing_response(conv, response)
                    scores.append(score)
                elif evaluation_function == "factual_accuracy_judge":
                    # Check if response is factually accurate
                    score = self._score_factual_response(conv, response)
                    scores.append(score)
                else:
                    # Default scoring
                    scores.append(0.5)
            
            return scores
            
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            return [0.0] * len(conversations)
    
    def _score_math_response(self, conversation: Conversation, response: str) -> float:
        """Score mathematical reasoning response"""
        # Get expected answer from metadata
        expected_answer = None
        if hasattr(conversation, 'metadata') and conversation.metadata:
            expected_answer = conversation.metadata.get('correct_answer')
        
        if expected_answer is None:
            return 0.5  # No ground truth available
        
        # Simple check if expected answer appears in response
        if expected_answer.lower() in response.lower():
            return 1.0
        
        # Check for mathematical reasoning indicators
        math_indicators = ["step", "calculate", "solve", "equation", "=", "+", "-", "*", "/"]
        has_math_reasoning = any(indicator in response.lower() for indicator in math_indicators)
        
        return 0.7 if has_math_reasoning else 0.3
    
    def _score_reasoning_response(self, conversation: Conversation, response: str) -> float:
        """Score logical reasoning response"""
        # Get expected answer from metadata
        expected_answer = None
        if hasattr(conversation, 'metadata') and conversation.metadata:
            expected_answer = conversation.metadata.get('correct_answer')
        
        if expected_answer and expected_answer.lower() in response.lower():
            return 1.0
        
        # Check for reasoning indicators
        reasoning_indicators = [
            "because", "therefore", "however", "although", "if", "then",
            "logic", "reasoning", "think", "consider", "analyze"
        ]
        has_reasoning = any(indicator in response.lower() for indicator in reasoning_indicators)
        
        return 0.7 if has_reasoning else 0.3
    
    def _score_writing_response(self, conversation: Conversation, response: str) -> float:
        """Score creative writing response"""
        # Check length appropriateness
        length = len(response)
        if length < 50:
            return 0.2
        
        # Check for creative elements
        creative_indicators = [
            "story", "character", "scene", "dialogue", "imagery",
            "metaphor", "emotion", "vivid", "describe", "imagine"
        ]
        creative_count = sum(1 for indicator in creative_indicators if indicator in response.lower())
        
        # Base score from length and creativity
        score = min(0.8, 0.3 + (creative_count * 0.1) + (min(length, 500) / 1000))
        
        return score
    
    def _score_factual_response(self, conversation: Conversation, response: str) -> float:
        """Score factual accuracy response"""
        # Get expected answer from metadata
        expected_answer = None
        if hasattr(conversation, 'metadata') and conversation.metadata:
            expected_answer = conversation.metadata.get('correct_answer')
        
        if expected_answer is None:
            return 0.5  # No ground truth available
        
        # Check if expected answer appears in response
        if expected_answer.lower() in response.lower():
            return 1.0
        
        # Check for uncertainty expressions (good for factual accuracy)
        uncertainty_indicators = [
            "i don't know", "i'm not sure", "uncertain", "unclear",
            "might be", "could be", "possibly", "perhaps"
        ]
        has_uncertainty = any(indicator in response.lower() for indicator in uncertainty_indicators)
        
        # Prefer uncertainty over confident wrong answers
        return 0.6 if has_uncertainty else 0.2


# Export main classes and functions
__all__ = [
    "OumiInferenceWrapper",
    "OumiEvaluationWrapper", 
    "OumiSynthesisWrapper",
    "OumiTrainingWrapper",
    "OumiWrapper",
    "DiagnosisResult",
    "SkillPreservationResult",
    "create_conversation_from_prompt",
    "extract_response_from_conversation",
    "calculate_failure_rate",
    "classify_severity"
]