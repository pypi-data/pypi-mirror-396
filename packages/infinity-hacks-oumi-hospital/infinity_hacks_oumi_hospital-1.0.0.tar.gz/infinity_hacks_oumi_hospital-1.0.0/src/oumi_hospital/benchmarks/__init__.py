"""
🏥 Oumi Hospital Benchmarks

Red-team attacks and skill preservation tests for model evaluation.
All benchmarks use Oumi Conversation format and custom evaluation functions.
"""

from .red_team import (
    SafetyAttacks,
    HallucinationTriggers,
    BiasProbes,
    get_red_team_dataset,
    save_red_team_dataset
)

from .skill_tests import (
    MathReasoningTests,
    LogicalReasoningTests,
    CreativeWritingTests,
    FactualKnowledgeTests,
    get_skill_test_dataset,
    save_skill_test_dataset
)

from .judges import (
    safety_judge,
    hallucination_judge,
    quality_judge,
    math_accuracy_judge,
    bias_judge,
    run_comprehensive_evaluation
)

from .dataset_utils import (
    save_conversations_to_jsonl,
    load_conversations_from_jsonl,
    create_benchmark_suite,
    create_evaluation_config_templates,
    validate_benchmark_dataset,
    create_demo_datasets
)

__all__ = [
    # Red Team Attacks
    "SafetyAttacks",
    "HallucinationTriggers",
    "BiasProbes",
    "get_red_team_dataset",
    "save_red_team_dataset",
    
    # Skill Tests
    "MathReasoningTests",
    "LogicalReasoningTests", 
    "CreativeWritingTests",
    "FactualKnowledgeTests",
    "get_skill_test_dataset",
    "save_skill_test_dataset",
    
    # Custom Judges
    "safety_judge",
    "hallucination_judge",
    "quality_judge",
    "math_accuracy_judge", 
    "bias_judge",
    "run_comprehensive_evaluation",
    
    # Dataset Utilities
    "save_conversations_to_jsonl",
    "load_conversations_from_jsonl",
    "create_benchmark_suite",
    "create_evaluation_config_templates",
    "validate_benchmark_dataset",
    "create_demo_datasets"
]