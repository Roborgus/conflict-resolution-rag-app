"""
Flask Web Application for Conflict Resolution RAG - CLOUD VERSION
Optimized for Railway deployment
"""
import os
import json
from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
from pathlib import Path

from config import Config
from rag_engine import RAGEngine
from batch_indexer import BatchIndexer

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize RAG engine
rag_engine = None

def get_rag_engine():
    """Get or initialize RAG engine"""
    global rag_engine
    if rag_engine is None:
        try:
            print("Inicializuji RAG engine...")
            rag_engine = RAGEngine()
            print("RAG engine úspěšně inicializován")
        except Exception as e:
            print(f"Chyba při inicializaci RAG engine: {e}")
            import traceback
            traceback.print_exc()
            return None
    return rag_engine

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/query', methods=['POST'])
def query():
    """Handle user queries"""
    try:
        data = request.get_json()
        query_text = data.get('query', '').strip()
        
        if not query_text:
            return jsonify({
                'error': 'Prázdný dotaz',
                'response': 'Zadejte prosím dotaz o transformativním přístupu ke konfliktům.'
            }), 400
        
        # Get RAG engine
        rag = get_rag_engine()
        if not rag:
            return jsonify({
                'error': 'RAG engine není dostupný',
                'response': 'Systém není připraven. Zkontrolujte konfiguraci.'
            }), 500
        
        # Generate response
        result = rag.generate_response(query_text)
        
        return jsonify({
            'response': result['response'],
            'sources': result['sources'],
            'citations': result['citations'],
            'num_sources': result.get('num_sources', len(result.get('sources', [])))
        })
    except Exception as e:
        print(f"Chyba při zpracování dotazu: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'Chyba při zpracování dotazu: {str(e)}',
            'response': 'Omlouvám se, ale došlo k chybě při zpracování vašeho dotazu.'
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Return database statistics"""
    try:
        rag = get_rag_engine()
        if not rag:
            return jsonify({
                'status': 'error',
                'message': 'RAG engine není dostupný'
            }), 500
        
        stats = rag.get_database_stats()
        return jsonify({
            'status': 'healthy',
            'database_documents': stats.get('total_documents', 0),
            'message': 'Aplikace je připravena'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Chyba: {str(e)}'
        }), 500

@app.route('/api/batch_index', methods=['POST'])
def batch_index_documents():
    """Index documents using batch indexer"""
    try:
        indexer = BatchIndexer(batch_size=2, delay_between_batches=3.0)
        results = indexer.index_all_documents()

        if results['success']:
            global rag_engine
            rag_engine = None  # Force reinitialization
            return jsonify({
                'message': 'Batch indexace dokončena úspěšně',
                'success': True,
                'total_processed': results['total_processed'],
                'total_chunks': results['total_chunks'],
                'total_failed': results['total_failed']
            })
        else:
            return jsonify({
                'error': 'Batch indexace selhala',
                'success': False,
                'details': results.get('error', 'Neznámá chyba')
            }), 500

    except Exception as e:
        return jsonify({'error': f'Chyba při batch indexaci: {str(e)}', 'success': False}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint nenalezen'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Vnitřní chyba serveru'}), 500

def initialize_app():
    """Initialize the application"""
    try:
        # Validate configuration
        Config.validate_config()
        
        # Initialize RAG engine
        global rag_engine
        print("Inicializuji RAG engine...")
        rag_engine = RAGEngine()
        print("RAG engine úspěšně inicializován")
        
        # Check if database needs indexing
        stats = rag_engine.get_database_stats()
        print(f"Statistiky databáze: {stats}")
        
        if stats.get('total_documents', 0) == 0:
            print("Databáze je prázdná, začínám indexaci...")
            # Use BatchIndexer for initial indexing with smaller batches for cloud
            indexer = BatchIndexer(batch_size=2, delay_between_batches=3.0)
            index_results = indexer.index_all_documents()
            if index_results['success']:
                print("Indexace dokončena úspěšně")
                # Reinitialize RAG engine to load the newly indexed data
                rag_engine = RAGEngine()
            else:
                print("Chyba při indexaci")
        else:
            print(f"Databáze obsahuje {stats.get('total_documents', 0)} dokumentů")
        
        print("Aplikace je připravena")
        return True
        
    except Exception as e:
        print(f"Chyba při inicializaci aplikace: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("Spouštím Conflict Resolution RAG App - CLOUD VERSION...")
    
    # Initialize the application
    if initialize_app():
        print("Aplikace úspěšně inicializována")
        print("Spouštím Flask server...")
        
        # Get port from environment (Railway provides this)
        port = int(os.getenv('PORT', 5000))
        
        app.run(debug=False, host='0.0.0.0', port=port)
    else:
        print("Chyba při inicializaci aplikace")
        print("Zkontrolujte konfiguraci a API klíče")
