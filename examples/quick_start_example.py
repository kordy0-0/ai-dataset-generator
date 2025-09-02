#!/usr/bin/env python3
"""
Quick Start Example for AI Dataset Generator
This script demonstrates how to use the generator with different configurations
"""

from ai_dataset_generator import AIDatasetGenerator
from config import ConfigTemplates, DatasetConfig

def example_medical_compliance():
    """Example: Medical compliance dataset generation"""
    print("🏥 Example 1: Medical Compliance Dataset")
    print("=" * 50)
    
    # Use pre-built medical template
    config = ConfigTemplates.medical_compliance()
    
    # Customize for this example
    config.knowledge_sources = ["../knowledge_base/medical/"]
    config.num_scenarios = 5  # Small number for demo
    config.output_prefix = "medical_demo"
    
    try:
        generator = AIDatasetGenerator(config)
        dataset = generator.generate_dataset()
        
        print(f"✅ Generated {len(dataset)} medical compliance training pairs")
        print("📄 Files created:")
        print("   - medical_demo_[timestamp].jsonl (training data)")
        print("   - medical_demo_raw_scenarios_[timestamp].json (raw scenarios)")
        print("   - config_[timestamp].json (configuration used)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure you have:")
        print("   1. Set OPENAI_API_KEY in .env file")
        print("   2. Added knowledge files to knowledge_base/medical/")
        print("   3. Installed requirements: pip install -r requirements.txt")

def example_custom_domain():
    """Example: Custom domain configuration"""
    print("\n🛠️ Example 2: Custom Domain (Quality Assurance)")
    print("=" * 50)
    
    # Create custom configuration
    config = DatasetConfig(
        domain_name="Quality Assurance",
        expert_role="QA Expert",
        task_description="quality assurance assessment based on standards and procedures",
        knowledge_sources=["../knowledge_base/qa/"],
        num_scenarios=3,
        output_prefix="qa_demo",
        
        # Custom prompts
        system_prompt_template="""You are an expert Quality Assurance specialist with deep knowledge of 
        QA standards, testing procedures, and quality control processes. Provide detailed assessments 
        based on industry standards and best practices.""",
        
        user_query_template="""Based on QA standards and procedures, what is your quality assessment 
        of this scenario? Provide recommendations and cite specific standards."""
    )
    
    print("✅ Custom QA configuration created")
    print(f"📋 Domain: {config.domain_name}")
    print(f"👤 Expert Role: {config.expert_role}")
    print(f"📁 Knowledge Sources: {config.knowledge_sources}")

def example_multiple_domains():
    """Example: Demonstrating different domain templates"""
    print("\n🌟 Example 3: Multiple Domain Templates")
    print("=" * 50)
    
    domains = [
        ("Medical", ConfigTemplates.medical_compliance()),
        ("Legal", ConfigTemplates.legal_compliance()),
        ("Financial", ConfigTemplates.financial_compliance()),
        ("Safety", ConfigTemplates.safety_compliance())
    ]
    
    for domain_name, config in domains:
        print(f"\n{domain_name} Domain Configuration:")
        print(f"  Expert Role: {config.expert_role}")
        print(f"  Task: {config.task_description}")
        print(f"  Knowledge Path: {config.knowledge_sources[0]}")
        print(f"  Model: {config.model_name}")

def main():
    """Run all examples"""
    print("🚀 AI Dataset Generator - Quick Start Examples")
    print("=" * 60)
    
    # Run examples
    example_medical_compliance()
    example_custom_domain() 
    example_multiple_domains()
    
    print("\n" + "=" * 60)
    print("🎉 Quick start examples completed!")
    print("\n📖 Next Steps:")
    print("1. Add your knowledge files to the appropriate knowledge_base/ subdirectory")
    print("2. Customize the configuration for your specific needs")
    print("3. Run ai_dataset_generator.py with your configuration")
    print("4. Use the generated .jsonl file for fine-tuning!")
    print("\n🔗 For more examples, see: examples/ directory")
    print("📚 Full documentation: README.md")

if __name__ == "__main__":
    main()
