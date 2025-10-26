# Transformativní přístup ke konfliktům - RAG Aplikace

Inteligentní webová aplikace pro vyhledávání a zodpovídání dotazů o transformativním přístupu ke konfliktům na základě akademických dokumentů. Aplikace využívá RAG (Retrieval Augmented Generation) s OpenAI GPT-4 a automaticky generuje citace ve formátu APA 7th edition.

## 🚀 Funkce

- **Sémantické vyhledávání** v dokumentech o transformativní mediace
- **Inteligentní odpovědi** generované pomocí OpenAI GPT-4
- **Automatické citace** ve formátu APA 7th edition
- **Moderní webové rozhraní** s responzivním designem
- **Správa dokumentů** s možností reindexace databáze
- **Real-time statistiky** o zpracovaných dokumentech

## 📋 Požadavky

- Python 3.8+
- OpenAI API klíč
- 2GB volného místa na disku (pro vektorovou databázi)

## 🛠️ Instalace

### 1. Klonování repozitáře
```bash
cd /Users/rob/Documents/GitHub
git clone <repository-url> conflict_resolution_app
cd conflict_resolution_app
```

### 2. Instalace závislostí
```bash
pip install -r requirements.txt
```

### 3. Konfigurace
```bash
# Zkopírujte šablonu konfigurace
cp .env.example .env

# Upravte .env soubor s vašimi údaji
nano .env
```

### 4. Získání OpenAI API klíče

