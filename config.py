#!/usr/bin/env python3
"""
Configuration module for the AI Training Dataset Generator
Allows users to customize the generator for their specific domain and use case
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from pathlib import Path

@dataclass
class DatasetConfig:
    """Configuration class for dataset generation"""
    
    # Domain-specific settings
    domain_name: str = "Medical Compliance"
    expert_role: str = "Medical Compliance Expert"
    task_description: str = "compliance assessment based on standard operating procedures"
    
    # Knowledge base configuration
    knowledge_sources: List[str] = None  # Will be set in __post_init__
    knowledge_type: str = "markdown"  # 'markdown', 'pdf', or 'text'
    chunk_size: int = 1000
    chunk_overlap: int = 100
    
    # Dataset generation settings
    num_scenarios: int = 25
    output_format: str = "jsonl"  # 'jsonl' or 'json'
    include_raw_scenarios: bool = True
    
    # Model configuration
    model_name: str = "gpt-4o-mini"  # OpenAI model to use
    temperature: float = 0.8
    max_tokens: int = 2000
    
    # Prompt templates
    system_prompt_template: str = None
    scenario_prompt_template: str = None
    user_query_template: str = None
    
    # Output configuration
    output_prefix: str = "training_dataset"
    
    def __post_init__(self):
        """Set default values after initialization"""
        if self.knowledge_sources is None:
            self.knowledge_sources = ["knowledge_base/"]
        
        if self.system_prompt_template is None:
            self.system_prompt_template = self._default_system_prompt()
        
        if self.scenario_prompt_template is None:
            self.scenario_prompt_template = self._default_scenario_prompt()
        
        if self.user_query_template is None:
            self.user_query_template = self._default_user_query()
    
    def _default_system_prompt(self) -> str:
        """Default system prompt template"""
        return f"""You are an expert {self.expert_role} with deep knowledge of industry standards, 
        regulations, and best practices in {self.domain_name.lower()}. 

        Your role is to provide accurate, detailed, and compliant assessments based on the 
        knowledge base provided. Always cite specific sections and requirements when making 
        decisions, and explain your reasoning clearly.

        When analyzing scenarios, follow this structure:
        1. Identify all relevant criteria from the knowledge base
        2. Apply each criterion to the given scenario
        3. Provide a clear decision with detailed rationale
        4. Cite specific sources and sections from the knowledge base
        """
    
    def _default_scenario_prompt(self) -> str:
        """Default scenario generation prompt"""
        return f"""Generate realistic, detailed scenarios for {self.task_description}. 
        
        Each scenario should:
        - Be based on real-world situations in {self.domain_name.lower()}
        - Include all necessary details for a complete assessment
        - Test different aspects of the knowledge base
        - Vary in complexity from simple to complex multi-factor cases
        - Include edge cases and borderline situations
        
        Create scenarios that would require consulting the knowledge base to answer correctly,
        rather than relying on general knowledge.
        """
    
    def _default_user_query(self) -> str:
        """Default user query template"""
        return """Based on the provided standards and procedures, what is your assessment of this scenario? 
        Please provide your decision and detailed rationale, citing specific requirements and sections."""

# Pre-defined configurations for common use cases
class ConfigTemplates:
    """Pre-defined configuration templates for common domains"""
    
    @staticmethod
    def medical_compliance() -> DatasetConfig:
        """Configuration for medical compliance assessment"""
        return DatasetConfig(
            domain_name="Medical Compliance",
            expert_role="Medical Compliance Expert",
            task_description="medical compliance assessment based on SOPs and regulations",
            knowledge_sources=["knowledge_base/medical/"],
            num_scenarios=25
        )
    
    @staticmethod
    def legal_compliance() -> DatasetConfig:
        """Configuration for legal compliance assessment"""
        return DatasetConfig(
            domain_name="Legal Compliance",
            expert_role="Legal Compliance Expert", 
            task_description="legal compliance assessment based on regulations and policies",
            knowledge_sources=["knowledge_base/legal/"],
            num_scenarios=25,
            user_query_template="""Based on the applicable laws and regulations, what is your legal assessment of this scenario? 
            Please provide your conclusion and detailed legal reasoning, citing specific statutes and regulations."""
        )
    
    @staticmethod
    def financial_compliance() -> DatasetConfig:
        """Configuration for financial compliance assessment"""
        return DatasetConfig(
            domain_name="Financial Compliance",
            expert_role="Financial Compliance Expert",
            task_description="financial compliance assessment based on regulations and standards",
            knowledge_sources=["knowledge_base/financial/"],
            num_scenarios=25,
            user_query_template="""Based on the financial regulations and standards, what is your compliance assessment? 
            Please provide your determination and detailed analysis, citing specific regulatory requirements."""
        )
    
    @staticmethod
    def safety_compliance() -> DatasetConfig:
        """Configuration for safety compliance assessment"""
        return DatasetConfig(
            domain_name="Safety Compliance",
            expert_role="Safety Compliance Expert",
            task_description="safety compliance assessment based on standards and procedures",
            knowledge_sources=["knowledge_base/safety/"],
            num_scenarios=25,
            user_query_template="""Based on the safety standards and procedures, what is your safety assessment? 
            Please provide your decision and detailed safety analysis, citing specific standards and requirements."""
        )
    
    @staticmethod
    def custom(domain: str, role: str, task: str, knowledge_path: str) -> DatasetConfig:
        """Create a custom configuration"""
        return DatasetConfig(
            domain_name=domain,
            expert_role=role,
            task_description=task,
            knowledge_sources=[knowledge_path],
            num_scenarios=25
        )

def load_config_from_file(config_path: str) -> DatasetConfig:
    """Load configuration from a JSON file"""
    import json
    
    with open(config_path, 'r') as f:
        config_dict = json.load(f)
    
    return DatasetConfig(**config_dict)

def save_config_to_file(config: DatasetConfig, config_path: str) -> None:
    """Save configuration to a JSON file"""
    import json
    from dataclasses import asdict
    
    with open(config_path, 'w') as f:
        json.dump(asdict(config), f, indent=2)
