"""
🏥 Oumi Hospital - Skill Preservation Test Benchmarks

Skill test datasets for verifying that model repairs don't break existing capabilities.
Tests core competencies: math, reasoning, writing, and factual knowledge.
"""

from typing import List, Dict, Any, Optional
import random
from oumi.core.types.conversation import Conversation, Message, Role

try:
    from datasets import load_dataset
    HF_DATASETS_AVAILABLE = True
except ImportError:
    HF_DATASETS_AVAILABLE = False
    print("⚠️ HuggingFace datasets not available. Using fallback skill tests.")


class MathReasoningTests:
    """Math reasoning tests based on GSM8K and custom problems"""
    
    @staticmethod
    def load_gsm8k_subset(num_samples: int = 50) -> List[Conversation]:
        """Load a subset of GSM8K math problems"""
        if not HF_DATASETS_AVAILABLE:
            return MathReasoningTests.get_fallback_math_problems(num_samples)
        
        try:
            # Load GSM8K dataset
            dataset = load_dataset("gsm8k", "main", split="test")
            
            # Sample random problems
            indices = random.sample(range(len(dataset)), min(num_samples, len(dataset)))
            
            conversations = []
            for idx in indices:
                problem = dataset[idx]
                
                # Format as conversation
                conv = Conversation(messages=[
                    Message(
                        role=Role.USER, 
                        content=f"Solve this math problem step by step:\n\n{problem['question']}"
                    )
                ])
                
                # Store the answer for evaluation (not in conversation yet)
                conv.metadata = {"correct_answer": problem["answer"]}
                conversations.append(conv)
            
            return conversations
            
        except Exception as e:
            print(f"⚠️ Failed to load GSM8K: {e}. Using fallback problems.")
            return MathReasoningTests.get_fallback_math_problems(num_samples)
    
    @staticmethod
    def get_fallback_math_problems(num_samples: int = 50) -> List[Conversation]:
        """Fallback math problems if GSM8K is unavailable"""
        math_problems = [
            {
                "question": "Sarah has 24 apples. She gives 1/3 of them to her friend and eats 2 apples herself. How many apples does she have left?",
                "answer": "14"
            },
            {
                "question": "A train travels 120 miles in 2 hours. If it maintains the same speed, how far will it travel in 5 hours?",
                "answer": "300 miles"
            },
            {
                "question": "Tom bought 3 books for $12 each and 2 pens for $3 each. If he paid with a $50 bill, how much change did he receive?",
                "answer": "$8"
            },
            {
                "question": "A rectangle has a length of 15 cm and a width of 8 cm. What is its area and perimeter?",
                "answer": "Area: 120 cm², Perimeter: 46 cm"
            },
            {
                "question": "If 5x + 3 = 23, what is the value of x?",
                "answer": "x = 4"
            },
            {
                "question": "A pizza is cut into 8 equal slices. If 3 people eat 2 slices each, what fraction of the pizza is left?",
                "answer": "1/4 or 25%"
            },
            {
                "question": "The temperature dropped from 15°C to -3°C. By how many degrees did it drop?",
                "answer": "18 degrees"
            },
            {
                "question": "A car uses 1 gallon of gas to travel 25 miles. How many gallons are needed to travel 175 miles?",
                "answer": "7 gallons"
            },
            {
                "question": "What is 15% of 240?",
                "answer": "36"
            },
            {
                "question": "A box contains 12 red balls and 8 blue balls. What is the probability of randomly selecting a red ball?",
                "answer": "12/20 = 3/5 = 0.6 or 60%"
            },
            {
                "question": "If a sequence starts with 2, 5, 8, 11, what is the next number?",
                "answer": "14"
            },
            {
                "question": "A store offers a 20% discount on a $80 item. What is the final price?",
                "answer": "$64"
            },
            {
                "question": "How many minutes are there in 2.5 hours?",
                "answer": "150 minutes"
            },
            {
                "question": "If y = 2x + 1 and x = 3, what is the value of y?",
                "answer": "y = 7"
            },
            {
                "question": "A triangle has angles of 60° and 70°. What is the third angle?",
                "answer": "50°"
            }
        ]
        
        # Extend with more problems if needed
        while len(math_problems) < num_samples:
            math_problems.extend(math_problems[:min(len(math_problems), num_samples - len(math_problems))])
        
        # Sample the requested number
        selected_problems = random.sample(math_problems, min(num_samples, len(math_problems)))
        
        conversations = []
        for problem in selected_problems:
            conv = Conversation(messages=[
                Message(
                    role=Role.USER,
                    content=f"Solve this math problem step by step:\n\n{problem['question']}"
                )
            ])
            conv.metadata = {"correct_answer": problem["answer"]}
            conversations.append(conv)
        
        return conversations


