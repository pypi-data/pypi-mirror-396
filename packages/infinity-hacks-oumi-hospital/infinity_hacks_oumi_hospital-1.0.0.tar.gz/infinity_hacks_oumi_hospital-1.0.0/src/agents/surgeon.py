"""
🔧 The Surgeon - Training Recipe Generation Agent

This agent generates Oumi training configurations with adaptive hyperparameters
based on diagnosis severity and skill preservation analysis.
"""

import json
import logging
import yaml
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.utils.console import hospital_console
from src.utils.oumi_integration import OumiTrainingWrapper

logger = logging.getLogger(__name__)
console = hospital_console.console


@dataclass
class TrainingRecipe:
    """Complete training recipe with metadata"""
    recipe_id: str
    model_name: str
    symptom: str
    severity: str
    cure_dataset_path: str
    config_yaml: str
    hyperparameters: Dict[str, Any]
    skill_adjustments: List[str]
    metadata: Dict[str, Any]
    output_path: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "recipe_id": self.recipe_id,
            "model_name": self.model_name,
            "symptom": self.symptom,
            "severity": self.severity,
            "cure_dataset_path": self.cure_dataset_path,
            "hyperparameters": self.hyperparameters,
            "skill_adjustments": self.skill_adjustments,
            "metadata": self.metadata,
            "output_path": self.output_path,
            "config_preview": self.config_yaml[:500] + "..." if len(self.config_yaml) > 500 else self.config_yaml
        }


