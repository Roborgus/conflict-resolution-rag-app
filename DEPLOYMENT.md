# 🚀 Cloud Deployment Guide

## Railway Deployment

### 1. **Připravte aplikaci**
```bash
# Všechny soubory jsou již připraveny
# PDF soubory jsou zkopírovány do ./pdf_sources/
```

### 2. **Nahrajte na Railway**

#### **Možnost A: Railway CLI**
```bash
# Instalujte Railway CLI
npm install -g @railway/cli

# Přihlaste se
railway login

# Deploy
railway deploy
```

#### **Možnost B: GitHub + Railway**
1. Nahrajte kód na GitHub
2. Jděte na [railway.app](https://railway.app)
3. Přihlaste se a vytvořte nový projekt
4. Propojte s GitHub repozitářem
5. Railway automaticky deploy

### 3. **Environment Variables**
Nastavte v Railway dashboard:
```
OPENAI_API_KEY=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
MODEL_NAME=gpt-4
EMBEDDINGS_MODEL=text-embedding-3-small
CHUNK_SIZE=400
CHUNK_OVERLAP=100
TOP_K_RESULTS=5
PDF_SOURCES_DIR=./pdf_sources
VECTOR_DB_PATH=./vectordb
SECRET_KEY=railway-secret-key-change-in-production
RAILWAY_ENVIRONMENT=true
```

### 4. **Alternativní platformy**

#### **Heroku**
```bash
# Instalujte Heroku CLI
# Vytvořte Procfile
echo "web: python3 app_cloud.py" > Procfile

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

#### **Render**
1. Jděte na [render.com](https://render.com)
2. Vytvořte nový Web Service
3. Propojte s GitHub
4. Nastavte environment variables

### 5. **Kontrola deployment**
- Aplikace bude dostupná na Railway URL
- Zkontrolujte logy pro případné chyby
- Testujte API endpointy

## 📋 Checklist před deploymentem
- [x] PDF soubory zkopírovány do ./pdf_sources/
- [x] app_cloud.py vytvořen
- [x] railway.json konfigurován
- [x] requirements.txt aktualizován
- [x] Environment variables připraveny
- [ ] Railway CLI nainstalován
- [ ] Deploy spuštěn
