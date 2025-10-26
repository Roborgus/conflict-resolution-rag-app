"""
Configuration settings for the Conflict Resolution RAG App
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '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')
    MODEL_NAME = os.getenv('MODEL_NAME', 'gpt-4')
    EMBEDDINGS_MODEL = os.getenv('EMBEDDINGS_MODEL', 'text-embedding-3-small')
    
    # RAG Configuration
    CHUNK_SIZE = 400  # Fixed size to match batch indexer
    CHUNK_OVERLAP = 100  # Fixed size to match batch indexer
    TOP_K_RESULTS = int(os.getenv('TOP_K_RESULTS', 5))
    
# File paths
PDF_SOURCES_DIR = os.getenv('PDF_SOURCES_DIR', '/Users/rob/Documents/GitHub/Transformative sources_git')
VECTOR_DB_PATH = os.getenv('VECTOR_DB_PATH', './vectordb')

# Cloud deployment paths
if os.getenv('RAILWAY_ENVIRONMENT'):
    # Running on Railway
    PDF_SOURCES_DIR = os.getenv('PDF_SOURCES_DIR', './pdf_sources')
    VECTOR_DB_PATH = os.getenv('VECTOR_DB_PATH', './vectordb')
    
# Flask configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    @classmethod
    def validate_config(cls):
        """Validate that required configuration is present"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required. Please set it in your .env file.")
        
        if not os.path.exists(cls.PDF_SOURCES_DIR):
            raise ValueError(f"PDF sources directory not found: {cls.PDF_SOURCES_DIR}")
        
        return True