class Surgeon:
    """
    The Surgeon generates Oumi training recipes with adaptive hyperparameters.
    
    Key capabilities:
    - Severity-based hyperparameter calculation
    - Skill preservation adjustments
    - Complete Oumi training YAML generation
    - Community recipe metadata
    - Rich terminal output with reasoning
    """
    
    def __init__(self):
        """Initialize the Surgeon"""
        self.training_wrapper = OumiTrainingWrapper()
        
        # Base hyperparameter configurations by severity
        self.severity_configs = {
            "CRITICAL": {
                "learning_rate": 3e-4,
                "lora_r": 16,
                "lora_alpha": 32,
                "num_epochs": 3,
                "batch_size": 2,
                "gradient_accumulation_steps": 8,
                "warmup_ratio": 0.05,
                "weight_decay": 0.01,
                "max_grad_norm": 0.5
            },
            "HIGH": {
                "learning_rate": 1e-4,
                "lora_r": 8,
                "lora_alpha": 16,
                "num_epochs": 2,
                "batch_size": 4,
                "gradient_accumulation_steps": 4,
                "warmup_ratio": 0.1,
                "weight_decay": 0.01,
                "max_grad_norm": 1.0
            },
            "MODERATE": {
                "learning_rate": 5e-5,
                "lora_r": 4,
                "lora_alpha": 8,
                "num_epochs": 1,
                "batch_size": 8,
                "gradient_accumulation_steps": 2,
                "warmup_ratio": 0.1,
                "weight_decay": 0.005,
                "max_grad_norm": 1.0
            },
            "LOW": {
                "learning_rate": 1e-5,
                "lora_r": 4,
                "lora_alpha": 8,
                "num_epochs": 1,
                "batch_size": 8,
                "gradient_accumulation_steps": 1,
                "warmup_ratio": 0.1,
                "weight_decay": 0.001,
                "max_grad_norm": 1.0
            }
        }
    
    def generate_recipe(
        self,
        diagnosis_data: Dict[str, Any],
        cure_dataset_path: str,
        skill_preservation_data: Optional[Dict[str, Any]] = None,
        output_dir: str = "./healed_model",
        recipe_name: Optional[str] = None
    ) -> TrainingRecipe:
        """
        Generate a complete training recipe based on diagnosis and skill preservation.
        
        Args:
            diagnosis_data: Results from diagnostician agent
            cure_dataset_path: Path to cure dataset from pharmacist
            skill_preservation_data: Optional results from neurologist
            output_dir: Directory for trained model output
            recipe_name: Optional custom recipe name
            
        Returns:
            TrainingRecipe with complete configuration
        """
        console.print(Panel.fit(
            "🔧 [bold blue]Surgical Planning[/bold blue]\n"
            f"Generating adaptive training recipe...",
            border_style="blue"
        ))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            # Extract key information
            task = progress.add_task("Analyzing diagnosis and skill data...", total=None)
            
            model_name = diagnosis_data.get("model_name", "unknown-model")
            symptom = diagnosis_data.get("symptom", "unknown")
            severity = diagnosis_data.get("severity", "MODERATE")
            
            progress.update(task, description="Calculating base hyperparameters...")
            
            # Get base hyperparameters for severity
            base_params = self.severity_configs.get(severity, self.severity_configs["MODERATE"]).copy()
            
            progress.update(task, description="Applying skill preservation adjustments...")
            
            # Apply skill preservation adjustments
            skill_adjustments = []
            if skill_preservation_data:
                base_params, adjustments = self._apply_skill_adjustments(
                    base_params, skill_preservation_data
                )
                skill_adjustments = adjustments
            
            progress.update(task, description="Generating Oumi training configuration...")
            
            # Generate recipe ID
            if recipe_name:
                recipe_id = recipe_name
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                recipe_id = f"{symptom}_{severity.lower()}_{timestamp}"
            
            # Generate complete YAML configuration
            config_yaml = self._generate_oumi_config(
                model_name=model_name,
                cure_dataset_path=cure_dataset_path,
                hyperparameters=base_params,
                output_dir=output_dir,
                recipe_id=recipe_id,
                symptom=symptom,
                severity=severity
            )
            
            progress.update(task, description="Adding community metadata...")
            
            # Generate metadata for community sharing
            metadata = self._generate_recipe_metadata(
                recipe_id=recipe_id,
                model_name=model_name,
                symptom=symptom,
                severity=severity,
                hyperparameters=base_params,
                skill_adjustments=skill_adjustments
            )
            
            progress.update(task, description="✅ Recipe generation complete")
        
        # Create recipe object
        recipe = TrainingRecipe(
            recipe_id=recipe_id,
            model_name=model_name,
            symptom=symptom,
            severity=severity,
            cure_dataset_path=cure_dataset_path,
            config_yaml=config_yaml,
            hyperparameters=base_params,
            skill_adjustments=skill_adjustments,
            metadata=metadata,
            output_path=f"{output_dir}/{recipe_id}"
        )
        
        # Display results
        self._display_recipe_summary(recipe)
        
        return recipe
    
    def _apply_skill_adjustments(
        self, 
        base_params: Dict[str, Any], 
        skill_data: Dict[str, Any]
    ) -> tuple[Dict[str, Any], List[str]]:
        """
        Apply skill preservation adjustments to hyperparameters.
        
        Args:
            base_params: Base hyperparameters from severity
            skill_data: Skill preservation analysis results
            
        Returns:
            Tuple of (adjusted_params, adjustment_descriptions)
        """
        adjusted_params = base_params.copy()
        adjustments = []
        
        # Extract skill preservation info
        verdict = skill_data.get("verdict", "safe")
        overall_degradation = skill_data.get("overall_degradation", 0.0)
        degraded_skills = []
        
        if "skill_scores" in skill_data:
            degraded_skills = [
                score["domain"] for score in skill_data["skill_scores"]
                if score.get("status") == "degraded"
            ]
        
        # Apply adjustments based on verdict
        if verdict == "critical":
            # Aggressive adjustments for critical degradation
            adjusted_params["learning_rate"] *= 0.5  # Halve learning rate
            adjusted_params["lora_r"] = max(4, adjusted_params["lora_r"] // 2)  # Smaller LoRA rank
            adjusted_params["lora_alpha"] = adjusted_params["lora_r"] * 2
            adjusted_params["num_epochs"] = max(1, adjusted_params["num_epochs"] - 1)  # Fewer epochs
            adjusted_params["gradient_accumulation_steps"] *= 2  # More stable gradients
            
            adjustments.extend([
                f"🚨 CRITICAL degradation: Reduced LR to {adjusted_params['learning_rate']:.2e}",
                f"🔧 Reduced LoRA rank to {adjusted_params['lora_r']} for stability",
                f"⏱️ Reduced epochs to {adjusted_params['num_epochs']} to prevent overfitting",
                "📊 Increased gradient accumulation for stability"
            ])
            
        elif verdict == "caution":
            # Moderate adjustments for caution
            adjusted_params["learning_rate"] *= 0.75  # Reduce learning rate by 25%
            adjusted_params["warmup_ratio"] = min(0.2, adjusted_params["warmup_ratio"] * 1.5)  # More warmup
            
            adjustments.extend([
                f"⚠️ CAUTION: Reduced LR to {adjusted_params['learning_rate']:.2e}",
                f"🔥 Increased warmup to {adjusted_params['warmup_ratio']:.2f} for stability"
            ])
        
        # Domain-specific adjustments
        if "math" in degraded_skills:
            # Math skills need careful tuning
            adjusted_params["weight_decay"] *= 0.5  # Less regularization
            adjustments.append("📊 Math degradation: Reduced weight decay for numerical stability")
        
        if "reasoning" in degraded_skills:
            # Reasoning needs more careful training
            adjusted_params["max_grad_norm"] *= 0.5  # Stricter gradient clipping
            adjustments.append("🧩 Reasoning degradation: Stricter gradient clipping")
        
        if "writing" in degraded_skills:
            # Writing benefits from longer warmup
            adjusted_params["warmup_ratio"] = min(0.3, adjusted_params["warmup_ratio"] * 2)
            adjustments.append("✍️ Writing degradation: Extended warmup period")
        
        if len(degraded_skills) >= 3:
            # Multiple skill degradation - add replay buffer recommendation
            adjustments.append("🔄 Multiple skills degraded: Consider adding 30% original data as replay buffer")
        
        return adjusted_params, adjustments
    
    def _generate_oumi_config(
        self,
        model_name: str,
        cure_dataset_path: str,
        hyperparameters: Dict[str, Any],
        output_dir: str,
        recipe_id: str,
        symptom: str,
        severity: str
    ) -> str:
        """Generate complete Oumi training YAML configuration"""
        
        # Generate timestamp for metadata
        timestamp = datetime.now().isoformat()
        
        # Create comprehensive config
        config = {
            # Recipe metadata header
            "_recipe_metadata": {
                "recipe_id": recipe_id,
                "version": "1.0",
                "author": "oumi-hospital",
                "created": timestamp,
                "symptom": symptom,
                "severity": severity,
                "tested_models": [model_name],
                "success_rate": None,  # To be filled after training
                "oumi_version": ">=0.1.0",
                "description": f"Automated treatment recipe for {symptom} issues (severity: {severity})"
            },
            
            # Model configuration
            "model": {
                "model_name": model_name,
                "trust_remote_code": True,
                "torch_dtype_str": "bfloat16"
            },
            
            # Data configuration
            "data": {
                "train": {
                    "datasets": [
                        {
                            "dataset_name": "text_sft_jsonl",
                            "dataset_path": cure_dataset_path
                        }
                    ]
                },
                "collator_name": "text_with_padding"
            },
            
            # Training configuration
            "training": {
                "trainer_type": "TRL_SFT",
                "output_dir": f"{output_dir}/{recipe_id}",
                
                # Core hyperparameters (adaptive)
                "learning_rate": hyperparameters["learning_rate"],
                "num_train_epochs": hyperparameters["num_epochs"],
                "per_device_train_batch_size": hyperparameters["batch_size"],
                "gradient_accumulation_steps": hyperparameters["gradient_accumulation_steps"],
                
                # Optimization
                "optimizer": "adamw_torch",
                "weight_decay": hyperparameters["weight_decay"],
                "max_grad_norm": hyperparameters["max_grad_norm"],
                
                # Learning rate schedule
                "lr_scheduler_type": "cosine",
                "warmup_ratio": hyperparameters["warmup_ratio"],
                
                # Checkpointing and evaluation
                "save_steps": 500,
                "eval_strategy": "steps",
                "eval_steps": 500,
                "logging_steps": 50,
                "save_total_limit": 3,
                
                # Early stopping for safety
                "early_stopping_patience": 3,
                "early_stopping_threshold": 0.01,
                
                # Memory optimization
                "dataloader_pin_memory": False,
                "remove_unused_columns": False,
                "fp16": False,
                "bf16": True
            },
            
            # PEFT (LoRA) configuration
            "peft": {
                "lora_r": hyperparameters["lora_r"],
                "lora_alpha": hyperparameters["lora_alpha"],
                "lora_dropout": 0.0,
                "lora_target_modules": ["q_proj", "v_proj", "k_proj", "o_proj"],
                "lora_bias": "none",
                "lora_task_type": "CAUSAL_LM"
            }
        }
        
        # Convert to YAML with custom formatting
        yaml_str = yaml.dump(config, default_flow_style=False, sort_keys=False, indent=2)
        
        # Add header comment
        header = f"""# 🏥 Oumi Model Hospital - Treatment Recipe
# Generated: {timestamp}
# Recipe ID: {recipe_id}
# Model: {model_name}
# Symptom: {symptom} (Severity: {severity})
# Cure Dataset: {cure_dataset_path}
#
# This recipe was automatically generated by the Surgeon agent
# based on diagnosis severity and skill preservation analysis.
#
# Usage: oumi train {recipe_id}.yaml

"""
        
        return header + yaml_str
    
    def _generate_recipe_metadata(
        self,
        recipe_id: str,
        model_name: str,
        symptom: str,
        severity: str,
        hyperparameters: Dict[str, Any],
        skill_adjustments: List[str]
    ) -> Dict[str, Any]:
        """Generate metadata for community recipe sharing"""
        
        return {
            "recipe_id": recipe_id,
            "version": "1.0",
            "author": "oumi-hospital",
            "created": datetime.now().isoformat(),
            "symptom": symptom,
            "severity": severity,
            "base_model": model_name,
            "hyperparameters": {
                "learning_rate": hyperparameters["learning_rate"],
                "lora_r": hyperparameters["lora_r"],
                "lora_alpha": hyperparameters["lora_alpha"],
                "num_epochs": hyperparameters["num_epochs"],
                "batch_size": hyperparameters["batch_size"]
            },
            "skill_adjustments": skill_adjustments,
            "oumi_version": ">=0.1.0",
            "tags": [symptom, severity.lower(), "automated", "hospital"],
            "description": f"Automated treatment recipe for {symptom} issues with {severity.lower()} severity",
            "usage": f"oumi train {recipe_id}.yaml",
            "success_rate": None,  # To be filled after validation
            "community_tested": False
        }
    
    def _display_recipe_summary(self, recipe: TrainingRecipe):
        """Display recipe summary with rich formatting"""
        
        # Recipe header
        console.print(Panel.fit(
            f"🔧 [bold blue]Treatment Recipe Generated[/bold blue]\n"
            f"Recipe ID: {recipe.recipe_id}",
            border_style="blue"
        ))
        
        # Hyperparameters table
        table = Table(title="🎛️ Adaptive Hyperparameters", border_style="blue")
        table.add_column("Parameter", style="cyan", no_wrap=True)
        table.add_column("Value", justify="right", style="green")
        table.add_column("Reasoning", style="yellow")
        
        # Add hyperparameter rows with reasoning
        params = recipe.hyperparameters
        severity = recipe.severity
        
        table.add_row(
            "Learning Rate",
            f"{params['learning_rate']:.2e}",
            f"Severity-based ({severity})"
        )
        
        table.add_row(
            "LoRA Rank",
            str(params["lora_r"]),
            "Balanced capacity/stability"
        )
        
        table.add_row(
            "LoRA Alpha",
            str(params["lora_alpha"]),
            "2x rank (standard ratio)"
        )
        
        table.add_row(
            "Epochs",
            str(params["num_epochs"]),
            f"Conservative for {severity.lower()} issues"
        )
        
        table.add_row(
            "Batch Size",
            str(params["batch_size"]),
            "Memory-optimized"
        )
        
        table.add_row(
            "Gradient Accumulation",
            str(params["gradient_accumulation_steps"]),
            "Effective batch size scaling"
        )
        
        console.print(table)
        
        # Skill adjustments
        if recipe.skill_adjustments:
            console.print("\n[bold]🧠 Skill Preservation Adjustments:[/bold]")
            for adjustment in recipe.skill_adjustments:
                console.print(f"  • {adjustment}")
        
        # Recipe metadata
        console.print(f"\n[bold]📋 Recipe Metadata:[/bold]")
        console.print(f"  • Model: {recipe.model_name}")
        console.print(f"  • Symptom: {recipe.symptom}")
        console.print(f"  • Severity: {recipe.severity}")
        console.print(f"  • Dataset: {recipe.cure_dataset_path}")
        console.print(f"  • Output: {recipe.output_path}")
        
        # Usage instructions
        console.print(f"\n[bold green]🚀 Ready to Train:[/bold green]")
        console.print(f"  oumi train {recipe.recipe_id}.yaml")
    
    def save_recipe(self, recipe: TrainingRecipe, output_dir: str = "./recipes") -> Dict[str, str]:
        """
        Save recipe to files for training and community sharing.
        
        Args:
            recipe: TrainingRecipe to save
            output_dir: Directory to save recipe files
            
        Returns:
            Dictionary with paths to saved files
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        saved_files = {}
        
        # Save YAML config for training
        yaml_path = output_path / f"{recipe.recipe_id}.yaml"
        with open(yaml_path, 'w', encoding='utf-8') as f:
            f.write(recipe.config_yaml)
        saved_files["yaml_config"] = str(yaml_path)
        
        # Save JSON metadata for community sharing
        json_path = output_path / f"{recipe.recipe_id}_metadata.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(recipe.to_dict(), f, indent=2)
        saved_files["metadata"] = str(json_path)
        
        # Save markdown summary
        md_path = output_path / f"{recipe.recipe_id}_summary.md"
        self._generate_markdown_summary(recipe, md_path)
        saved_files["summary"] = str(md_path)
        
        console.print(f"\n📄 Recipe files saved:")
        for file_type, path in saved_files.items():
            console.print(f"  • {file_type}: {path}")
        
        return saved_files
    
    def _generate_markdown_summary(self, recipe: TrainingRecipe, output_path: Path):
        """Generate markdown summary of the recipe"""
        
        md_content = f"""# 🔧 Treatment Recipe: {recipe.recipe_id}

## Summary
- **Model**: `{recipe.model_name}`
- **Symptom**: {recipe.symptom}
- **Severity**: {recipe.severity}
- **Dataset**: `{recipe.cure_dataset_path}`
- **Output**: `{recipe.output_path}`

## Hyperparameters

| Parameter | Value | Reasoning |
|-----------|-------|-----------|
| Learning Rate | `{recipe.hyperparameters['learning_rate']:.2e}` | Severity-based ({recipe.severity}) |
| LoRA Rank | `{recipe.hyperparameters['lora_r']}` | Balanced capacity/stability |
| LoRA Alpha | `{recipe.hyperparameters['lora_alpha']}` | 2x rank (standard ratio) |
| Epochs | `{recipe.hyperparameters['num_epochs']}` | Conservative for {recipe.severity.lower()} issues |
| Batch Size | `{recipe.hyperparameters['batch_size']}` | Memory-optimized |

## Skill Preservation Adjustments

"""
        
        if recipe.skill_adjustments:
            for adjustment in recipe.skill_adjustments:
                md_content += f"- {adjustment}\n"
        else:
            md_content += "- No skill preservation adjustments needed\n"
        
        md_content += f"""
## Usage

```bash
# Train the model with this recipe
oumi train {recipe.recipe_id}.yaml

# Monitor training progress
tensorboard --logdir {recipe.output_path}/logs
```

## Recipe Metadata

- **Recipe ID**: `{recipe.recipe_id}`
- **Version**: `{recipe.metadata['version']}`
- **Author**: `{recipe.metadata['author']}`
- **Created**: `{recipe.metadata['created']}`
- **Oumi Version**: `{recipe.metadata['oumi_version']}`

## Community Sharing

This recipe can be shared with the Oumi community for others to use:

```bash
oumi-hospital share-recipe --recipe {recipe.recipe_id}.yaml
```

---
*Generated by Oumi Model Hospital - Surgeon Agent*
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)


