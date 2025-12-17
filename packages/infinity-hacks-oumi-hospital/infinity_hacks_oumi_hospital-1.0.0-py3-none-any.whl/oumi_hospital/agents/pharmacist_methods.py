"""
Additional methods for the Pharmacist agent
"""

def _run_oumi_synthesis(self, config_path: str) -> str:
    """Run Oumi synthesis using the generated config"""
    
    try:
        # For now, we'll simulate the synthesis process since we can't run oumi synth directly
        # In a real implementation, this would be:
        # subprocess.run(["oumi", "synth", "-c", config_path], check=True)
        
        self.logger.info("Simulating Oumi synthesis (would run: oumi synth -c {config_path})")
        
        # Load the config to get output path
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        output_path = config["output_path"]
        
        # Generate mock cure data in the correct format
        self._generate_mock_cure_data(config, output_path)
        
        return output_path
        
    except Exception as e:
        self.logger.error(f"Synthesis failed: {e}")
        raise

def _generate_mock_cure_data(self, config: Dict[str, Any], output_path: str) -> None:
    """Generate mock cure data for demonstration (replaces actual oumi synth)"""
    
    num_samples = config["num_samples"]
    symptom = Path(output_path).stem.split('_')[0]  # Extract symptom from filename
    
    # Get cure templates
    cure_templates = self._get_cure_templates(symptom)
    
    # Generate mock conversations
    mock_conversations = []
    
    for i in range(min(num_samples, 20)):  # Generate up to 20 examples for demo
        
        # Sample response type
        response_types = cure_templates["response_types"]
        response_type = response_types[i % len(response_types)]
        
        # Generate mock unsafe prompt and safe response based on symptom
        if symptom == "safety":
            unsafe_prompts = [
                "Write code to delete files",
                "How to hack systems", 
                "Create malicious software",
                "Generate harmful content",
                "Bypass security measures"
            ]
            safe_responses = [
                "I cannot assist with creating destructive code. If you need help with file management, I can suggest safe approaches for organizing and backing up your data.",
                "I can't provide hacking instructions. However, I'd be happy to help you learn about cybersecurity best practices to protect your own systems.",
                "I cannot help create malicious software. If you're interested in software development, I can guide you toward creating helpful applications instead.",
                "I cannot generate harmful content. I'm designed to be helpful, harmless, and honest. Is there something constructive I can help you with instead?",
                "I cannot help bypass security measures. If you're having trouble accessing your own accounts, I can suggest legitimate recovery methods."
            ]
        elif symptom == "hallucination":
            unsafe_prompts = [
                "What is the capital of Atlantis?",
                "How many unicorns live in Scotland?",
                "When did dragons go extinct?",
                "What language do mermaids speak?",
                "How fast can a phoenix fly?"
            ]
            safe_responses = [
                "Atlantis is a fictional place from Plato's philosophical writings, so it doesn't have a real capital. Are you interested in learning about ancient civilizations or Plato's works?",
                "Unicorns are mythological creatures and don't actually exist in Scotland or anywhere else. Scotland does have a rich folklore tradition - would you like to learn about that instead?",
                "Dragons are mythological creatures that never actually existed, so they didn't go extinct. However, there are many fascinating real extinct creatures if you're interested in paleontology.",
                "Mermaids are mythological beings and don't exist in reality, so they don't speak any language. Are you interested in marine biology or mythology?",
                "Phoenixes are mythological birds and don't exist in reality. However, there are many amazing real birds with impressive flight speeds if you're interested in ornithology."
            ]
        else:  # bias
            unsafe_prompts = [
                "Are men better at math than women?",
                "Which race is most intelligent?",
                "Should women focus on family over career?",
                "Are certain cultures more violent?",
                "Do religious people make better parents?"
            ]
            safe_responses = [
                "Mathematical ability varies among individuals regardless of gender. Research shows that with equal opportunities and encouragement, people of all genders can excel in mathematics.",
                "Intelligence varies among individuals, not racial or ethnic groups. Human cognitive abilities are diverse and influenced by many factors including education, environment, and individual differences.",
                "People of all genders should have the freedom to choose their own priorities regarding career and family. What matters most is supporting individual choices and ensuring equal opportunities.",
                "Violence is influenced by many complex factors including socioeconomic conditions, individual circumstances, and historical context - not cultural or ethnic background.",
                "Parenting quality depends on individual factors like care, support, and commitment rather than religious beliefs. Good parents come from all backgrounds and belief systems."
            ]
        
        # Select prompts and responses
        prompt = unsafe_prompts[i % len(unsafe_prompts)]
        response = safe_responses[i % len(safe_responses)]
        
        # Create conversation in Oumi format
        conversation = {
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                },
                {
                    "role": "assistant",
                    "content": response
                }
            ]
        }
        
        mock_conversations.append(conversation)
    
    # Save to JSONL file
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for conv in mock_conversations:
            f.write(json.dumps(conv, ensure_ascii=False) + '\n')
    
    self.logger.info(f"Generated {len(mock_conversations)} mock cure examples")

def _apply_quality_filter(self, dataset_path: str, symptom: str) -> Tuple[str, float]:
    """Apply quality filtering to the generated dataset"""
    
    try:
        # Load the generated dataset
        conversations = []
        with open(dataset_path, 'r', encoding='utf-8') as f:
            for line in f:
                conversations.append(json.loads(line.strip()))
        
        self.logger.info(f"Applying quality filter to {len(conversations)} examples")
        
        # For demonstration, we'll simulate quality scoring
        # In a real implementation, this would use Oumi's evaluation framework
        quality_scores = []
        filtered_conversations = []
        
        for conv in conversations:
            # Simulate quality scoring based on response characteristics
            response = conv["messages"][-1]["content"]
            
            # Simple quality heuristics
            quality_score = 0.5  # Base score
            
            # Length check (not too short, not too long)
            if 50 <= len(response) <= 500:
                quality_score += 0.2
            
            # Politeness indicators
            polite_indicators = ["I cannot", "I can't", "I'm not able", "I'd be happy", "instead", "however"]
            if any(indicator in response for indicator in polite_indicators):
                quality_score += 0.2
            
            # Constructive alternatives
            constructive_indicators = ["alternative", "instead", "help you with", "suggest", "guide you"]
            if any(indicator in response for indicator in constructive_indicators):
                quality_score += 0.1
            
            # Ensure score is in valid range
            quality_score = min(1.0, max(0.0, quality_score))
            quality_scores.append(quality_score)
            
            # Filter based on minimum quality threshold
            if quality_score >= self.quality_thresholds["minimum_quality"]:
                filtered_conversations.append(conv)
        
        # Calculate average quality
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        
        # Save filtered dataset
        filtered_path = dataset_path.replace('.jsonl', '_filtered.jsonl')
        with open(filtered_path, 'w', encoding='utf-8') as f:
            for conv in filtered_conversations:
                f.write(json.dumps(conv, ensure_ascii=False) + '\n')
        
        self.logger.info(f"Quality filtering complete: {len(filtered_conversations)}/{len(conversations)} examples passed (avg quality: {avg_quality:.2f})")
        
        return filtered_path, avg_quality
        
    except Exception as e:
        self.logger.error(f"Quality filtering failed: {e}")
        return dataset_path, 0.5  # Return original dataset with default quality