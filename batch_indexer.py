"""
Batch indexer pro postupné zpracování dokumentů
Řeší problém s překročením limitu tokenů při indexaci
"""
import os
import time
from pathlib import Path
from typing import List, Dict, Any
from pdf_processor import PDFProcessor
from rag_engine import RAGEngine
from config import Config

class BatchIndexer:
    def __init__(self, batch_size: int = 5, delay_between_batches: float = 2.0):
        """
        Inicializace batch indexeru
        
        Args:
            batch_size: Počet dokumentů na jednu dávku
            delay_between_batches: Zpoždění mezi dávkami (sekundy)
        """
        self.batch_size = batch_size
        self.delay_between_batches = delay_between_batches
        self.pdf_processor = PDFProcessor()
        self.rag_engine = RAGEngine()
        self.processed_files = []
        self.failed_files = []
        
    def get_pdf_files(self) -> List[str]:
        """Získá seznam všech PDF souborů"""
        pdf_dir = Path(Config.PDF_SOURCES_DIR)
        if not pdf_dir.exists():
            raise FileNotFoundError(f"Složka {pdf_dir} neexistuje")
            
        pdf_files = list(pdf_dir.glob("*.pdf"))
        print(f"Nalezeno {len(pdf_files)} PDF souborů")
        return [str(f) for f in pdf_files]
    
    def process_batch(self, pdf_files: List[str]) -> Dict[str, Any]:
        """
        Zpracuje jednu dávku dokumentů
        
        Args:
            pdf_files: Seznam cest k PDF souborům
            
        Returns:
            Slovník s výsledky zpracování
        """
        batch_results = {
            'processed': 0,
            'failed': 0,
            'total_chunks': 0,
            'errors': []
        }
        
        print(f"Zpracovávám dávku {len(pdf_files)} dokumentů...")
        
        for pdf_file in pdf_files:
            try:
                print(f"Zpracovávám: {os.path.basename(pdf_file)}")
                
                # Extrakce textu a metadat
                text, metadata = self.pdf_processor.extract_text_and_metadata(pdf_file)
                
                if not text.strip():
                    print(f"Žádný text nebyl extrahován z {os.path.basename(pdf_file)}")
                    batch_results['failed'] += 1
                    self.failed_files.append(pdf_file)
                    continue
                
                # Chunking textu
                chunks = self.pdf_processor.chunk_text(text, metadata)
                print(f"Vytvořeno {len(chunks)} chunků z {os.path.basename(pdf_file)}")
                
                # Převod chunks na Document objekty a přidání do vektorové databáze
                if chunks:
                    from langchain.schema import Document
                    documents = []
                    for chunk in chunks:
                        doc = Document(
                            page_content=chunk['text'],
                            metadata={
                                'id': chunk['id'],
                                'filename': chunk['metadata']['filename'],
                                'author': chunk['metadata']['author'],
                                'title': chunk['metadata']['title'],
                                'year': chunk['metadata']['year'],
                                'chunk_index': chunk['chunk_index']
                            }
                        )
                        documents.append(doc)
                    
                    self.rag_engine.add_documents_to_vectorstore(documents)
                    batch_results['total_chunks'] += len(chunks)
                    batch_results['processed'] += 1
                    self.processed_files.append(pdf_file)
                
            except Exception as e:
                error_msg = f"Chyba při zpracování {os.path.basename(pdf_file)}: {str(e)}"
                print(error_msg)
                batch_results['errors'].append(error_msg)
                batch_results['failed'] += 1
                self.failed_files.append(pdf_file)
        
        return batch_results
    
    def index_all_documents(self) -> Dict[str, Any]:
        """
        Postupně zpracuje všechny dokumenty po dávkách
        
        Returns:
            Celkové výsledky indexace
        """
        print("🚀 Začínám postupné indexování dokumentů...")
        
        # Získání seznamu PDF souborů
        try:
            pdf_files = self.get_pdf_files()
        except FileNotFoundError as e:
            return {
                'success': False,
                'error': str(e),
                'total_processed': 0,
                'total_failed': 0,
                'total_chunks': 0
            }
        
        if not pdf_files:
            return {
                'success': False,
                'error': 'Nebyly nalezeny žádné PDF soubory',
                'total_processed': 0,
                'total_failed': 0,
                'total_chunks': 0
            }
        
        # Rozdělení na dávky
        batches = [pdf_files[i:i + self.batch_size] for i in range(0, len(pdf_files), self.batch_size)]
        
        print(f"Celkem {len(pdf_files)} souborů rozděleno do {len(batches)} dávek")
        
        total_results = {
            'total_processed': 0,
            'total_failed': 0,
            'total_chunks': 0,
            'all_errors': []
        }
        
        # Zpracování každé dávky
        for i, batch in enumerate(batches, 1):
            print(f"\n📦 Zpracovávám dávku {i}/{len(batches)} ({len(batch)} dokumentů)")
            
            try:
                batch_results = self.process_batch(batch)
                
                # Aktualizace celkových výsledků
                total_results['total_processed'] += batch_results['processed']
                total_results['total_failed'] += batch_results['failed']
                total_results['total_chunks'] += batch_results['total_chunks']
                total_results['all_errors'].extend(batch_results['errors'])
                
                print(f"✅ Dávka {i} dokončena: {batch_results['processed']} úspěšných, {batch_results['failed']} neúspěšných")
                
                # Zpoždění mezi dávkami (kromě poslední)
                if i < len(batches):
                    print(f"⏳ Čekám {self.delay_between_batches}s před další dávkou...")
                    time.sleep(self.delay_between_batches)
                    
            except Exception as e:
                error_msg = f"Chyba při zpracování dávky {i}: {str(e)}"
                print(f"❌ {error_msg}")
                total_results['all_errors'].append(error_msg)
        
        # Finální výsledky
        success = total_results['total_processed'] > 0
        
        print(f"\n🎯 Indexace dokončena!")
        print(f"✅ Úspěšně zpracováno: {total_results['total_processed']} dokumentů")
        print(f"❌ Neúspěšně: {total_results['total_failed']} dokumentů")
        print(f"📄 Celkem chunků: {total_results['total_chunks']}")
        
        if total_results['all_errors']:
            print(f"\n⚠️ Chyby:")
            for error in total_results['all_errors'][:5]:  # Zobrazit max 5 chyb
                print(f"  - {error}")
            if len(total_results['all_errors']) > 5:
                print(f"  ... a {len(total_results['all_errors']) - 5} dalších chyb")
        
        return {
            'success': success,
            'total_processed': total_results['total_processed'],
            'total_failed': total_results['total_failed'],
            'total_chunks': total_results['total_chunks'],
            'errors': total_results['all_errors'],
            'processed_files': self.processed_files,
            'failed_files': self.failed_files
        }

def main():
    """Hlavní funkce pro spuštění batch indexování"""
    print("🔄 Spouštím batch indexování...")
    
    # Vytvoření indexeru s menšími dávkami
    indexer = BatchIndexer(batch_size=3, delay_between_batches=3.0)
    
    # Spuštění indexace
    results = indexer.index_all_documents()
    
    if results['success']:
        print(f"\n🎉 Indexace úspěšně dokončena!")
        print(f"📊 Statistiky:")
        print(f"  - Zpracováno dokumentů: {results['total_processed']}")
        print(f"  - Celkem chunků: {results['total_chunks']}")
        print(f"  - Neúspěšných: {results['total_failed']}")
    else:
        print(f"\n❌ Indexace selhala!")
        if 'error' in results:
            print(f"Chyba: {results['error']}")
    
    return results

if __name__ == "__main__":
    main()