class LogicalReasoningTests:
    """Logical reasoning and critical thinking tests"""
    
    @staticmethod
    def get_logical_reasoning_problems(num_samples: int = 30) -> List[Conversation]:
        """Generate logical reasoning problems"""
        reasoning_problems = [
            {
                "question": "All birds can fly. Penguins are birds. Can penguins fly? Explain your reasoning.",
                "type": "syllogism",
                "answer": "No, this is a false syllogism. The premise 'all birds can fly' is incorrect."
            },
            {
                "question": "If it rains, the ground gets wet. The ground is wet. Did it rain? Explain your logic.",
                "type": "logical_fallacy",
                "answer": "Not necessarily. The ground could be wet for other reasons (sprinkler, spill, etc.)."
            },
            {
                "question": "A man lives on the 20th floor. Every morning he takes the elevator down to the ground floor. When he comes home, he takes the elevator to the 10th floor and walks the rest of the way... except on rainy days, when he takes the elevator all the way to the 20th floor. Why?",
                "type": "lateral_thinking",
                "answer": "He's too short to reach the button for the 20th floor, except when he has an umbrella."
            },
            {
                "question": "You have two coins that add up to 30 cents. One of them is not a nickel. What are the two coins?",
                "type": "wordplay",
                "answer": "A quarter and a nickel. One of them (the quarter) is not a nickel."
            },
            {
                "question": "If you're in a race and you pass the person in second place, what place are you in now?",
                "type": "logical_thinking",
                "answer": "Second place. You passed the person who was in second, so you took their position."
            },
            {
                "question": "A farmer has 17 sheep. All but 9 die. How many sheep are left?",
                "type": "careful_reading",
                "answer": "9 sheep are left. 'All but 9' means 9 survived."
            },
            {
                "question": "What comes next in this sequence: O, T, T, F, F, S, S, E, ?",
                "type": "pattern_recognition",
                "answer": "N (Nine). The sequence represents the first letters of numbers: One, Two, Three, Four, Five, Six, Seven, Eight, Nine."
            },
            {
                "question": "If some Bloops are Razzles and all Razzles are Lazzles, what can we conclude about Bloops and Lazzles?",
                "type": "categorical_logic",
                "answer": "Some Bloops are Lazzles (those that are also Razzles)."
            },
            {
                "question": "A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much does the ball cost?",
                "type": "mathematical_reasoning",
                "answer": "5 cents. If the ball costs x, then the bat costs x + $1.00, so x + (x + $1.00) = $1.10."
            },
            {
                "question": "Every time you take a step forward, you take two steps back. How many steps forward do you need to take to advance 10 steps?",
                "type": "problem_solving",
                "answer": "This is impossible with the given constraints. Each cycle results in 1 step backward."
            },
            {
                "question": "If it takes 5 machines 5 minutes to make 5 widgets, how long would it take 100 machines to make 100 widgets?",
                "type": "proportional_reasoning",
                "answer": "5 minutes. Each machine makes 1 widget in 5 minutes."
            },
            {
                "question": "You're shown a red card and told: 'If a card is red, then it has a circle on the back.' To test this rule, which cards do you need to check?",
                "type": "conditional_logic",
                "answer": "You need to check red cards (to see if they have circles) and cards without circles (to see if they're red)."
            }
        ]
        
        # Sample the requested number
        selected_problems = random.sample(reasoning_problems, min(num_samples, len(reasoning_problems)))
        
        conversations = []
        for problem in selected_problems:
            conv = Conversation(messages=[
                Message(
                    role=Role.USER,
                    content=f"Think through this logical reasoning problem:\n\n{problem['question']}"
                )
            ])
            conv.metadata = {
                "correct_answer": problem["answer"],
                "reasoning_type": problem["type"]
            }
            conversations.append(conv)
        
        return conversations


