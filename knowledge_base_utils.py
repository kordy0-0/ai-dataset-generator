#!/usr/bin/env python3
"""
Knowledge Base Utilities
Helper functions for processing and managing knowledge base files

This module provides utilities to:
- Extract text from PDFs
- Process markdown files
- Convert various document formats
- Organize knowledge base structure
"""

import fitz  # PyMuPDF
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import re


class KnowledgeBaseProcessor:
    """Utility class for processing knowledge base documents"""
    
    def __init__(self, output_dir: str = "knowledge_base"):
        """Initialize the processor with an output directory"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def extract_text_from_pdf(self, pdf_path: str, output_path: Optional[str] = None) -> str:
        """
        Extract text from PDF file
        
        Args:
            pdf_path: Path to PDF file
            output_path: Optional path to save extracted text
            
        Returns:
            Extracted text content
        """
        try:
            doc = fitz.open(pdf_path)
            text_content = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                
                # Clean up the text
                text = self._clean_text(text)
                text_content.append(f"# Page {page_num + 1}\n\n{text}\n")
            
            doc.close()
            
            full_text = "\n".join(text_content)
            
            # Save to file if output path specified
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(full_text)
                print(f"✅ Extracted text saved to: {output_path}")
            
            return full_text
            
        except Exception as e:
            print(f"❌ Error extracting text from {pdf_path}: {e}")
            return ""
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        # Fix common OCR issues
        text = text.replace('ﬁ', 'fi')
        text = text.replace('ﬂ', 'fl')
        text = text.replace(''', "'")
        text = text.replace('"', '"')
        text = text.replace('"', '"')
        
        return text.strip()
    
    def process_pdf_directory(self, pdf_dir: str, output_subdir: str = "pdf_extracts") -> List[str]:
        """
        Process all PDFs in a directory
        
        Args:
            pdf_dir: Directory containing PDF files
            output_subdir: Subdirectory to save extracted text files
            
        Returns:
            List of paths to extracted text files
        """
        pdf_path = Path(pdf_dir)
        if not pdf_path.exists():
            print(f"❌ Directory not found: {pdf_dir}")
            return []
        
        output_path = self.output_dir / output_subdir
        output_path.mkdir(exist_ok=True)
        
        extracted_files = []
        pdf_files = list(pdf_path.glob("*.pdf"))
        
        if not pdf_files:
            print(f"⚠️ No PDF files found in {pdf_dir}")
            return []
        
        print(f"📄 Processing {len(pdf_files)} PDF files...")
        
        for pdf_file in pdf_files:
            output_file = output_path / f"{pdf_file.stem}.md"
            text = self.extract_text_from_pdf(str(pdf_file), str(output_file))
            
            if text:
                extracted_files.append(str(output_file))
                print(f"✅ Processed: {pdf_file.name}")
            else:
                print(f"❌ Failed to process: {pdf_file.name}")
        
        return extracted_files
    
    def create_knowledge_base_structure(self, domain: str) -> Dict[str, str]:
        """
        Create organized directory structure for a domain
        
        Args:
            domain: Domain name (e.g., "medical", "legal", "financial")
            
        Returns:
            Dictionary mapping content types to directory paths
        """
        domain_path = self.output_dir / domain.lower().replace(" ", "_")
        
        directories = {
            "main": str(domain_path),
            "pdfs": str(domain_path / "pdfs"),
            "markdown": str(domain_path / "markdown"), 
            "extracted": str(domain_path / "extracted"),
            "processed": str(domain_path / "processed")
        }
        
        # Create directories
        for dir_path in directories.values():
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        # Create README
        readme_content = f"""# {domain} Knowledge Base

This directory contains knowledge base files for {domain} domain.

## Directory Structure

- `pdfs/` - Original PDF documents
- `markdown/` - Markdown documentation files  
- `extracted/` - Text extracted from PDFs
- `processed/` - Processed and cleaned knowledge files

## Usage

1. Add your source documents to the appropriate directories
2. Run the knowledge base processor to extract and clean text
3. Use the processed files for dataset generation

