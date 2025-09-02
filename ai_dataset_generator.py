#!/usr/bin/env python3
"""
AI Training Dataset Generator
A configurable tool for generating high-quality training datasets for AI fine-tuning

This tool helps users create domain-specific training datasets by leveraging their 
knowledge base (PDFs, markdown files, etc.) to generate realistic scenarios and 
expert-level responses for fine-tuning language models.

Author: Open Source AI Community
License: MIT
"""

import os
import json
import fitz  # PyMuPDF for PDF processing
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import random
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from agno.agent import Agent
    from agno.models.openai import OpenAIChat
    from agno.knowledge.markdown import MarkdownKnowledgeBase
    from agno.knowledge.pdf import PDFKnowledgeBase
    AGNO_AVAILABLE = True
except ImportError:
    AGNO_AVAILABLE = False
    print("Warning: Agno framework not found. Install with: pip install agno")

from config import DatasetConfig, ConfigTemplates


class AIDatasetGenerator:
    """
    Configurable AI training dataset generator
    
    This class generates training datasets for fine-tuning by:
    1. Loading domain knowledge from various sources (PDF, markdown, text)
    2. Creating realistic scenarios based on the knowledge
    3. Generating expert-level responses for training
    4. Outputting in formats suitable for fine-tuning (JSONL, JSON)
    """
    
    def __init__(self, config: DatasetConfig, openai_api_key: Optional[str] = None):
        """
        Initialize the dataset generator
        
        Args:
            config: Configuration object defining the generation parameters
            openai_api_key: OpenAI API key (can also be set via environment variable)
        """
        self.config = config
        
        # Set up OpenAI API key
        if openai_api_key:
            os.environ["OPENAI_API_KEY"] = openai_api_key
        elif not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OpenAI API key must be provided either as parameter or OPENAI_API_KEY environment variable")
        
        if not AGNO_AVAILABLE:
            raise ImportError("Agno framework is required. Install with: pip install agno")
        
        # Initialize knowledge base
        self.knowledge_base = self._create_knowledge_base()
        
        # Create the AI agent
        self.agent = Agent(
            name=config.expert_role,
            model=OpenAIChat(
                id=config.model_name,
                temperature=config.temperature,
                max_tokens=config.max_tokens
            ),
            knowledge_base=self.knowledge_base,
            instructions=config.system_prompt_template,
            show_tool_calls=False,
            markdown=True
        )
        
        print(f"✅ AI Dataset Generator initialized for {config.domain_name}")
        print(f"📚 Knowledge base loaded from {len(config.knowledge_sources)} source(s)")
        print(f"🤖 Using model: {config.model_name}")
    
    def _create_knowledge_base(self):
        """Create knowledge base from configured sources"""
        print("📚 Loading knowledge base...")
        
        # Collect all knowledge files
        knowledge_files = []
        for source in self.config.knowledge_sources:
            source_path = Path(source)
            
            if source_path.is_file():
                knowledge_files.append(str(source_path))
            elif source_path.is_dir():
                # Add all supported files in directory
                for ext in ['*.md', '*.pdf', '*.txt']:
                    knowledge_files.extend([str(f) for f in source_path.glob(ext)])
        
        if not knowledge_files:
            raise ValueError(f"No knowledge files found in sources: {self.config.knowledge_sources}")
        
        print(f"📄 Found {len(knowledge_files)} knowledge file(s)")
        
        # Separate files by type
        pdf_files = [f for f in knowledge_files if f.endswith('.pdf')]
        markdown_files = [f for f in knowledge_files if f.endswith(('.md', '.markdown'))]
        text_files = [f for f in knowledge_files if f.endswith('.txt')]
        
        # Create appropriate knowledge base
        if pdf_files and self.config.knowledge_type in ['pdf', 'auto']:
            print(f"📑 Loading {len(pdf_files)} PDF file(s)")
            return PDFKnowledgeBase(
                sources=pdf_files,
                chunk_size=self.config.chunk_size,
                chunk_overlap=self.config.chunk_overlap
            )
        elif markdown_files:
            print(f"📝 Loading {len(markdown_files)} Markdown file(s)")
            return MarkdownKnowledgeBase(
                sources=markdown_files,
                chunk_size=self.config.chunk_size,
                chunk_overlap=self.config.chunk_overlap
            )
        else:
            # Fallback to treating all as text
            print(f"📄 Loading {len(knowledge_files)} text file(s)")
            return MarkdownKnowledgeBase(
                sources=knowledge_files,
                chunk_size=self.config.chunk_size,
                chunk_overlap=self.config.chunk_overlap
            )
    
    def generate_scenario(self, scenario_type: str = "general") -> Dict[str, Any]:
        """
        Generate a single realistic scenario for the domain
        
        Args:
            scenario_type: Type of scenario to generate (e.g., "edge_case", "complex", "basic")
            
        Returns:
            Dictionary containing the scenario details
        """
        scenario_prompt = f"""
        {self.config.scenario_prompt_template}
        
        Create a {scenario_type} scenario for {self.config.task_description}.
        
        The scenario should:
        - Be realistic and detailed
        - Include all necessary context and information
        - Require knowledge from the knowledge base to assess correctly
        - Be different from previously generated scenarios
        
        Please provide the scenario in a structured format with:
        - Background/Context
        - Specific details relevant to assessment
        - Key factors that need evaluation
        """
        
        try:
            response = self.agent.run(scenario_prompt)
            return {
                "type": scenario_type,
                "content": response.content,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"⚠️ Error generating scenario: {e}")
            return None
    
    def generate_response(self, scenario: str) -> Dict[str, Any]:
        """
        Generate expert response to a scenario
        
        Args:
            scenario: The scenario to respond to
            
        Returns:
            Dictionary containing the expert response
        """
        full_prompt = f"""
        SCENARIO:
        {scenario}
        
        QUESTION: {self.config.user_query_template}
        """
        
        try:
            response = self.agent.run(full_prompt)
            return {
                "content": response.content,
                "timestamp": datetime.now().isoformat(),
                "model_used": self.config.model_name
            }
        except Exception as e:
            print(f"⚠️ Error generating response: {e}")
            return None
    
    def generate_training_pair(self, scenario_type: str = "general") -> Optional[Dict[str, Any]]:
        """
        Generate a complete training pair (scenario + expert response)
        
        Args:
            scenario_type: Type of scenario to generate
            
        Returns:
            Complete training pair ready for fine-tuning
        """
        # Generate scenario
        scenario_data = self.generate_scenario(scenario_type)
        if not scenario_data:
            return None
        
        scenario_content = scenario_data["content"]
        
        # Generate expert response
        response_data = self.generate_response(scenario_content)
        if not response_data:
            return None
        
        # Format for training
        training_pair = {
            "messages": [
                {
                    "role": "user",
                    "content": f"{scenario_content}\n\nQUESTION: {self.config.user_query_template}"
                },
                {
                    "role": "assistant", 
                    "content": response_data["content"]
                }
            ],
            "metadata": {
                "scenario_type": scenario_type,
                "domain": self.config.domain_name,
                "generated_at": datetime.now().isoformat(),
                "model": self.config.model_name
            }
        }
        
        return training_pair
    
    def generate_dataset(self, scenario_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Generate a complete training dataset
        
        Args:
            scenario_types: List of scenario types to generate. If None, uses default mix.
            
        Returns:
            List of training pairs
        """
        if scenario_types is None:
            # Default mix of scenario types
            scenario_types = (
                ["basic"] * (self.config.num_scenarios // 3) +
                ["complex"] * (self.config.num_scenarios // 3) +
                ["edge_case"] * (self.config.num_scenarios // 3) +
                ["general"] * (self.config.num_scenarios % 3)
            )
        
        dataset = []
        raw_scenarios = []
        
        print(f"🚀 Generating {self.config.num_scenarios} training pairs...")
        
        for i, scenario_type in enumerate(scenario_types[:self.config.num_scenarios], 1):
            print(f"📝 Generating pair {i}/{self.config.num_scenarios} ({scenario_type})...")
            
            training_pair = self.generate_training_pair(scenario_type)
            if training_pair:
                dataset.append(training_pair)
                
                if self.config.include_raw_scenarios:
                    raw_scenarios.append({
                        "id": i,
                        "type": scenario_type,
                        "scenario": training_pair["messages"][0]["content"],
                        "response": training_pair["messages"][1]["content"],
                        "metadata": training_pair["metadata"]
                    })
            else:
                print(f"⚠️ Failed to generate pair {i}")
        
        print(f"✅ Generated {len(dataset)} training pairs")
        
        # Save datasets
        self._save_dataset(dataset, raw_scenarios)
        
        return dataset
    
    def _save_dataset(self, dataset: List[Dict[str, Any]], raw_scenarios: List[Dict[str, Any]]):
        """Save the generated dataset to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save main training dataset
        if self.config.output_format.lower() == "jsonl":
            output_file = f"{self.config.output_prefix}_{timestamp}.jsonl"
            with open(output_file, 'w') as f:
                for item in dataset:
                    f.write(json.dumps(item) + '\n')
        else:
            output_file = f"{self.config.output_prefix}_{timestamp}.json"
            with open(output_file, 'w') as f:
                json.dump(dataset, f, indent=2)
        
        print(f"💾 Training dataset saved to: {output_file}")
        
        # Save raw scenarios if requested
        if self.config.include_raw_scenarios and raw_scenarios:
            raw_file = f"{self.config.output_prefix}_raw_scenarios_{timestamp}.json"
            with open(raw_file, 'w') as f:
                json.dump(raw_scenarios, f, indent=2)
            print(f"💾 Raw scenarios saved to: {raw_file}")
        
        # Save configuration
        config_file = f"config_{timestamp}.json"
        from dataclasses import asdict
        with open(config_file, 'w') as f:
            json.dump(asdict(self.config), f, indent=2)
        print(f"💾 Configuration saved to: {config_file}")


def main():
    """
    Main function demonstrating usage
    You can customize this for your specific use case
    """
    
    # Example 1: Medical compliance (default)
    print("=== Example 1: Medical Compliance ===")
    config = ConfigTemplates.medical_compliance()
    config.knowledge_sources = ["kb/"]  # Point to your knowledge base
    config.num_scenarios = 5  # Small number for demo
    
    try:
        generator = AIDatasetGenerator(config)
        dataset = generator.generate_dataset()
        print(f"✅ Generated {len(dataset)} training pairs for medical compliance")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Example 2: Custom domain
    print("\n=== Example 2: Custom Domain ===")
    custom_config = ConfigTemplates.custom(
        domain="Quality Assurance",
        role="QA Expert", 
        task="quality assessment based on standards",
        knowledge_path="knowledge_base/qa/"
    )
    custom_config.num_scenarios = 3
    
    print("Custom configuration created for Quality Assurance domain")
    
    print("\n🎉 Dataset generation examples completed!")
    print("\n📖 To use this tool:")
    print("1. Add your knowledge files to the knowledge_base/ directory")
    print("2. Customize the configuration for your domain")
    print("3. Run: python ai_dataset_generator.py")
    print("4. Use the generated .jsonl file for fine-tuning!")


if __name__ == "__main__":
    main()
