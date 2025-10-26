"""
PDF Processor for Conflict Resolution RAG App
Extracts text and metadata from PDF documents about transformative conflict resolution
"""
import os
import re
from pathlib import Path
from typing import List, Dict, Tuple
import fitz  # PyMuPDF
from config import Config


class PDFProcessor:
    """Processes PDF documents and extracts text with metadata"""
    
    def __init__(self):
        self.sources_dir = Path(Config.PDF_SOURCES_DIR)
        self.chunk_size = Config.CHUNK_SIZE
        self.chunk_overlap = Config.CHUNK_OVERLAP
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF using PyMuPDF (most reliable method)"""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            
            for page_num in range(doc.page_count):
                page = doc[page_num]
                page_text = page.get_text()
                if page_text.strip():
                    text += f"\n--- Stránka {page_num + 1} ---\n"
                    text += page_text
            
            doc.close()
            return text.strip()
            
        except Exception as e:
            print(f"Chyba při čtení PDF {pdf_path}: {e}")
            return ""
    
    def extract_metadata_from_filename(self, filename: str) -> Dict[str, str]:
        """Extract basic metadata from filename"""
        # Remove .pdf extension
        name = filename.replace('.pdf', '')
        
        # Try to extract author and title patterns
        metadata = {
            'filename': filename,
            'title': name,
            'author': 'Unknown',
            'year': 'Unknown',
            'source_type': 'document'
        }
        
        # Common patterns for academic papers
        # Pattern: Author_Title.pdf
        if '_' in name:
            parts = name.split('_')
            if len(parts) >= 2:
                # First part might be author
                potential_author = parts[0]
                if len(potential_author.split()) <= 3:  # Reasonable author name length
                    metadata['author'] = potential_author.replace('_', ' ')
                    metadata['title'] = '_'.join(parts[1:]).replace('_', ' ')
        
        # Pattern: Author, Title.pdf
        if ',' in name and '_' not in name:
            parts = name.split(',')
            if len(parts) >= 2:
                metadata['author'] = parts[0].strip()
                metadata['title'] = parts[1].strip()
        
        # Look for year in filename
        year_match = re.search(r'\b(19|20)\d{2}\b', name)
        if year_match:
            metadata['year'] = year_match.group()
        
        return metadata
    
    def chunk_text(self, text: str, metadata: Dict[str, str]) -> List[Dict[str, str]]:
        """Split text into overlapping chunks with metadata"""
        if not text.strip():
            return []
        
        # Split by paragraphs first
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        chunks = []
        current_chunk = ""
        chunk_id = 0
        
        for paragraph in paragraphs:
            # If adding this paragraph would exceed chunk size
            if len(current_chunk) + len(paragraph) > self.chunk_size and current_chunk:
                # Save current chunk
                chunks.append({
                    'id': f"{metadata['filename']}_chunk_{chunk_id}",
                    'text': current_chunk.strip(),
                    'metadata': metadata.copy(),
                    'chunk_index': chunk_id
                })
                chunk_id += 1
                
                # Start new chunk with overlap
                overlap_text = current_chunk[-self.chunk_overlap:] if len(current_chunk) > self.chunk_overlap else current_chunk
                current_chunk = overlap_text + "\n\n" + paragraph
            else:
                current_chunk += "\n\n" + paragraph if current_chunk else paragraph
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append({
                'id': f"{metadata['filename']}_chunk_{chunk_id}",
                'text': current_chunk.strip(),
                'metadata': metadata.copy(),
                'chunk_index': chunk_id
            })
        
        return chunks
    
    def process_single_pdf(self, pdf_path: str) -> List[Dict[str, str]]:
        """Process a single PDF file and return chunks"""
        print(f"Zpracovávám: {pdf_path}")
        
        # Extract text
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            print(f"Žádný text nebyl extrahován z {pdf_path}")
            return []
        
        # Extract metadata
        filename = os.path.basename(pdf_path)
        metadata = self.extract_metadata_from_filename(filename)
        
        # Add file path to metadata
        metadata['file_path'] = pdf_path
        
        # Chunk the text
        chunks = self.chunk_text(text, metadata)
        
        print(f"Vytvořeno {len(chunks)} chunků z {filename}")
        return chunks
    
    def process_all_pdfs(self) -> List[Dict[str, str]]:
        """Process all PDF files in the sources directory"""
        if not self.sources_dir.exists():
            raise FileNotFoundError(f"Sources directory not found: {self.sources_dir}")
        
        all_chunks = []
        pdf_files = list(self.sources_dir.glob("*.pdf"))
        
        if not pdf_files:
            print(f"Žádné PDF soubory nenalezeny v {self.sources_dir}")
            return []
        
        print(f"Nalezeno {len(pdf_files)} PDF souborů")
        
        for pdf_file in pdf_files:
            try:
                chunks = self.process_single_pdf(str(pdf_file))
                all_chunks.extend(chunks)
            except Exception as e:
                print(f"Chyba při zpracování {pdf_file}: {e}")
                continue
        
        print(f"Celkem zpracováno {len(all_chunks)} chunků z {len(pdf_files)} souborů")
        return all_chunks
    
    def extract_text_and_metadata(self, pdf_path: str) -> Tuple[str, Dict[str, str]]:
        """Extract text and metadata from a single PDF file"""
        # Extract text
        text = self.extract_text_from_pdf(pdf_path)
        
        # Extract metadata
        filename = os.path.basename(pdf_path)
        metadata = self.extract_metadata_from_filename(filename)
        metadata['file_path'] = pdf_path
        
        return text, metadata
    
    def get_document_list(self) -> List[Dict[str, str]]:
        """Get list of all PDF documents with basic info"""
        if not self.sources_dir.exists():
            return []
        
        documents = []
        for pdf_file in self.sources_dir.glob("*.pdf"):
            metadata = self.extract_metadata_from_filename(pdf_file.name)
            metadata['file_path'] = str(pdf_file)
            metadata['file_size'] = os.path.getsize(pdf_file)
            documents.append(metadata)
        
        return documents


def main():
    """Test the PDF processor"""
    processor = PDFProcessor()
    
    # Test processing all PDFs
    print("Testování PDF procesoru...")
    chunks = processor.process_all_pdfs()
    
    if chunks:
        print(f"\nPrvní chunk jako příklad:")
        print(f"ID: {chunks[0]['id']}")
        print(f"Autor: {chunks[0]['metadata']['author']}")
        print(f"Název: {chunks[0]['metadata']['title']}")
        print(f"Text (prvních 200 znaků): {chunks[0]['text'][:200]}...")


if __name__ == "__main__":
    main()