def main():
    """CLI entry point for surgeon"""
    import argparse
    
    parser = argparse.ArgumentParser(description="🔧 Surgeon - Generate training recipes")
    parser.add_argument("--diagnosis", required=True, help="Path to diagnosis JSON")
    parser.add_argument("--cure-dataset", required=True, help="Path to cure dataset")
    parser.add_argument("--skill-report", help="Path to skill preservation report")
    parser.add_argument("--output", default="./healed_model", help="Output directory")
    parser.add_argument("--recipe-name", help="Custom recipe name")
    parser.add_argument("--save-dir", default="./recipes", help="Directory to save recipe files")
    
    args = parser.parse_args()
    
    # Load diagnosis data
    with open(args.diagnosis, 'r') as f:
        diagnosis_data = json.load(f)
    
    # Load skill preservation data if provided
    skill_data = None
    if args.skill_report:
        with open(args.skill_report, 'r') as f:
            skill_data = json.load(f)
    
    # Initialize surgeon
    surgeon = Surgeon()
    
    # Generate recipe
    recipe = surgeon.generate_recipe(
        diagnosis_data=diagnosis_data,
        cure_dataset_path=args.cure_dataset,
        skill_preservation_data=skill_data,
        output_dir=args.output,
        recipe_name=args.recipe_name
    )
    
    # Save recipe files
    saved_files = surgeon.save_recipe(recipe, args.save_dir)
    
    console.print(f"\n🎉 Recipe generation complete!")
    console.print(f"Ready to train: oumi train {recipe.recipe_id}.yaml")


if __name__ == "__main__":
    main()