1. Jděte na [OpenAI Platform](https://platform.openai.com/)
2. Přihlaste se nebo vytvořte účet
3. Jděte do sekce "API Keys"
4. Klikněte na "Create new secret key"
5. Zkopírujte klíč a vložte ho do `.env` souboru

**Příklad .env souboru:**
```env
OPENAI_API_KEY=sk-your-actual-api-key-here
CHUNK_SIZE=800
CHUNK_OVERLAP=200
TOP_K_RESULTS=5
MODEL_NAME=gpt-4
EMBEDDINGS_MODEL=text-embedding-3-small
PDF_SOURCES_DIR=../Transformative sources_git
VECTOR_DB_PATH=./vectordb
```

## 🎯 Spuštění aplikace

### 1. První spuštění
```bash
python app.py
```

Při prvním spuštění aplikace:
- Automaticky naskenuje složku `../Transformative sources_git/`
- Extrahuje text ze všech PDF dokumentů
- Vytvoří vektorovou databázi s embeddings
- Spustí webový server na `http://localhost:5000`

### 2. Přístup k aplikaci
Otevřete webový prohlížeč a jděte na:
```
http://localhost:5000
```

## 📁 Struktura projektu

```
conflict_resolution_app/
├── app.py                    # Flask webová aplikace
├── rag_engine.py            # RAG engine s ChromaDB
├── pdf_processor.py         # Zpracování PDF dokumentů
├── citation_generator.py    # Generování APA citací
├── config.py               # Konfigurace aplikace
├── requirements.txt        # Python závislosti
├── .env.example           # Šablona konfigurace
├── .env                   # Vaše konfigurace (vytvořte)
├── data/
│   └── pdfs/             # Složka pro PDF dokumenty
├── vectordb/             # ChromaDB databáze (auto-generated)
├── static/
│   ├── css/
│   │   └── style.css     # Styly aplikace
│   └── js/
│       └── app.js        # Frontend JavaScript
└── templates/
    └── index.html        # Hlavní stránka
```

## 🔧 Konfigurace

### Environment Variables

| Proměnná | Popis | Výchozí hodnota |
|----------|-------|-----------------|
| `OPENAI_API_KEY` | OpenAI API klíč | **Povinné** |
| `CHUNK_SIZE` | Velikost textových chunků | 800 |
| `CHUNK_OVERLAP` | Překryv mezi chunky | 200 |
| `TOP_K_RESULTS` | Počet relevantních dokumentů | 5 |
| `MODEL_NAME` | OpenAI model | gpt-4 |
| `EMBEDDINGS_MODEL` | Embeddings model | text-embedding-3-small |
| `PDF_SOURCES_DIR` | Složka s PDF dokumenty | ../Transformative sources_git |
| `VECTOR_DB_PATH` | Cesta k vektorové databázi | ./vectordb |

### Podporované modely

**OpenAI Modely:**
- `gpt-4` (doporučeno)
- `gpt-3.5-turbo` (rychlejší, levnější)

**Embeddings modely:**
- `text-embedding-3-small` (doporučeno)
- `text-embedding-3-large`
- `text-embedding-ada-002`

## 📚 Použití

### Základní vyhledávání
1. Zadejte dotaz do vyhledávacího pole
2. Klikněte na "Hledat" nebo stiskněte Enter
3. Aplikace vyhledá relevantní dokumenty a vygeneruje odpověď
4. Odpověď obsahuje citace ve formátu APA 7th

### Příklady dotazů
- "Co je transformativní mediace?"
- "Jaké jsou principy empowerment a recognition?"
- "Jak funguje transformativní přístup v praxi?"
- "Jaké jsou rozdíly mezi transformativní a facilitativní mediace?"

### Správa dokumentů
- **Statistiky**: Zobrazuje počet zpracovaných dokumentů
- **Seznam dokumentů**: Přehled všech dostupných PDF souborů
- **Reindexace**: Možnost znovu zpracovat všechny dokumenty

## 🔍 API Endpointy

### Hlavní endpointy
- `GET /` - Hlavní stránka
- `POST /api/query` - Vyhledávání a generování odpovědí
- `GET /api/documents` - Seznam dostupných dokumentů
- `GET /api/stats` - Statistiky databáze
- `POST /api/reindex` - Reindexace databáze
- `GET /api/health` - Kontrola stavu aplikace

### Příklad API volání
```bash
# Vyhledávání
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Co je transformativní mediace?"}'

# Statistiky
curl http://localhost:5000/api/stats
```

## 🛠️ Řešení problémů

### Časté problémy

**1. Chyba: "OPENAI_API_KEY is required"**
```bash
# Zkontrolujte .env soubor
cat .env
# Ujistěte se, že API klíč je správně nastaven
```

**2. Chyba při čtení PDF**
```bash
# Zkontrolujte, že složka s PDF existuje
ls -la ../Transformative sources_git/
# Ujistěte se, že PDF soubory nejsou poškozené
```

**3. Pomalé vyhledávání**
- Zkuste snížit `TOP_K_RESULTS` v konfiguraci
- Použijte `gpt-3.5-turbo` místo `gpt-4`
- Zkontrolujte připojení k internetu

**4. Chyba při inicializaci databáze**
```bash
# Smažte vektorovou databázi a znovu spusťte
rm -rf vectordb/
python app.py
```

### Logy a debugging
```bash
# Spuštění s debug módu
FLASK_DEBUG=1 python app.py

# Kontrola logů
tail -f app.log
```

## 📊 Výkon

### Doporučené nastavení
- **Chunk size**: 800 tokenů (optimální pro akademické texty)
- **Top K results**: 5-10 (dostatečný kontext)
- **Model**: GPT-4 (nejlepší kvalita odpovědí)

### Náklady na API
- **Embeddings**: ~$0.02 za 1M tokenů
- **GPT-4**: ~$0.03 za 1K tokenů
- **Odhad**: ~$0.10-0.50 za dotaz (závisí na délce dokumentů)

## 🔒 Bezpečnost

- API klíče jsou uloženy v `.env` souboru (nepřidávejte do git)
- Aplikace běží lokálně, data neopouštějí váš počítač
- PDF dokumenty zůstávají ve vaší složce

## 📈 Rozšíření

### Možná vylepšení
- Podpora pro více jazyků
- Export odpovědí do PDF
- Pokročilé filtry vyhledávání
- Batch zpracování dotazů
- Integrace s dalšími AI modely

### Přidání nových dokumentů
1. Přidejte PDF soubory do složky `../Transformative sources_git/`
2. Spusťte reindexaci přes webové rozhraní
3. Nebo restartujte aplikaci

## 🤝 Podpora

Pro problémy a dotazy:
1. Zkontrolujte logy aplikace
2. Ověřte konfiguraci v `.env` souboru
3. Ujistěte se, že máte platný OpenAI API klíč
4. Zkontrolujte, že PDF soubory nejsou poškozené

## 📄 Licence

Tento projekt je vytvořen pro akademické a výzkumné účely. Ujistěte se, že máte práva k použití všech PDF dokumentů.

---

**Vytvořeno pro výzkum transformativního přístupu ke konfliktům** 🤝
