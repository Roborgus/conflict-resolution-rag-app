#!/usr/bin/env python3
"""
Skript pro nahrání PDF souborů do cloudového úložiště
"""
import os
import shutil
from pathlib import Path

def upload_pdfs_to_cloud():
    """Nahraje PDF soubory do cloudového úložiště"""
    
    # Lokální cesta k PDF souborům
    local_pdf_dir = Path("/Users/rob/Documents/GitHub/Transformative sources_git")
    
    # Cloudová cesta
    cloud_pdf_dir = Path("./pdf_sources")
    
    # Vytvoř cloudovou složku
    cloud_pdf_dir.mkdir(exist_ok=True)
    
    print(f"📁 Kopíruji PDF soubory z {local_pdf_dir} do {cloud_pdf_dir}")
    
    # Najdi všechny PDF soubory
    pdf_files = list(local_pdf_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ Žádné PDF soubory nenalezeny")
        return False
    
    print(f"📄 Nalezeno {len(pdf_files)} PDF souborů")
    
    # Kopíruj soubory
    copied_count = 0
    for pdf_file in pdf_files:
        try:
            destination = cloud_pdf_dir / pdf_file.name
            shutil.copy2(pdf_file, destination)
            print(f"✅ Zkopírován: {pdf_file.name}")
            copied_count += 1
        except Exception as e:
            print(f"❌ Chyba při kopírování {pdf_file.name}: {e}")
    
    print(f"🎯 Úspěšně zkopírováno {copied_count} z {len(pdf_files)} souborů")
    return copied_count > 0

if __name__ == "__main__":
    print("🚀 Nahrávám PDF soubory pro cloud deployment...")
    success = upload_pdfs_to_cloud()
    
    if success:
        print("✅ PDF soubory úspěšně nahrány pro cloud")
    else:
        print("❌ Chyba při nahrávání PDF souborů")
