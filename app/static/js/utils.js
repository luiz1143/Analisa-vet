/**
 * Utilitários para o aplicativo AnalisaVet
 */

// Funções utilitárias para manipulação de DOM, requisições AJAX, etc.
const Utils = {
    // Exibe uma mensagem de status
    showStatusMessage: function(elementId, message, type) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        element.textContent = message;
        element.className = 'status-message';
        
        if (type) {
            element.classList.add(type);
        }
        
        element.style.display = 'block';
    },
    
    // Limpa uma mensagem de status
    clearStatusMessage: function(elementId) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        element.textContent = '';
        element.className = 'status-message';
        element.style.display = 'none';
    },
    
    // Faz uma requisição AJAX
    fetchAPI: async function(url, options = {}) {
        try {
            // Configurações padrão
            const defaultOptions = {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                credentials: 'include' // Inclui cookies nas requisições
            };
            
            // Mescla as opções padrão com as opções fornecidas
            const fetchOptions = { ...defaultOptions, ...options };
            
            // Se o método for POST, PUT, etc. e o corpo for um objeto, converte para JSON
            if (fetchOptions.body && typeof fetchOptions.body === 'object' && !(fetchOptions.body instanceof FormData)) {
                fetchOptions.body = JSON.stringify(fetchOptions.body);
            }
            
            // Se o corpo for FormData, remove o cabeçalho Content-Type para que o navegador defina automaticamente
            if (fetchOptions.body instanceof FormData) {
                delete fetchOptions.headers['Content-Type'];
            }
            
            // Faz a requisição
            const response = await fetch(url, fetchOptions);
            
            // Se a resposta for um PDF ou outro arquivo binário
            if (url.includes('/reports/') && response.ok) {
                return response.blob();
            }
            
            // Para outras respostas, tenta converter para JSON
            const data = await response.json();
            
            // Verifica se a resposta foi bem-sucedida
            if (!response.ok) {
                throw new Error(data.error || 'Erro na requisição');
            }
            
            return data;
        } catch (error) {
            console.error('Erro na requisição:', error);
            throw error;
        }
    },
    
    // Formata um valor para exibição
    formatValue: function(value, decimals = 2) {
        if (value === null || value === undefined) return '-';
        
        if (typeof value === 'number') {
            return value.toLocaleString('pt-BR', {
                minimumFractionDigits: decimals,
                maximumFractionDigits: decimals
            });
        }
        
        return value;
    },
    
    // Exibe ou oculta um elemento
    toggleElement: function(elementId, show) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        element.style.display = show ? 'block' : 'none';
    },
    
    // Preenche um formulário com dados
    fillForm: function(formData) {
        for (const [key, value] of Object.entries(formData)) {
            const element = document.getElementById(key);
            if (element && value !== null && value !== undefined) {
                element.value = value;
            }
        }
    },
    
    // Coleta dados de um formulário
    collectFormData: function(inputIds) {
        const data = {};
        
        for (const id of inputIds) {
            const element = document.getElementById(id);
            if (element) {
                // Para campos numéricos, converte para número
                if (element.type === 'number') {
                    data[id] = element.value ? parseFloat(element.value) : null;
                } else {
                    data[id] = element.value || null;
                }
            }
        }
        
        return data;
    },
    
    // Baixa um arquivo
    downloadFile: function(blob, filename) {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }
};
