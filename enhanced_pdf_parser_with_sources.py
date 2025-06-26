#!/usr/bin/env python3
"""
Enhanced PDF Parser with Source Tracking
Processes multiple PDFs and maintains source attribution throughout the pipeline
Full English version for numerical analysis
"""

import PyPDF2
import os
import re
import json
import logging
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass

@dataclass
class SourceDocument:
    """Document with source attribution"""
    source_id: str
    source_label: str
    file_path: str
    raw_text: str
    cleaned_text: str
    processing_timestamp: str

class EnhancedPDFParser:
    """
    Enhanced PDF parser with source tracking and text cleaning for numerical analysis
    """
    
    def __init__(self, log_level: str = 'INFO'):
        # Setup logging
        self.logger = logging.getLogger('EnhancedPDFParser')
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        log_filename = f'pdf_parser_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        file_handler = logging.FileHandler(log_filename)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Processing statistics
        self.processing_stats = {
            'total_documents': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'total_text_length': 0,
            'source_mapping': {}
        }
        
        self.logger.info("EnhancedPDFParser initialized successfully")
        self.logger.info(f"Processing log file: {log_filename}")
    
    def process_multiple_pdfs(self, pdf_configs: List[Dict[str, str]]) -> List[SourceDocument]:
        """
        Process multiple PDFs with source attribution
        
        Args:
            pdf_configs: List of dicts with 'path', 'source_id', 'source_label'
            Example: [
                {'path': 'paper1.pdf', 'source_id': 'SRC_001', 'source_label': 'Source One'},
                {'path': 'paper2.pdf', 'source_id': 'SRC_002', 'source_label': 'Source Two'},
                {'path': 'paper3.pdf', 'source_id': 'SRC_003', 'source_label': 'Source Three'}
            ]
        
        Returns:
            List of SourceDocument objects with cleaned text and source attribution
        """
        
        self.logger.info(f"Starting processing of {len(pdf_configs)} PDF documents")
        
        processed_documents = []
        
        for i, config in enumerate(pdf_configs, 1):
            self.logger.info(f"Processing document {i}/{len(pdf_configs)}: {config['source_label']}")
            
            try:
                # Extract raw text
                raw_text = self._extract_text_from_pdf(config['path'])
                
                # Clean text for numerical analysis
                cleaned_text = self._clean_text_for_numerical_extraction(raw_text)
                
                # Create source document
                source_doc = SourceDocument(
                    source_id=config['source_id'],
                    source_label=config['source_label'],
                    file_path=config['path'],
                    raw_text=raw_text,
                    cleaned_text=cleaned_text,
                    processing_timestamp=datetime.now().isoformat()
                )
                
                processed_documents.append(source_doc)
                
                # Update statistics
                self.processing_stats['successful_extractions'] += 1
                self.processing_stats['total_text_length'] += len(cleaned_text)
                self.processing_stats['source_mapping'][config['source_id']] = config['source_label']
                
                self.logger.info(f"Successfully processed {config['source_label']}: "
                               f"{len(cleaned_text)} characters extracted")
                
            except Exception as e:
                self.logger.error(f"Failed to process {config['source_label']}: {str(e)}")
                self.processing_stats['failed_extractions'] += 1
                continue
        
        self.processing_stats['total_documents'] = len(pdf_configs)
        
        self.logger.info(f"Processing completed: {self.processing_stats['successful_extractions']}"
                        f"/{self.processing_stats['total_documents']} documents successful")
        
        return processed_documents
    
    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract raw text from PDF file"""
        
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        self.logger.debug(f"Extracting text from: {pdf_path}")
        
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                self.logger.debug(f"PDF contains {num_pages} pages")
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    text += page_text + "\n"
                    
                    self.logger.debug(f"Extracted {len(page_text)} characters from page {page_num + 1}")
                    
        except Exception as e:
            raise Exception(f"Error reading PDF {pdf_path}: {str(e)}")
        
        return text.strip()
    
    def _clean_text_for_numerical_extraction(self, raw_text: str) -> str:
        """
        Clean text specifically for numerical extraction
        Focus on fixing line breaks and preserving numerical contexts
        """
        
        self.logger.debug("Starting text cleaning for numerical extraction")
        
        # Step 1: Fix broken lines that split numbers from context
        text = self._fix_numerical_line_breaks(raw_text)
        
        # Step 2: Normalize whitespace while preserving structure
        text = self._normalize_whitespace(text)
        
        # Step 3: Clean special characters but preserve numerical symbols
        text = self._clean_preserve_numerical_symbols(text)
        
        # Step 4: Remove noise while keeping numerical context
        text = self._remove_noise_keep_context(text)
        
        self.logger.debug(f"Text cleaning completed: {len(raw_text)} → {len(text)} characters")
        
        return text
    
    def _fix_numerical_line_breaks(self, text: str) -> str:
        """Fix line breaks that separate numbers from units or context"""
        
        # Fix broken numerical expressions
        # Example: "97.2\n%" → "97.2%"
        text = re.sub(r'(\d+\.?\d*)\s*\n\s*([%°])', r'\1\2', text)
        
        # Fix broken scientific notation
        # Example: "1.5 × 10\n-6" → "1.5 × 10^-6"
        text = re.sub(r'(\d+\.?\d*\s*[×x]\s*10)\s*\n\s*([-+]?\d+)', r'\1^\2', text)
        
        # Fix broken ranges
        # Example: "90\n-\n95" → "90-95"
        text = re.sub(r'(\d+\.?\d*)\s*\n\s*[-–]\s*\n\s*(\d+\.?\d*)', r'\1-\2', text)
        
        # Fix broken error ranges
        # Example: "95.2\n±\n0.5" → "95.2±0.5"
        text = re.sub(r'(\d+\.?\d*)\s*\n\s*±\s*\n\s*(\d+\.?\d*)', r'\1±\2', text)
        
        # Fix broken units
        # Example: "37\n°C" → "37°C"
        text = re.sub(r'(\d+\.?\d*)\s*\n\s*([μmkMGT]?[gLMVAW]|°[CF]?)', r'\1\2', text)
        
        return text
    
    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace while preserving paragraph structure"""
        
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        
        # Preserve paragraph breaks (double newlines)
        text = re.sub(r'\n\n+', '\n\n', text)
        
        # Fix single line breaks within sentences
        # Keep line break if it's likely a paragraph boundary
        lines = text.split('\n')
        cleaned_lines = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                cleaned_lines.append('')
                continue
                
            # If this line and next line both end with sentence-ending punctuation,
            # keep the line break
            if (i < len(lines) - 1 and 
                line.endswith(('.', '!', '?', ':', ';')) and 
                lines[i + 1].strip()):
                cleaned_lines.append(line)
            elif i < len(lines) - 1 and lines[i + 1].strip():
                # Otherwise, prepare to join with next line
                cleaned_lines.append(line + ' ')
            else:
                cleaned_lines.append(line)
        
        return ''.join(cleaned_lines)
    
    def _clean_preserve_numerical_symbols(self, text: str) -> str:
        """Clean special characters while preserving numerical symbols"""
        
        # Remove non-essential special characters but keep numerical ones
        # Keep: . , - + × ° % ± = : / ( ) [ ] μ m k M G T g L V A W
        essential_chars = r'[a-zA-Z0-9\s\.\,\-\+×°%±=:/\(\)\[\]μmkMGTgLVAW]'
        
        # Replace non-essential characters with space
        text = re.sub(r'[^\w\s\.\,\-\+×°%±=:/\(\)\[\]μmkMGTgLVAW]', ' ', text)
        
        return text
    
    def _remove_noise_keep_context(self, text: str) -> str:
        """Remove noise while keeping numerical context"""
        
        # Remove obvious header/footer patterns
        text = re.sub(r'\n\s*Page \d+\s*\n', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)  # Standalone page numbers
        
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Clean up spaces around punctuation (but preserve numerical formats)
        text = re.sub(r'\s+([,;:])\s+', r'\1 ', text)
        
        return text.strip()
    
    def export_processed_documents(self, documents: List[SourceDocument], 
                                 output_path: str = None) -> str:
        """Export processed documents to JSON for pipeline use"""
        
        if output_path is None:
            output_path = f'processed_documents_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        export_data = {
            'processing_timestamp': datetime.now().isoformat(),
            'total_documents': len(documents),
            'processing_stats': self.processing_stats,
            'documents': []
        }
        
        for doc in documents:
            doc_data = {
                'source_id': doc.source_id,
                'source_label': doc.source_label,
                'file_path': doc.file_path,
                'text_length': len(doc.cleaned_text),
                'cleaned_text': doc.cleaned_text,
                'processing_timestamp': doc.processing_timestamp
            }
            export_data['documents'].append(doc_data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Processed documents exported to: {output_path}")
        return output_path
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get comprehensive processing statistics"""
        return self.processing_stats.copy()


def demonstrate_enhanced_pdf_parser():
    """Demonstration of enhanced PDF parser with source tracking"""
    
    print("=" * 70)
    print("Enhanced PDF Parser with Source Tracking - Demonstration")
    print("=" * 70)
    
    # Initialize parser
    parser = EnhancedPDFParser(log_level='INFO')
    
    # Example configuration for three papers
    pdf_configs = [
        {
            'path': 'dobson_2003_protein_folding.pdf',
            'source_id': 'SRC_001',
            'source_label': 'Source One'
        },
        {
            'path': 'mark_1997_kinase_study.pdf',
            'source_id': 'SRC_002', 
            'source_label': 'Source Two'
        },
        {
            'path': 'atlas_2005_proteomics.pdf',
            'source_id': 'SRC_003',
            'source_label': 'Source Three'
        }
    ]
    
    print(f"\n🔄 Processing {len(pdf_configs)} research papers...")
    
    # Process documents (would work with actual PDF files)
    try:
        processed_docs = parser.process_multiple_pdfs(pdf_configs)
        
        print(f"\n📊 Processing Results:")
        stats = parser.get_processing_statistics()
        print(f"   Successfully processed: {stats['successful_extractions']}")
        print(f"   Failed extractions: {stats['failed_extractions']}")
        print(f"   Total text extracted: {stats['total_text_length']} characters")
        
        print(f"\n📄 Processed Documents:")
        for doc in processed_docs:
            print(f"   {doc.source_label} ({doc.source_id}): {len(doc.cleaned_text)} chars")
        
        # Export for pipeline
        export_path = parser.export_processed_documents(processed_docs)
        print(f"\n💾 Documents exported to: {export_path}")
        
        print(f"\n✅ Ready for numerical extraction with source tracking!")
        
    except Exception as e:
        print(f"\n❌ Demonstration using simulated data (PDF files not found)")
        print(f"   Error: {str(e)}")
        print(f"\n📋 Expected workflow:")
        print(f"   1. PDF text extraction with source attribution")
        print(f"   2. Text cleaning for numerical analysis")
        print(f"   3. Export structured data for next pipeline stage")
        print(f"   4. Source tracking maintained throughout process")


if __name__ == "__main__":
    demonstrate_enhanced_pdf_parser()