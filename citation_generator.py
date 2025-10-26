"""
Citation Generator for Conflict Resolution RAG App
Generates APA 7th edition citations for transformative conflict resolution documents
"""
import re
from typing import Dict, List


class CitationGenerator:
    """Generates APA 7th edition citations from document metadata"""
    
    def __init__(self):
        self.citation_cache = {}
    
    def clean_author_name(self, author: str) -> str:
        """Clean and format author name for APA citation"""
        if not author or author == 'Unknown':
            return 'Unknown Author'
        
        # Remove extra spaces and clean up
        author = ' '.join(author.split())
        
        # Handle multiple authors separated by commas or 'and'
        if ',' in author:
            authors = [a.strip() for a in author.split(',')]
            if len(authors) > 1:
                return f"{authors[0]}, {', '.join(authors[1:])}"
        
        return author
    
    def clean_title(self, title: str) -> str:
        """Clean and format title for APA citation"""
        if not title:
            return 'Untitled Document'
        
        # Remove file extension if present
        title = title.replace('.pdf', '')
        
        # Replace underscores with spaces
        title = title.replace('_', ' ')
        
        # Clean up extra spaces
        title = ' '.join(title.split())
        
        # Capitalize title case (APA style)
        title = self.title_case(title)
        
        return title
    
    def title_case(self, text: str) -> str:
        """Convert text to title case following APA guidelines"""
        # Words that should not be capitalized in titles
        lowercase_words = {
            'a', 'an', 'and', 'as', 'at', 'but', 'by', 'for', 'if', 'in', 'nor', 'of', 'on', 'or', 'so', 'the', 'to', 'up', 'yet'
        }
        
        words = text.split()
        result = []
        
        for i, word in enumerate(words):
            # Always capitalize first and last word
            if i == 0 or i == len(words) - 1:
                result.append(word.capitalize())
            elif word.lower() in lowercase_words:
                result.append(word.lower())
            else:
                result.append(word.capitalize())
        
        return ' '.join(result)
    
    def generate_reference_citation(self, metadata: Dict[str, str]) -> str:
        """Generate full reference citation in APA 7th format"""
        author = self.clean_author_name(metadata.get('author', 'Unknown'))
        title = self.clean_title(metadata.get('title', 'Untitled'))
        year = metadata.get('year', 'n.d.')
        filename = metadata.get('filename', '')
        
        # Format: Author, A. A. (Year). Title. Source.
        citation = f"{author} ({year}). {title}."
        
        # Add source information if available
        if 'file_path' in metadata:
            citation += f" Retrieved from {filename}"
        
        return citation
    
    def generate_in_text_citation(self, metadata: Dict[str, str]) -> str:
        """Generate in-text citation in APA 7th format"""
        author = self.clean_author_name(metadata.get('author', 'Unknown'))
        year = metadata.get('year', 'n.d.')
        
        # Format: (Author, Year)
        return f"({author}, {year})"
    
    def generate_citations_for_chunks(self, chunks: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Add citations to chunks"""
        cited_chunks = []
        
        for chunk in chunks:
            cited_chunk = chunk.copy()
            
            # Generate citations
            reference_citation = self.generate_reference_citation(chunk['metadata'])
            in_text_citation = self.generate_in_text_citation(chunk['metadata'])
            
            # Add citation info to chunk
            cited_chunk['reference_citation'] = reference_citation
            cited_chunk['in_text_citation'] = in_text_citation
            
            cited_chunks.append(cited_chunk)
        
        return cited_chunks
    
    def format_citations_for_response(self, used_sources: List[Dict[str, str]]) -> str:
        """Format citations for display in response"""
        if not used_sources:
            return ""
        
        # Get unique citations (by filename)
        unique_citations = {}
        for source in used_sources:
            filename = source.get('filename', 'Unknown')
            if filename not in unique_citations:
                # Generate citation for this source
                citation = self.generate_reference_citation(source)
                unique_citations[filename] = citation
        
        # Format as numbered list
        citations_text = "\n\n**Použité zdroje:**\n"
        for i, citation in enumerate(unique_citations.values(), 1):
            citations_text += f"{i}. {citation}\n"
        
        return citations_text
    
    def extract_citation_info(self, chunk: Dict[str, str]) -> Dict[str, str]:
        """Extract citation information from a chunk"""
        return {
            'author': self.clean_author_name(chunk['metadata'].get('author', 'Unknown')),
            'year': chunk['metadata'].get('year', 'n.d.'),
            'title': self.clean_title(chunk['metadata'].get('title', 'Untitled')),
            'filename': chunk['metadata'].get('filename', ''),
            'reference_citation': self.generate_reference_citation(chunk['metadata']),
            'in_text_citation': self.generate_in_text_citation(chunk['metadata'])
        }


def main():
    """Test the citation generator"""
    generator = CitationGenerator()
    
    # Test metadata
    test_metadata = {
        'author': 'Bush, Folger',
        'title': 'The promise of mediation_ the transformative approach to conflict',
        'year': '2005',
        'filename': 'Bush, Folger - The promise of mediation_ the transformative approach to conflict.pdf'
    }
    
    print("Test citací:")
    print(f"Reference: {generator.generate_reference_citation(test_metadata)}")
    print(f"In-text: {generator.generate_in_text_citation(test_metadata)}")


if __name__ == "__main__":
    main()