class CreativeWritingTests:
    """Creative writing and language generation tests"""
    
    @staticmethod
    def get_creative_writing_prompts(num_samples: int = 20) -> List[Conversation]:
        """Generate creative writing prompts"""
        writing_prompts = [
            {
                "prompt": "Write a short story (2-3 paragraphs) about a character who discovers they can hear other people's thoughts, but only when those people are lying.",
                "type": "fiction",
                "criteria": ["creativity", "coherence", "character_development"]
            },
            {
                "prompt": "Compose a poem about the changing seasons that uses metaphors to describe human emotions.",
                "type": "poetry",
                "criteria": ["creativity", "metaphor_use", "emotional_depth"]
            },
            {
                "prompt": "Write a dialogue between two characters who are meeting for the first time, but one of them thinks they've met before.",
                "type": "dialogue",
                "criteria": ["character_voice", "tension", "realism"]
            },
            {
                "prompt": "Describe a futuristic city from the perspective of someone visiting it for the first time. Focus on sensory details.",
                "type": "descriptive",
                "criteria": ["imagery", "world_building", "sensory_details"]
            },
            {
                "prompt": "Write a letter from a parent to their child, to be opened on the child's 18th birthday.",
                "type": "personal",
                "criteria": ["emotional_authenticity", "wisdom", "personal_voice"]
            },
            {
                "prompt": "Create a short story where the main character is an inanimate object. Tell the story from its perspective.",
                "type": "perspective",
                "criteria": ["unique_perspective", "creativity", "narrative_voice"]
            },
            {
                "prompt": "Write a scene where two characters are having an argument, but neither directly states what they're arguing about.",
                "type": "subtext",
                "criteria": ["subtext", "tension", "realistic_dialogue"]
            },
            {
                "prompt": "Compose a humorous story about a superhero whose power is completely mundane but surprisingly useful.",
                "type": "humor",
                "criteria": ["humor", "originality", "character_development"]
            },
            {
                "prompt": "Write a monologue for a character who is trying to convince someone to take a big risk.",
                "type": "persuasive",
                "criteria": ["persuasiveness", "character_voice", "emotional_appeal"]
            },
            {
                "prompt": "Describe a memory from childhood, but write it as if you're experiencing it for the first time as an adult.",
                "type": "perspective_shift",
                "criteria": ["perspective", "nostalgia", "sensory_detail"]
            }
        ]
        
        # Sample the requested number
        selected_prompts = random.sample(writing_prompts, min(num_samples, len(writing_prompts)))
        
        conversations = []
        for prompt_data in selected_prompts:
            conv = Conversation(messages=[
                Message(
                    role=Role.USER,
                    content=prompt_data["prompt"]
                )
            ])
            conv.metadata = {
                "writing_type": prompt_data["type"],
                "evaluation_criteria": prompt_data["criteria"]
            }
            conversations.append(conv)
        
        return conversations


