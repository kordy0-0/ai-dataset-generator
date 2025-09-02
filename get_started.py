#!/usr/bin/env python3
"""
Getting Started with AI Dataset Generator
Interactive setup and first-run guide
"""

import os
import sys
from pathlib import Path

def check_requirements():
    """Check if requirements are installed"""
    print("🔍 Checking requirements...")
    
    try:
        import agno
        print("✅ Agno framework installed")
    except ImportError:
        print("❌ Agno framework not found")
        print("   Install with: pip install agno[all]")
        return False
    
    try:
        import openai
        print("✅ OpenAI library installed")
    except ImportError:
        print("❌ OpenAI library not found")
        print("   Install with: pip install openai")
        return False
        
    try:
        import fitz
        print("✅ PyMuPDF installed")
    except ImportError:
        print("❌ PyMuPDF not found")
        print("   Install with: pip install PyMuPDF")
        return False
    
    return True

def check_api_key():
    """Check if OpenAI API key is configured"""
    print("\n🔑 Checking API key...")
    
    # Check .env file
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
            if "OPENAI_API_KEY" in content and not "your_openai_api_key_here" in content:
                print("✅ API key found in .env file")
                return True
    
    # Check environment variable
    if os.getenv("OPENAI_API_KEY"):
        print("✅ API key found in environment")
        return True
    
    print("❌ No API key found")
    print("   Create .env file with: OPENAI_API_KEY=your_actual_key_here")
    return False

def setup_knowledge_base():
    """Guide user through knowledge base setup"""
    print("\n📚 Setting up knowledge base...")
    
    kb_dir = Path("knowledge_base")
    if not kb_dir.exists():
        kb_dir.mkdir()
        print("✅ Created knowledge_base/ directory")
    
    # Check for existing knowledge
    knowledge_files = list(kb_dir.glob("**/*"))
    knowledge_files = [f for f in knowledge_files if f.is_file() and f.suffix in ['.pdf', '.md', '.txt']]
    
    if knowledge_files:
        print(f"✅ Found {len(knowledge_files)} knowledge files")
        for f in knowledge_files[:5]:  # Show first 5
            print(f"   📄 {f}")
        if len(knowledge_files) > 5:
            print(f"   ... and {len(knowledge_files) - 5} more")
        return True
    else:
        print("⚠️ No knowledge files found")
        print("   Add your PDFs, markdown, or text files to knowledge_base/")
        print("   Or run: python knowledge_base_utils.py for interactive setup")
        return False

def run_example():
    """Run a simple example"""
    print("\n🚀 Running example...")
    
    try:
        from examples.quick_start_example import example_custom_domain
        example_custom_domain()
        print("✅ Example configuration created successfully")
        return True
    except Exception as e:
        print(f"❌ Example failed: {e}")
        return False

def main():
    """Main setup guide"""
    print("🎉 Welcome to AI Dataset Generator!")
    print("=" * 50)
    print("This tool helps you create training datasets for AI fine-tuning")
    print("using your own domain knowledge and documents.\n")
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Please install missing requirements first:")
        print("   pip install -r requirements.txt")
        return
    
    # Check API key
    if not check_api_key():
        print("\n❌ Please set up your OpenAI API key first")
        return
    
    # Setup knowledge base
    has_knowledge = setup_knowledge_base()
    
    # Run example
    example_success = run_example()
    
    print("\n" + "=" * 50)
    print("🎯 Setup Summary:")
    print(f"   Requirements: ✅")
    print(f"   API Key: ✅") 
    print(f"   Knowledge Base: {'✅' if has_knowledge else '⚠️'}")
    print(f"   Example: {'✅' if example_success else '⚠️'}")
    
    if has_knowledge and example_success:
        print("\n🎉 You're ready to generate datasets!")
        print("\n📖 Next steps:")
        print("1. Customize configuration in config.py")
        print("2. Run: python ai_dataset_generator.py")
        print("3. Use generated .jsonl file for fine-tuning")
    else:
        print("\n📋 Still needed:")
        if not has_knowledge:
            print("• Add knowledge files to knowledge_base/")
        print("• Review examples/ directory for guidance")
    
    print("\n📚 Documentation: README.md")
    print("💬 Issues: https://github.com/yourusername/ai-dataset-generator/issues")

if __name__ == "__main__":
    main()
