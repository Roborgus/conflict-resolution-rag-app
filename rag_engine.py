"""
RAG Engine for Conflict Resolution App
Handles vector database, embeddings, and semantic search for transformative conflict resolution
"""
import os
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

import chromadb
from chromadb.config import Settings
from openai import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document

from config import Config
from pdf_processor import PDFProcessor
from citation_generator import CitationGenerator


class RAGEngine:
    """Main RAG engine for semantic search and response generation"""
    
    def __init__(self):
        self.config = Config()
        self.openai_client = OpenAI(api_key=self.config.OPENAI_API_KEY)
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=self.config.OPENAI_API_KEY,
            model=self.config.EMBEDDINGS_MODEL
        )
        
        # Initialize components
        self.pdf_processor = PDFProcessor()
        self.citation_generator = CitationGenerator()
        
        # Initialize vector database
        self.vector_db = self._initialize_vector_db()
        
        # System prompt for conflict resolution responses
        self.system_prompt = """Jste expert na transformativní přístup ke konfliktům a mediace. 
Vaše odpovědi musí být založené výhradně na poskytnutém kontextu z dokumentů o transformativní mediace.

Pravidla pro odpovědi:
1. Odpovídejte pouze na základě poskytnutého kontextu
2. Pokud informace není v kontextu, přiznejte to
3. Používejte akademický, informativní tón
4. Citace konkrétních zdrojů pro každé tvrzení
5. Odpovídejte v češtině, pokud je dotaz v češtině
6. Zaměřte se na transformativní přístup, empowerment a recognition
7. Vysvětlujte koncepty jasně a prakticky

Kontext: {context}

Dotaz: {query}

Odpověď:"""
    
    def _initialize_vector_db(self) -> Chroma:
        """Initialize or load the vector database"""
        try:
            # Try to load existing database
            if os.path.exists(self.config.VECTOR_DB_PATH):
                print("Načítám existující vektorovou databázi...")
                return Chroma(
                    persist_directory=self.config.VECTOR_DB_PATH,
                    embedding_function=self.embeddings
                )
            else:
                print("Vytvářím novou vektorovou databázi...")
                return Chroma(
                    persist_directory=self.config.VECTOR_DB_PATH,
                    embedding_function=self.embeddings
                )
        except Exception as e:
            print(f"Chyba při inicializaci vektorové databáze: {e}")
            # Create new database
            return Chroma(
                persist_directory=self.config.VECTOR_DB_PATH,
                embedding_function=self.embeddings
            )
    
    def process_and_index_documents(self) -> bool:
        """Process all PDF documents and add them to the vector database"""
        try:
            print("Zpracovávám dokumenty...")
            
            # Process all PDFs
            chunks = self.pdf_processor.process_all_pdfs()
            if not chunks:
                print("Žádné dokumenty k zpracování")
                return False
            
            # Add citations to chunks
            cited_chunks = self.citation_generator.generate_citations_for_chunks(chunks)
            
            # Convert to LangChain documents
            documents = []
            for chunk in cited_chunks:
                doc = Document(
                    page_content=chunk['text'],
                    metadata={
                        'id': chunk['id'],
                        'filename': chunk['metadata']['filename'],
                        'author': chunk['metadata']['author'],
                        'title': chunk['metadata']['title'],
                        'year': chunk['metadata']['year'],
                        'chunk_index': chunk['chunk_index'],
                        'reference_citation': chunk['reference_citation'],
                        'in_text_citation': chunk['in_text_citation']
                    }
                )
                documents.append(doc)
            
            # Add to vector database
            print(f"Přidávám {len(documents)} dokumentů do vektorové databáze...")
            self.vector_db.add_documents(documents)
            
            # Persist the database
            self.vector_db.persist()
            
            print(f"Úspěšně zpracováno a indexováno {len(documents)} chunků")
            return True
            
        except Exception as e:
            print(f"Chyba při zpracování dokumentů: {e}")
            return False
    
    def search_relevant_documents(self, query: str, top_k: int = None) -> List[Document]:
        """Search for relevant documents using semantic search"""
        if top_k is None:
            top_k = self.config.TOP_K_RESULTS
        
        try:
            # Perform similarity search
            results = self.vector_db.similarity_search(query, k=top_k)
            return results
        except Exception as e:
            print(f"Chyba při vyhledávání: {e}")
            return []
    
    def generate_response(self, query: str) -> Dict[str, Any]:
        """Generate a response to the user query using RAG"""
        try:
            # Search for relevant documents
            relevant_docs = self.search_relevant_documents(query)
            
            if not relevant_docs:
                return {
                    'response': 'Omlouvám se, ale nenašel jsem relevantní informace v dostupných dokumentech o transformativním přístupu ke konfliktům.',
                    'sources': [],
                    'citations': ''
                }
            
            # Prepare context from relevant documents
            context_parts = []
            used_sources = []
            
            for doc in relevant_docs:
                # Safe metadata access
                metadata = getattr(doc, 'metadata', {}) or {}
                title = metadata.get('title', 'Neznámý')
                author = metadata.get('author', 'Neznámý autor')
                
                context_parts.append(f"Zdroj: {title} ({author})\n{doc.page_content}")
                used_sources.append(metadata)
            
            context = "\n\n---\n\n".join(context_parts)
            
            # Generate response using OpenAI
            response = self.openai_client.chat.completions.create(
                model=self.config.MODEL_NAME,
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt.format(context=context, query=query)
                    },
                    {
                        "role": "user", 
                        "content": query
                    }
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            # Extract response text
            response_text = response.choices[0].message.content
            
            # Generate citations
            try:
                citations = self.citation_generator.format_citations_for_response(used_sources)
            except Exception as e:
                print(f"Chyba při generování citací: {e}")
                citations = ""
            
            return {
                'response': response_text,
                'sources': used_sources,
                'citations': citations,
                'num_sources': len(used_sources)
            }
            
        except Exception as e:
            print(f"Chyba při generování odpovědi: {e}")
            return {
                'response': f'Chyba při generování odpovědi: {str(e)}',
                'sources': [],
                'citations': ''
            }
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector database"""
        try:
            # Get collection info
            collection = self.vector_db._collection
            count = collection.count()
            
            return {
                'total_documents': count,
                'database_path': self.config.VECTOR_DB_PATH,
                'sources_directory': self.config.PDF_SOURCES_DIR,
                'chunk_size': self.config.CHUNK_SIZE,
                'chunk_overlap': self.config.CHUNK_OVERLAP
            }
        except Exception as e:
            return {
                'error': f'Chyba při získávání statistik: {str(e)}',
                'total_documents': 0
            }
    
    def reindex_database(self) -> bool:
        """Reindex the entire database"""
        try:
            print("Začínám reindexaci databáze...")
            
            # Clear existing database
            if os.path.exists(self.config.VECTOR_DB_PATH):
                import shutil
                shutil.rmtree(self.config.VECTOR_DB_PATH)
            
            # Reinitialize database
            self.vector_db = self._initialize_vector_db()
            
            # Process and index documents
            success = self.process_and_index_documents()
            
            if success:
                print("Reindexace dokončena úspěšně")
            else:
                print("Reindexace selhala")
            
            return success
            
        except Exception as e:
            print(f"Chyba při reindexaci: {e}")
            return False
    
    def add_documents_to_vectorstore(self, documents: List[Document]) -> bool:
        """Přidá dokumenty do vektorové databáze"""
        try:
            if not documents:
                return True
                
            print(f"Přidávám {len(documents)} dokumentů do vektorové databáze...")
            
            # Přidání dokumentů do ChromaDB
            self.vector_db.add_documents(documents)
            
            print(f"✅ Úspěšně přidáno {len(documents)} dokumentů")
            return True
            
        except Exception as e:
            print(f"❌ Chyba při přidávání dokumentů: {e}")
            return False
    
    def get_available_documents(self) -> List[Dict[str, str]]:
        """Get list of available documents"""
        return self.pdf_processor.get_document_list()


def main():
    """Test the RAG engine"""
    try:
        # Initialize RAG engine
        rag = RAGEngine()
        
        # Check if database exists and has documents
        stats = rag.get_database_stats()
        print(f"Statistiky databáze: {stats}")
        
        if stats.get('total_documents', 0) == 0:
            print("Databáze je prázdná, zpracovávám dokumenty...")
            success = rag.process_and_index_documents()
            if not success:
                print("Chyba při zpracování dokumentů")
                return
        
        # Test query
        test_query = "Co je transformativní mediace?"
        print(f"\nTestovací dotaz: {test_query}")
        
        response = rag.generate_response(test_query)
        print(f"\nOdpověď: {response['response']}")
        print(f"\nPočet zdrojů: {response['num_sources']}")
        print(f"\nCitace: {response['citations']}")
        
    except Exception as e:
        print(f"Chyba při testování RAG engine: {e}")


if __name__ == "__main__":
    main()
