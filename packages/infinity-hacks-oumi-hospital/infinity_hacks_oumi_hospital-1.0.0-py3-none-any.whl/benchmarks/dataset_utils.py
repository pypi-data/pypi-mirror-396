"""
🏥 Oumi Hospital - Benchmark Dataset Utilities

Utilities for managing, formatting, and saving benchmark datasets in Oumi format.
"""

import json
import random
from pathlib import Path
from typing import List, Dict, Any, Optional
from oumi.core.types.conversation import Conversation, Message, Role

from .red_team import get_red_team_dataset
from .skill_tests import get_skill_test_dataset


def save_conversations_to_jsonl(
    conversations: List[Conversation], 
    output_path: str,
    include_metadata: bool = True
) -> None:
    """
    Save conversations to JSONL file in Oumi format
    
    Args:
        conversations: List of Conversation objects
        output_path: Path to save JSONL file
        include_metadata: Whether to include metadata in output
    """
    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for conv in conversations:
            # Convert to dict format for JSON serialization
            conv_dict = {
                "messages": [
                    {
                        "role": msg.role.value,
                        "content": msg.content
                    }
                    for msg in conv.messages
                ]
            }
            
            # Add metadata if present and requested
            if include_metadata and hasattr(conv, 'metadata') and conv.metadata:
                conv_dict["metadata"] = conv.metadata
            
            f.write(json.dumps(conv_dict, ensure_ascii=False) + '\n')
    
    print(f"✅ Saved {len(conversations)} conversations to {output_path}")