## Generated on: {self._get_timestamp()}
"""
        
        readme_path = domain_path / "README.md"
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        
        print(f"📁 Created knowledge base structure for {domain}")
        print(f"📁 Main directory: {directories['main']}")
        
        return directories
    
    def _get_timestamp(self) -> str:
        """Get current timestamp string"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def combine_knowledge_files(self, input_dir: str, output_file: str, 
                               file_pattern: str = "*.md") -> str:
        """
        Combine multiple knowledge files into a single file
        
        Args:
            input_dir: Directory containing knowledge files
            output_file: Path for combined output file
            file_pattern: File pattern to match (e.g., "*.md", "*.txt")
            
        Returns:
            Path to the combined file
        """
        input_path = Path(input_dir)
        files = list(input_path.glob(file_pattern))
        
        if not files:
            print(f"⚠️ No files matching {file_pattern} found in {input_dir}")
            return ""
        
        combined_content = []
        combined_content.append(f"# Combined Knowledge Base\n")
        combined_content.append(f"Generated from {len(files)} files on {self._get_timestamp()}\n\n")
        
        for file_path in sorted(files):
            print(f"📄 Adding: {file_path.name}")
            
            combined_content.append(f"## {file_path.stem}\n")
            combined_content.append(f"*Source: {file_path.name}*\n\n")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    combined_content.append(content)
                    combined_content.append("\n\n---\n\n")
            except Exception as e:
                print(f"⚠️ Error reading {file_path}: {e}")
        
        # Write combined file
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(combined_content))
        
        print(f"✅ Combined {len(files)} files into: {output_file}")
        return str(output_path)
    
    def analyze_knowledge_base(self, knowledge_dir: str) -> Dict[str, Any]:
        """
        Analyze knowledge base content and provide statistics
        
        Args:
            knowledge_dir: Directory containing knowledge files
            
        Returns:
            Dictionary with analysis results
        """
        kb_path = Path(knowledge_dir)
        if not kb_path.exists():
            return {"error": f"Directory not found: {knowledge_dir}"}
        
        analysis = {
            "directory": str(kb_path),
            "file_counts": {},
            "total_files": 0,
            "total_size_mb": 0,
            "content_stats": {
                "total_chars": 0,
                "total_words": 0,
                "avg_words_per_file": 0
            }
        }
        
        # Count files by type
        file_types = ['.pdf', '.md', '.txt', '.markdown']
        for file_type in file_types:
            files = list(kb_path.glob(f"**/*{file_type}"))
            analysis["file_counts"][file_type] = len(files)
            analysis["total_files"] += len(files)
        
        # Calculate total size
        total_size = sum(f.stat().st_size for f in kb_path.glob("**/*") if f.is_file())
        analysis["total_size_mb"] = round(total_size / (1024 * 1024), 2)
        
        # Analyze text content
        text_files = list(kb_path.glob("**/*.md")) + list(kb_path.glob("**/*.txt"))
        total_words = 0
        total_chars = 0
        
        for text_file in text_files:
            try:
                with open(text_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    total_chars += len(content)
                    total_words += len(content.split())
            except Exception:
                continue
        
        analysis["content_stats"]["total_chars"] = total_chars
        analysis["content_stats"]["total_words"] = total_words
        if text_files:
            analysis["content_stats"]["avg_words_per_file"] = round(total_words / len(text_files))
        
        return analysis


def setup_knowledge_base_interactive():
    """Interactive setup for knowledge base"""
    print("🚀 Knowledge Base Setup Wizard")
    print("=" * 40)
    
    processor = KnowledgeBaseProcessor()
    
    # Get domain information
    domain = input("Enter your domain (e.g., Medical, Legal, Finance): ").strip()
    if not domain:
        domain = "General"
    
    # Create structure
    directories = processor.create_knowledge_base_structure(domain)
    
    print(f"\n📁 Created knowledge base structure:")
    for name, path in directories.items():
        print(f"  {name}: {path}")
    
    # Ask about PDF processing
    has_pdfs = input("\nDo you have PDF files to process? (y/n): ").lower().startswith('y')
    
    if has_pdfs:
        pdf_dir = input("Enter path to directory containing PDFs: ").strip()
        if pdf_dir and Path(pdf_dir).exists():
            extracted_files = processor.process_pdf_directory(pdf_dir, f"{domain.lower()}_extracted")
            print(f"✅ Extracted text from {len(extracted_files)} PDFs")
        else:
            print("⚠️ PDF directory not found or not specified")
    
    # Provide next steps
    print(f"\n🎉 Knowledge base setup complete!")
    print(f"\n📋 Next steps:")
    print(f"1. Add your documents to: {directories['main']}")
    print(f"2. Configure ai_dataset_generator.py to use: knowledge_sources=['{directories['main']}']")
    print(f"3. Run: python ai_dataset_generator.py")
    
    return directories


if __name__ == "__main__":
    setup_knowledge_base_interactive()