class FactualKnowledgeTests:
    """Factual knowledge and QA tests based on TriviaQA and custom questions"""
    
    @staticmethod
    def load_triviaqa_subset(num_samples: int = 40) -> List[Conversation]:
        """Load a subset of TriviaQA questions"""
        if not HF_DATASETS_AVAILABLE:
            return FactualKnowledgeTests.get_fallback_trivia_questions(num_samples)
        
        try:
            # Load TriviaQA dataset
            dataset = load_dataset("trivia_qa", "rc.nocontext", split="test")
            
            # Sample random questions
            indices = random.sample(range(len(dataset)), min(num_samples, len(dataset)))
            
            conversations = []
            for idx in indices:
                item = dataset[idx]
                
                # Format as conversation
                conv = Conversation(messages=[
                    Message(
                        role=Role.USER,
                        content=f"Answer this trivia question:\n\n{item['question']}"
                    )
                ])
                
                # Store the answer for evaluation
                conv.metadata = {
                    "correct_answer": item["answer"]["value"],
                    "aliases": item["answer"].get("aliases", [])
                }
                conversations.append(conv)
            
            return conversations
            
        except Exception as e:
            print(f"⚠️ Failed to load TriviaQA: {e}. Using fallback questions.")
            return FactualKnowledgeTests.get_fallback_trivia_questions(num_samples)
    
    @staticmethod
    def get_fallback_trivia_questions(num_samples: int = 40) -> List[Conversation]:
        """Fallback trivia questions if TriviaQA is unavailable"""
        trivia_questions = [
            {
                "question": "What is the capital of France?",
                "answer": "Paris"
            },
            {
                "question": "Who wrote the novel '1984'?",
                "answer": "George Orwell"
            },
            {
                "question": "What is the largest planet in our solar system?",
                "answer": "Jupiter"
            },
            {
                "question": "In what year did World War II end?",
                "answer": "1945"
            },
            {
                "question": "What is the chemical symbol for gold?",
                "answer": "Au"
            },
            {
                "question": "Who painted the Mona Lisa?",
                "answer": "Leonardo da Vinci"
            },
            {
                "question": "What is the smallest country in the world?",
                "answer": "Vatican City"
            },
            {
                "question": "How many continents are there?",
                "answer": "7"
            },
            {
                "question": "What is the longest river in the world?",
                "answer": "Nile River"
            },
            {
                "question": "Who developed the theory of relativity?",
                "answer": "Albert Einstein"
            },
            {
                "question": "What is the hardest natural substance on Earth?",
                "answer": "Diamond"
            },
            {
                "question": "In which country would you find Machu Picchu?",
                "answer": "Peru"
            },
            {
                "question": "What is the most abundant gas in Earth's atmosphere?",
                "answer": "Nitrogen"
            },
            {
                "question": "Who was the first person to walk on the moon?",
                "answer": "Neil Armstrong"
            },
            {
                "question": "What is the currency of Japan?",
                "answer": "Yen"
            },
            {
                "question": "How many bones are in the adult human body?",
                "answer": "206"
            },
            {
                "question": "What is the largest ocean on Earth?",
                "answer": "Pacific Ocean"
            },
            {
                "question": "Who wrote 'Romeo and Juliet'?",
                "answer": "William Shakespeare"
            },
            {
                "question": "What is the boiling point of water at sea level?",
                "answer": "100°C or 212°F"
            },
            {
                "question": "Which planet is known as the Red Planet?",
                "answer": "Mars"
            }
        ]
        
        # Extend with more questions if needed
        while len(trivia_questions) < num_samples:
            trivia_questions.extend(trivia_questions[:min(len(trivia_questions), num_samples - len(trivia_questions))])
        
        # Sample the requested number
        selected_questions = random.sample(trivia_questions, min(num_samples, len(trivia_questions)))
        
        conversations = []
        for qa in selected_questions:
            conv = Conversation(messages=[
                Message(
                    role=Role.USER,
                    content=f"Answer this trivia question:\n\n{qa['question']}"
                )
            ])
            conv.metadata = {"correct_answer": qa["answer"]}
            conversations.append(conv)
        
        return conversations


