# Enhanced PDF Parser with Source Tracking

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python tool designed for deep parsing of PDF documents, with a unique focus on extracting not just the text but also its associated sources or citations. It's built for researchers, data scientists, and anyone needing to analyze academic papers, reports, or legal documents while maintaining a clear link between text segments and their original references.

This parser uses `PyMuPDF` for robust text extraction and `spaCy` for intelligent, NLP-based sentence segmentation.

## Features

* **Full Text Extraction**: Parses entire PDF documents and extracts clean, readable text.
* **Source/Citation Tracking**: Uniquely identifies and extracts source annotations (e.g., ``, ``) alongside the text on a page-by-page basis.
* **Advanced Text Cleaning**: Utilizes regular expressions to remove unnecessary line breaks, extra spaces, and other common OCR artifacts.
* **NLP-Powered Sentence Segmentation**: Leverages `spaCy` for accurate sentence tokenization, preserving the grammatical structure of the text.
* **Text Analysis & Statistics**: Automatically calculates key statistics, including word count, unique word count, and the most common words.
* **Structured Output**: Provides extracted data—full text, sentences, sources, and stats—in clean, accessible formats.

## Installation

To use this parser, you need to install the necessary libraries. It is highly recommended to use a virtual environment.

1.  **Install required Python packages:**

    ```bash
    pip install PyMuPDF spacy
    ```

2.  **Download the spaCy English language model:**

    ```bash
    python -m spacy download en_core_web_sm
    ```

## Usage

Here is a basic example of how to use the `EnhancedPDFParser`.

```python
# main_script.py
from enhanced_pdf_parser_with_sources import EnhancedPDFParser
import logging

def main():
    """Demonstrates the usage of the EnhancedPDFParser."""
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Path to your PDF file
    pdf_file_path = 'path/to/your/document.pdf' # IMPORTANT: Change this to your PDF file path

    try:
        # 1. Initialize the parser with the PDF path
        parser = EnhancedPDFParser(pdf_path=pdf_file_path)
        logging.info(f"Successfully initialized parser for: {pdf_file_path}")

        # 2. Extract text and sources
        parser.extract_text_and_sources()
        logging.info("Text and sources extracted.")

        # 3. Analyze the extracted text
        parser.analyze_text()
        logging.info("Text analysis complete.")

        # 4. Retrieve the results
        full_text = parser.get_full_text()
        stats = parser.get_stats()
        sources = parser.get_sources()
        sentences = parser.get_sentences()

        # 5. Print the results
        print("\n" + "="*50)
        print("          PDF PARSER ANALYSIS REPORT")
        print("="*50)

        print("\n--- Extracted Statistics ---")
        for key, value in stats.items():
            if key != 'most_common_words':
                print(f"{key.replace('_', ' ').title()}: {value}")
        print("Most Common Words:", stats.get('most_common_words', []))
        
        print("\n--- Extracted Sources (First 5) ---")
        for i, (page, source_list) in enumerate(sources.items()):
            if i >= 5:
                print("... and more.")
                break
            print(f"Page {page}: {source_list}")

        print("\n--- Extracted Sentences (First 5) ---")
        for i, sentence in enumerate(sentences):
            if i >= 5:
                print("...")
                break
            print(f"[{i+1}] {sentence}")

    except FileNotFoundError:
        logging.error(f"Error: The file was not found at '{pdf_file_path}'")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    main()

```

## How It Works

The engine operates in a few key steps:
1.  **PDF Loading**: It uses the `fitz` library (from PyMuPDF) to open and read the PDF file page by page.
2.  **Source Pattern Matching**: For each page, it scans the text to find and isolate citation patterns like `` using regular expressions. This allows it to link sources to specific pages.
3.  **Text Cleaning**: Raw extracted text is cleaned to normalize whitespace and remove artifacts.
4.  **NLP Sentence Segmentation**: The entire cleaned text is processed by a `spaCy` language model, which accurately splits the text into a structured list of sentences.
5.  **Statistical Analysis**: Basic text statistics are computed from the processed text to provide a quick overview of the document's content.

## Contributing

Contributions are welcome! If you would like to contribute to this project, please feel free to fork the repository, make your changes, and submit a pull request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
