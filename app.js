/**
 * Transformative Conflict Resolution RAG App - Frontend JavaScript
 * Handles user interactions, API calls, and UI updates
 */

class ConflictResolutionApp {
    constructor() {
        this.isLoading = false;
        this.currentQuery = '';
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadInitialData();
    }

    bindEvents() {
        // Search functionality
        const searchBtn = document.getElementById('searchBtn');
        const queryInput = document.getElementById('queryInput');
        const exampleBtns = document.querySelectorAll('.example-btn');
        const newQueryBtn = document.getElementById('newQueryBtn');
        const retryBtn = document.getElementById('retryBtn');

        // Search button click
        searchBtn.addEventListener('click', () => this.handleSearch());

        // Enter key in search input
        queryInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !this.isLoading) {
                this.handleSearch();
            }
        });

        // Example query buttons
        exampleBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const query = e.target.getAttribute('data-query');
                queryInput.value = query;
                this.handleSearch();
            });
        });

        // New query button
        newQueryBtn.addEventListener('click', () => this.resetSearch());

        // Retry button
        retryBtn.addEventListener('click', () => this.handleSearch());

        // Sidebar actions
        const refreshStatsBtn = document.getElementById('refreshStatsBtn');
        const reindexBtn = document.getElementById('reindexBtn');

        refreshStatsBtn.addEventListener('click', () => this.loadDatabaseStats());
        reindexBtn.addEventListener('click', () => this.handleReindex());
    }

    async loadInitialData() {
        await this.loadDatabaseStats();
        await this.loadDocuments();
    }

    async handleSearch() {
        const queryInput = document.getElementById('queryInput');
        const query = queryInput.value.trim();

        if (!query) {
            this.showError('Zadejte prosím dotaz');
            return;
        }

        this.currentQuery = query;
        this.showLoading();
        this.hideError();
        this.hideResults();

        try {
            const response = await this.searchQuery(query);
            this.displayResults(response);
        } catch (error) {
            console.error('Search error:', error);
            this.showError('Chyba při vyhledávání: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }

    async searchQuery(query) {
        const response = await fetch('/api/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Chyba serveru');
        }

        return await response.json();
    }

    displayResults(data) {
        const resultsSection = document.getElementById('resultsSection');
        const responseContent = document.getElementById('responseContent');
        const citationsContent = document.getElementById('citationsContent');
        const sourcesCount = document.getElementById('sourcesCount');

        // Display response
        responseContent.innerHTML = this.formatResponse(data.response);

        // Display citations
        if (data.citations) {
            citationsContent.innerHTML = data.citations;
        } else {
            citationsContent.innerHTML = '';
        }

        // Update sources count
        sourcesCount.textContent = `${data.num_sources || 0} zdrojů`;

        // Show results
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    formatResponse(text) {
        // Basic text formatting
        return text
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>')
            .replace(/^/, '<p>')
            .replace(/$/, '</p>');
    }

    resetSearch() {
        const queryInput = document.getElementById('queryInput');
        queryInput.value = '';
        queryInput.focus();
        
        this.hideResults();
        this.hideError();
        this.currentQuery = '';
    }

    async loadDatabaseStats() {
        try {
            const response = await fetch('/api/stats');
            const data = await response.json();

            if (response.ok) {
                this.updateDatabaseStats(data);
            } else {
                console.error('Error loading stats:', data.error);
            }
        } catch (error) {
            console.error('Error loading database stats:', error);
        }
    }

    updateDatabaseStats(stats) {
        const documentCount = document.getElementById('documentCount');
        const databaseStatus = document.getElementById('databaseStatus');

        if (stats.total_documents !== undefined) {
            documentCount.textContent = stats.total_documents;
        }

        if (stats.total_documents > 0) {
            databaseStatus.textContent = 'Připravena';
            databaseStatus.style.color = '#27ae60';
        } else {
            databaseStatus.textContent = 'Prázdná';
            databaseStatus.style.color = '#e74c3c';
        }
    }

    async loadDocuments() {
        try {
            const response = await fetch('/api/documents');
            const data = await response.json();

            if (response.ok) {
                this.updateDocumentsList(data.documents);
            } else {
                console.error('Error loading documents:', data.error);
            }
        } catch (error) {
            console.error('Error loading documents:', error);
        }
    }

    updateDocumentsList(documents) {
        const documentsList = document.getElementById('documentsList');
        
        if (!documents || documents.length === 0) {
            documentsList.innerHTML = '<p class="loading-text">Žádné dokumenty nenalezeny</p>';
            return;
        }

        const documentsHTML = documents.map(doc => `
            <div class="document-item">
                <div class="document-title">${this.truncateText(doc.title, 40)}</div>
                <div class="document-author">${doc.author}</div>
            </div>
        `).join('');

        documentsList.innerHTML = documentsHTML;
    }

    async handleReindex() {
        if (!confirm('Opravdu chcete reindexovat databázi? Tato operace může trvat několik minut.')) {
            return;
        }

        const reindexBtn = document.getElementById('reindexBtn');
        const originalText = reindexBtn.innerHTML;
        
        reindexBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Reindexuji...';
        reindexBtn.disabled = true;

        try {
            const response = await fetch('/api/reindex', {
                method: 'POST'
            });
            const data = await response.json();

            if (response.ok && data.success) {
                alert('Databáze byla úspěšně reindexována');
                await this.loadDatabaseStats();
            } else {
                alert('Chyba při reindexaci: ' + (data.error || 'Neznámá chyba'));
            }
        } catch (error) {
            console.error('Reindex error:', error);
            alert('Chyba při reindexaci: ' + error.message);
        } finally {
            reindexBtn.innerHTML = originalText;
            reindexBtn.disabled = false;
        }
    }

    showLoading() {
        this.isLoading = true;
        const loadingIndicator = document.getElementById('loadingIndicator');
        const searchBtn = document.getElementById('searchBtn');
        
        loadingIndicator.style.display = 'block';
        searchBtn.disabled = true;
        searchBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>Hledám...</span>';
    }

    hideLoading() {
        this.isLoading = false;
        const loadingIndicator = document.getElementById('loadingIndicator');
        const searchBtn = document.getElementById('searchBtn');
        
        loadingIndicator.style.display = 'none';
        searchBtn.disabled = false;
        searchBtn.innerHTML = '<i class="fas fa-search"></i> <span>Hledat</span>';
    }

    showError(message) {
        const errorSection = document.getElementById('errorSection');
        const errorMessage = document.getElementById('errorMessage');
        
        errorMessage.textContent = message;
        errorSection.style.display = 'block';
        errorSection.scrollIntoView({ behavior: 'smooth' });
    }

    hideError() {
        const errorSection = document.getElementById('errorSection');
        errorSection.style.display = 'none';
    }

    hideResults() {
        const resultsSection = document.getElementById('resultsSection');
        resultsSection.style.display = 'none';
    }

    truncateText(text, maxLength) {
        if (text.length <= maxLength) {
            return text;
        }
        return text.substring(0, maxLength) + '...';
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ConflictResolutionApp();
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
        // Page became visible, refresh stats
        const app = window.conflictResolutionApp;
        if (app) {
            app.loadDatabaseStats();
        }
    }
});