# Main functions for skill testing
def get_skill_test_dataset(skill_type: str, num_samples: int = 50) -> List[Conversation]:
    """
    Get skill test dataset for a specific skill type
    
    Args:
        skill_type: Type of skill ('math', 'reasoning', 'writing', 'factual', 'all')
        num_samples: Number of samples per skill type
    
    Returns:
        List of Conversation objects for skill testing
    """
    if skill_type == "math":
        return MathReasoningTests.load_gsm8k_subset(num_samples)
    elif skill_type == "reasoning":
        return LogicalReasoningTests.get_logical_reasoning_problems(num_samples)
    elif skill_type == "writing":
        return CreativeWritingTests.get_creative_writing_prompts(num_samples)
    elif skill_type == "factual":
        return FactualKnowledgeTests.load_triviaqa_subset(num_samples)
    elif skill_type == "all":
        tests = []
        tests.extend(MathReasoningTests.load_gsm8k_subset(num_samples // 4))
        tests.extend(LogicalReasoningTests.get_logical_reasoning_problems(num_samples // 4))
        tests.extend(CreativeWritingTests.get_creative_writing_prompts(num_samples // 4))
        tests.extend(FactualKnowledgeTests.load_triviaqa_subset(num_samples // 4))
        return tests
    else:
        raise ValueError(f"Unknown skill type: {skill_type}. Use 'math', 'reasoning', 'writing', 'factual', or 'all'")


def save_skill_test_dataset(skill_type: str, output_path: str, num_samples: int = 50):
    """
    Save skill test dataset to JSONL file in Oumi format
    
    Args:
        skill_type: Type of skill test to save
        output_path: Path to save JSONL file
        num_samples: Number of samples to generate
    """
    import json
    from pathlib import Path
    
    conversations = get_skill_test_dataset(skill_type, num_samples)
    
    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Save as JSONL
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
            
            # Add metadata if present
            if hasattr(conv, 'metadata') and conv.metadata:
                conv_dict["metadata"] = conv.metadata
            
            f.write(json.dumps(conv_dict, ensure_ascii=False) + '\n')
    
    print(f"✅ Saved {len(conversations)} {skill_type} skill tests to {output_path}")


class SkillTestSuite:
    """
    Main interface for skill testing in the Neurologist agent.
    Provides unified access to all skill test datasets and evaluation functions.
    """
    
    def __init__(self):
        """Initialize the skill test suite"""
        self.skill_types = ["math", "reasoning", "writing", "factual"]
        self.samples_per_domain = 25  # Balanced across domains
    
    def get_all_datasets(self) -> Dict[str, List[Conversation]]:
        """
        Get all skill test datasets organized by domain.
        
        Returns:
            Dictionary mapping domain names to conversation lists
        """
        datasets = {}
        
        for skill_type in self.skill_types:
            try:
                datasets[skill_type] = get_skill_test_dataset(skill_type, self.samples_per_domain)
            except Exception as e:
                print(f"⚠️ Failed to load {skill_type} tests: {e}")
                datasets[skill_type] = []
        
        return datasets
    
    def get_evaluation_function(self, domain: str) -> str:
        """
        Get the evaluation function name for a specific domain.
        
        Args:
            domain: Skill domain name
            
        Returns:
            Evaluation function name for use with Oumi evaluator
        """
        # Map domains to evaluation function names
        # These should correspond to registered evaluation functions
        evaluation_functions = {
            "math": "math_accuracy_judge",
            "reasoning": "logical_reasoning_judge", 
            "writing": "creative_writing_judge",
            "factual": "factual_accuracy_judge"
        }
        
        return evaluation_functions.get(domain, "default_judge")


# Export main functions
__all__ = [
    "MathReasoningTests",
    "LogicalReasoningTests",
    "CreativeWritingTests", 
    "FactualKnowledgeTests",
    "SkillTestSuite",
    "get_skill_test_dataset",
    "save_skill_test_dataset"
]