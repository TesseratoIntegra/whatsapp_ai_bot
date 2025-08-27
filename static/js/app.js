// WhatsApp Bot - Frontend Application
class KnowledgeManager {
    constructor() {
        this.apiBase = window.location.origin;
        this.currentPage = 1;
        this.pageSize = 12;
        this.currentEditId = null;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadStats();
        this.loadCategories();
        this.loadKnowledge();
    }
    
    // Event Listeners
    setupEventListeners() {
        // Tab navigation
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
        });
        
        // Form submission
        document.getElementById('knowledge-form').addEventListener('submit', (e) => this.handleFormSubmit(e));
        document.getElementById('modal-form').addEventListener('submit', (e) => this.handleModalFormSubmit(e));
        
        // Search
        document.getElementById('search-btn').addEventListener('click', () => this.handleSearch());
        document.getElementById('search-query').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.handleSearch();
        });
        
        // Quick search
        document.getElementById('quick-search').addEventListener('input', (e) => this.handleQuickSearch(e.target.value));
        
        // Category filter
        document.getElementById('category-filter').addEventListener('change', (e) => this.filterByCategory(e.target.value));
        
        // Pagination
        document.getElementById('prev-page').addEventListener('click', () => this.prevPage());
        document.getElementById('next-page').addEventListener('click', () => this.nextPage());
        
        // Modal controls
        document.querySelector('.modal-close').addEventListener('click', () => this.closeModal());
        document.getElementById('modal-cancel').addEventListener('click', () => this.closeModal());
        document.getElementById('modal-save').addEventListener('click', () => this.saveModalForm());
        document.getElementById('modal-delete').addEventListener('click', () => this.deleteKnowledge());
        
        // Import
        document.getElementById('import-rag-btn').addEventListener('click', () => this.importRagFiles());
        
        // Clear form
        document.getElementById('clear-form').addEventListener('click', () => this.clearForm());
        
        // Close modal on outside click
        document.getElementById('knowledge-modal').addEventListener('click', (e) => {
            if (e.target.id === 'knowledge-modal') {
                this.closeModal();
            }
        });
    }
    
    // Tab Management
    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        
        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
        document.getElementById(`${tabName}-tab`).classList.add('active');
        
        // Load data if needed
        if (tabName === 'list') {
            this.loadKnowledge();
        }
    }
    
    // API Calls
    async makeRequest(url, options = {}) {
        this.showLoading();
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            this.showToast(`Erro: ${error.message}`, 'error');
            throw error;
        } finally {
            this.hideLoading();
        }
    }
    
    // Load Statistics
    async loadStats() {
        try {
            const stats = await this.makeRequest('/admin/stats');
            document.getElementById('total-entries').textContent = stats.total_entries;
            document.getElementById('total-categories').textContent = stats.total_categories;
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }
    
    // Load Categories
    async loadCategories() {
        try {
            const response = await this.makeRequest('/admin/categories');
            const categories = response.categories;
            
            // Update category filter
            const categoryFilter = document.getElementById('category-filter');
            const searchCategory = document.getElementById('search-category');
            const categoriesList = document.getElementById('categories-list');
            
            // Clear existing options
            categoryFilter.innerHTML = '<option value="">Todas as Categorias</option>';
            searchCategory.innerHTML = '<option value="">Todas as Categorias</option>';
            categoriesList.innerHTML = '';
            
            categories.forEach(category => {
                if (category) {
                    const option1 = new Option(category, category);
                    const option2 = new Option(category, category);
                    const option3 = document.createElement('option');
                    option3.value = category;
                    
                    categoryFilter.appendChild(option1);
                    searchCategory.appendChild(option2);
                    categoriesList.appendChild(option3);
                }
            });
        } catch (error) {
            console.error('Error loading categories:', error);
        }
    }
    
    // Load Knowledge
    async loadKnowledge(filters = {}) {
        try {
            const params = new URLSearchParams({
                limit: this.pageSize,
                offset: (this.currentPage - 1) * this.pageSize,
                ...filters
            });
            
            const knowledge = await this.makeRequest(`/admin/knowledge?${params}`);
            this.renderKnowledgeGrid(knowledge);
            this.updatePagination(knowledge.length);
        } catch (error) {
            console.error('Error loading knowledge:', error);
        }
    }
    
    // Render Knowledge Grid
    renderKnowledgeGrid(knowledge) {
        const grid = document.getElementById('knowledge-grid');
        
        if (knowledge.length === 0) {
            grid.innerHTML = '<div class="no-results">Nenhum conhecimento encontrado</div>';
            return;
        }
        
        grid.innerHTML = knowledge.map(item => `
            <div class="knowledge-card" onclick="knowledgeManager.openModal(${item.id})">
                <div class="knowledge-card-header">
                    <h3 class="knowledge-title">${item.title}</h3>
                    ${item.category ? `<span class="knowledge-category">${item.category}</span>` : ''}
                </div>
                <div class="knowledge-content">${item.content}</div>
                ${item.tags && item.tags.length > 0 ? `
                    <div class="knowledge-tags">
                        ${item.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                    </div>
                ` : ''}
            </div>
        `).join('');
    }
    
    // Form Handling
    async handleFormSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const data = {
            title: formData.get('title'),
            content: formData.get('content'),
            category: formData.get('category') || null,
            tags: formData.get('tags') ? formData.get('tags').split(',').map(tag => tag.trim()) : [],
            metadata: {}
        };
        
        try {
            await this.makeRequest('/admin/knowledge', {
                method: 'POST',
                body: JSON.stringify(data)
            });
            
            this.showToast('Conhecimento adicionado com sucesso!');
            this.clearForm();
            this.loadStats();
            this.loadCategories();
            
            // Switch to list tab
            this.switchTab('list');
        } catch (error) {
            console.error('Error creating knowledge:', error);
        }
    }
    
    // Clear Form
    clearForm() {
        document.getElementById('knowledge-form').reset();
    }
    
    // Search Handling
    async handleSearch() {
        const query = document.getElementById('search-query').value;
        const searchType = document.getElementById('search-type').value;
        const category = document.getElementById('search-category').value;
        
        if (!query.trim()) {
            this.showToast('Digite um termo para buscar', 'warning');
            return;
        }
        
        try {
            const data = {
                query: query,
                search_type: searchType,
                category: category || null,
                limit: 10
            };
            
            const results = await this.makeRequest('/admin/knowledge/search', {
                method: 'POST',
                body: JSON.stringify(data)
            });
            
            this.renderSearchResults(results);
        } catch (error) {
            console.error('Error searching:', error);
        }
    }
    
    // Render Search Results
    renderSearchResults(results) {
        const container = document.getElementById('search-results');
        
        if (results.length === 0) {
            container.innerHTML = '<div class="no-results">Nenhum resultado encontrado</div>';
            return;
        }
        
        container.innerHTML = `
            <h3>Resultados da Busca (${results.length})</h3>
            <div class="knowledge-grid">
                ${results.map(item => `
                    <div class="knowledge-card" onclick="knowledgeManager.openModal(${item.id})">
                        <div class="knowledge-card-header">
                            <h3 class="knowledge-title">${item.title}</h3>
                            ${item.category ? `<span class="knowledge-category">${item.category}</span>` : ''}
                        </div>
                        <div class="knowledge-content">${item.content}</div>
                        ${item.tags && item.tags.length > 0 ? `
                            <div class="knowledge-tags">
                                ${item.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                            </div>
                        ` : ''}
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    // Quick Search
    handleQuickSearch(query) {
        if (query.length > 2) {
            this.loadKnowledge({ q: query });
        } else if (query.length === 0) {
            this.loadKnowledge();
        }
    }
    
    // Filter by Category
    filterByCategory(category) {
        const filters = category ? { category } : {};
        this.currentPage = 1;
        this.loadKnowledge(filters);
    }
    
    // Pagination
    prevPage() {
        if (this.currentPage > 1) {
            this.currentPage--;
            this.loadKnowledge();
        }
    }
    
    nextPage() {
        this.currentPage++;
        this.loadKnowledge();
    }
    
    updatePagination(resultsCount) {
        document.getElementById('page-info').textContent = `Página ${this.currentPage}`;
        document.getElementById('prev-page').disabled = this.currentPage === 1;
        document.getElementById('next-page').disabled = resultsCount < this.pageSize;
    }
    
    // Modal Management
    async openModal(id) {
        try {
            const knowledge = await this.makeRequest(`/admin/knowledge/${id}`);
            
            this.currentEditId = id;
            document.getElementById('modal-id').value = id;
            document.getElementById('modal-title-input').value = knowledge.title;
            document.getElementById('modal-category').value = knowledge.category || '';
            document.getElementById('modal-tags').value = knowledge.tags ? knowledge.tags.join(', ') : '';
            document.getElementById('modal-content').value = knowledge.content;
            
            document.getElementById('knowledge-modal').style.display = 'block';
        } catch (error) {
            console.error('Error loading knowledge:', error);
        }
    }
    
    closeModal() {
        document.getElementById('knowledge-modal').style.display = 'none';
        this.currentEditId = null;
    }
    
    async handleModalFormSubmit(e) {
        e.preventDefault();
        this.saveModalForm();
    }
    
    async saveModalForm() {
        const id = this.currentEditId;
        const data = {
            title: document.getElementById('modal-title-input').value,
            content: document.getElementById('modal-content').value,
            category: document.getElementById('modal-category').value || null,
            tags: document.getElementById('modal-tags').value ? 
                  document.getElementById('modal-tags').value.split(',').map(tag => tag.trim()) : [],
            metadata: {}
        };
        
        try {
            await this.makeRequest(`/admin/knowledge/${id}`, {
                method: 'PUT',
                body: JSON.stringify(data)
            });
            
            this.showToast('Conhecimento atualizado com sucesso!');
            this.closeModal();
            this.loadKnowledge();
            this.loadStats();
            this.loadCategories();
        } catch (error) {
            console.error('Error updating knowledge:', error);
        }
    }
    
    async deleteKnowledge() {
        if (!confirm('Tem certeza que deseja excluir este conhecimento?')) {
            return;
        }
        
        try {
            await this.makeRequest(`/admin/knowledge/${this.currentEditId}`, {
                method: 'DELETE'
            });
            
            this.showToast('Conhecimento excluído com sucesso!');
            this.closeModal();
            this.loadKnowledge();
            this.loadStats();
            this.loadCategories();
        } catch (error) {
            console.error('Error deleting knowledge:', error);
        }
    }
    
    // Import RAG Files
    async importRagFiles() {
        if (!confirm('Deseja importar os arquivos RAG existentes? Isso pode levar alguns minutos.')) {
            return;
        }
        
        try {
            const result = await this.makeRequest('/admin/knowledge/bulk-import', {
                method: 'POST'
            });
            
            document.getElementById('import-results').innerHTML = `
                <div class="import-success">
                    <i class="fas fa-check-circle"></i>
                    <h3>Importação Concluída!</h3>
                    <p>${result.message}</p>
                    <p><strong>Documentos importados:</strong> ${result.count}</p>
                </div>
            `;
            
            this.showToast(`${result.count} documentos importados com sucesso!`);
            this.loadStats();
            this.loadCategories();
        } catch (error) {
            console.error('Error importing files:', error);
            document.getElementById('import-results').innerHTML = `
                <div class="import-error">
                    <i class="fas fa-exclamation-circle"></i>
                    <h3>Erro na Importação</h3>
                    <p>Ocorreu um erro ao importar os arquivos. Verifique se o banco de dados está configurado corretamente.</p>
                </div>
            `;
        }
    }
    
    // UI Helpers
    showLoading() {
        document.getElementById('loading').style.display = 'block';
    }
    
    hideLoading() {
        document.getElementById('loading').style.display = 'none';
    }
    
    showToast(message, type = 'success') {
        const toast = document.getElementById('toast');
        const toastMessage = document.getElementById('toast-message');
        
        toastMessage.textContent = message;
        toast.className = `toast ${type}`;
        toast.classList.add('show');
        
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
}

// Initialize the application
let knowledgeManager;

document.addEventListener('DOMContentLoaded', () => {
    knowledgeManager = new KnowledgeManager();
});

// Additional CSS for no results and import results
const additionalCSS = `
.no-results {
    text-align: center;
    padding: 60px 20px;
    color: #6c757d;
    font-size: 1.2em;
}

.import-success,
.import-error {
    text-align: center;
    padding: 40px;
    border-radius: 10px;
    margin-top: 20px;
}

.import-success {
    background: rgba(37, 211, 102, 0.1);
    border: 1px solid #25D366;
    color: #155724;
}

.import-success i {
    font-size: 3em;
    color: #25D366;
    margin-bottom: 20px;
}

.import-error {
    background: rgba(220, 53, 69, 0.1);
    border: 1px solid #dc3545;
    color: #721c24;
}

.import-error i {
    font-size: 3em;
    color: #dc3545;
    margin-bottom: 20px;
}

.search-results h3 {
    margin-bottom: 20px;
    color: #343a40;
}
`;

// Add additional CSS to the page
const style = document.createElement('style');
style.textContent = additionalCSS;
document.head.appendChild(style);