def load_conversations_from_jsonl(input_path: str) -> List[Conversation]:
    """
    Load conversations from JSONL file
    
    Args:
        input_path: Path to JSONL file
        
    Returns:
        List of Conversation objects
    """
    conversations = []
    
    with open(input_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                data = json.loads(line.strip())
                
                # Convert messages
                messages = []
                for msg_data in data["messages"]:
                    role = Role(msg_data["role"])
                    content = msg_data["content"]
                    messages.append(Message(role=role, content=content))
                
                # Create conversation
                conv = Conversation(messages=messages)
                
                # Add metadata if present
                if "metadata" in data:
                    conv.metadata = data["metadata"]
                
                conversations.append(conv)
                
            except Exception as e:
                print(f"⚠️ Error parsing line {line_num}: {e}")
                continue
    
    print(f"✅ Loaded {len(conversations)} conversations from {input_path}")
    return conversations


def create_benchmark_suite(
    output_dir: str = "benchmarks",
    red_team_samples: int = 50,
    skill_test_samples: int = 50
) -> Dict[str, str]:
    """
    Create complete benchmark suite with all datasets
    
    Args:
        output_dir: Directory to save benchmark files
        red_team_samples: Number of red-team samples per symptom
        skill_test_samples: Number of skill test samples per domain
        
    Returns:
        Dictionary mapping benchmark names to file paths
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    benchmark_files = {}
    
    print("🏥 Creating Oumi Hospital Benchmark Suite...")
    
    # Red-team attack datasets
    red_team_symptoms = ["safety", "hallucination", "bias"]
    for symptom in red_team_symptoms:
        conversations = get_red_team_dataset(symptom)
        
        # Sample if too many
        if len(conversations) > red_team_samples:
            conversations = random.sample(conversations, red_team_samples)
        
        file_path = output_path / f"red_team_{symptom}.jsonl"
        save_conversations_to_jsonl(conversations, str(file_path))
        benchmark_files[f"red_team_{symptom}"] = str(file_path)
    
    # Skill preservation test datasets
    skill_domains = ["math", "reasoning", "writing", "factual"]
    for domain in skill_domains:
        conversations = get_skill_test_dataset(domain, skill_test_samples)
        
        file_path = output_path / f"skill_test_{domain}.jsonl"
        save_conversations_to_jsonl(conversations, str(file_path))
        benchmark_files[f"skill_test_{domain}"] = str(file_path)
    
    # Combined datasets
    all_red_team = get_red_team_dataset("all")
    if len(all_red_team) > red_team_samples * 3:
        all_red_team = random.sample(all_red_team, red_team_samples * 3)
    
    file_path = output_path / "red_team_all.jsonl"
    save_conversations_to_jsonl(all_red_team, str(file_path))
    benchmark_files["red_team_all"] = str(file_path)
    
    all_skills = get_skill_test_dataset("all", skill_test_samples * 4)
    file_path = output_path / "skill_test_all.jsonl"
    save_conversations_to_jsonl(all_skills, str(file_path))
    benchmark_files["skill_test_all"] = str(file_path)
    
    # Create benchmark manifest
    manifest = {
        "benchmark_suite": "Oumi Hospital",
        "version": "1.0",
        "description": "Comprehensive benchmark suite for model diagnosis and skill preservation",
        "created_by": "Oumi Hospital Team",
        "datasets": {
            name: {
                "path": path,
                "type": "red_team" if "red_team" in name else "skill_test",
                "format": "oumi_conversation_jsonl",
                "samples": len(load_conversations_from_jsonl(path))
            }
            for name, path in benchmark_files.items()
        }
    }
    
    manifest_path = output_path / "benchmark_manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Benchmark suite created in {output_dir}/")
    print(f"📋 Manifest saved to {manifest_path}")
    print(f"📊 Total datasets: {len(benchmark_files)}")
    
    return benchmark_files


def create_evaluation_config_templates(output_dir: str = "configs") -> Dict[str, str]:
    """
    Create Oumi evaluation config templates for each benchmark
    
    Args:
        output_dir: Directory to save config files
        
    Returns:
        Dictionary mapping config names to file paths
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    config_files = {}
    
    # Safety evaluation config
    safety_config = """
model:
  model_name: "meta-llama/Llama-3.1-8B-Instruct"
  trust_remote_code: true

engine: VLLM

generation:
  max_new_tokens: 512
  temperature: 0.0

tasks:
  - evaluation_backend: custom
    task_name: safety_judge

output_dir: "./evaluation_results/safety"
"""
    
    safety_path = output_path / "safety_evaluation.yaml"
    with open(safety_path, 'w') as f:
        f.write(safety_config.strip())
    config_files["safety_evaluation"] = str(safety_path)
    
    # Hallucination evaluation config
    hallucination_config = """
model:
  model_name: "meta-llama/Llama-3.1-8B-Instruct"
  trust_remote_code: true

engine: VLLM

generation:
  max_new_tokens: 512
  temperature: 0.0

tasks:
  - evaluation_backend: custom
    task_name: hallucination_judge

output_dir: "./evaluation_results/hallucination"
"""
    
    hallucination_path = output_path / "hallucination_evaluation.yaml"
    with open(hallucination_path, 'w') as f:
        f.write(hallucination_config.strip())
    config_files["hallucination_evaluation"] = str(hallucination_path)
    
    # Comprehensive evaluation config
    comprehensive_config = """
model:
  model_name: "meta-llama/Llama-3.1-8B-Instruct"
  trust_remote_code: true

engine: VLLM

generation:
  max_new_tokens: 512
  temperature: 0.0

tasks:
  - evaluation_backend: custom
    task_name: safety_judge
  - evaluation_backend: custom
    task_name: hallucination_judge
  - evaluation_backend: custom
    task_name: quality_judge
  - evaluation_backend: custom
    task_name: bias_judge

output_dir: "./evaluation_results/comprehensive"
"""
    
    comprehensive_path = output_path / "comprehensive_evaluation.yaml"
    with open(comprehensive_path, 'w') as f:
        f.write(comprehensive_config.strip())
    config_files["comprehensive_evaluation"] = str(comprehensive_path)
    
    print(f"✅ Created {len(config_files)} evaluation config templates in {output_dir}/")
    
    return config_files


def validate_benchmark_dataset(file_path: str) -> Dict[str, Any]:
    """
    Validate a benchmark dataset file
    
    Args:
        file_path: Path to JSONL benchmark file
        
    Returns:
        Validation report
    """
    try:
        conversations = load_conversations_from_jsonl(file_path)
        
        # Validation checks
        total_conversations = len(conversations)
        empty_conversations = sum(1 for conv in conversations if not conv.messages)
        single_message_conversations = sum(1 for conv in conversations if len(conv.messages) == 1)
        conversations_with_metadata = sum(1 for conv in conversations if hasattr(conv, 'metadata') and conv.metadata)
        
        # Content analysis
        avg_message_length = 0
        if conversations:
            total_length = sum(len(msg.content) for conv in conversations for msg in conv.messages)
            total_messages = sum(len(conv.messages) for conv in conversations)
            avg_message_length = total_length / total_messages if total_messages > 0 else 0
        
        validation_report = {
            "file_path": file_path,
            "is_valid": True,
            "total_conversations": total_conversations,
            "empty_conversations": empty_conversations,
            "single_message_conversations": single_message_conversations,
            "conversations_with_metadata": conversations_with_metadata,
            "average_message_length": avg_message_length,
            "issues": []
        }
        
        # Check for issues
        if empty_conversations > 0:
            validation_report["issues"].append(f"{empty_conversations} empty conversations found")
        
        if avg_message_length < 10:
            validation_report["issues"].append("Average message length is very short")
        
        if total_conversations == 0:
            validation_report["is_valid"] = False
            validation_report["issues"].append("No conversations found in file")
        
        return validation_report
        
    except Exception as e:
        return {
            "file_path": file_path,
            "is_valid": False,
            "error": str(e),
            "issues": [f"Failed to load file: {e}"]
        }


def create_demo_datasets(output_dir: str = "demo_data") -> Dict[str, str]:
    """
    Create small demo datasets for testing and demonstration
    
    Args:
        output_dir: Directory to save demo files
        
    Returns:
        Dictionary mapping demo dataset names to file paths
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    demo_files = {}
    
    # Small safety demo (5 samples)
    safety_demo = get_red_team_dataset("safety")[:5]
    demo_path = output_path / "demo_safety.jsonl"
    save_conversations_to_jsonl(safety_demo, str(demo_path))
    demo_files["demo_safety"] = str(demo_path)
    
    # Small math demo (5 samples)
    math_demo = get_skill_test_dataset("math", 5)
    demo_path = output_path / "demo_math.jsonl"
    save_conversations_to_jsonl(math_demo, str(demo_path))
    demo_files["demo_math"] = str(demo_path)
    
    print(f"✅ Created demo datasets in {output_dir}/")
    
    return demo_files


# Export main functions
__all__ = [
    "save_conversations_to_jsonl",
    "load_conversations_from_jsonl",
    "create_benchmark_suite",
    "create_evaluation_config_templates",
    "validate_benchmark_dataset",
    "create_demo_datasets"
]