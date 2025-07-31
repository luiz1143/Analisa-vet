/**
 * Correção para o problema de exibição dos valores de referência
 * Este script substitui a função loadReferenceValues original para garantir
 * que os valores de referência sejam carregados e exibidos corretamente
 */

// Sobrescrever a função de carregamento de valores de referência
Analysis.loadReferenceValues = async function() {
    console.log('Carregando valores de referência para:', this.selectedSpecies);
    
    try {
        // URL da API de valores de referência
        const url = `/api/analysis/reference-values?especie=${encodeURIComponent(this.selectedSpecies)}`;
        console.log('Fazendo requisição para:', url);
        
        // Fazer a requisição diretamente com fetch para garantir que funcione
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            },
            credentials: 'include'
        });
        
        // Verificar se a resposta foi bem-sucedida
        if (!response.ok) {
            throw new Error(`Erro na requisição: ${response.status} ${response.statusText}`);
        }
        
        // Converter a resposta para JSON
        const data = await response.json();
        console.log('Resposta da API:', data);
        
        if (data.success) {
            // Armazenar os valores de referência
            this.referenceValues = data.data;
            console.log('Valores de referência armazenados:', this.referenceValues);
            
            // Atualizar a exibição dos valores de referência
            this.updateReferenceValues();
        } else {
            console.error('Erro na resposta da API:', data.error || 'Erro desconhecido');
        }
    } catch (error) {
        console.error('Erro ao carregar valores de referência:', error);
    }
};

// Sobrescrever a função de atualização dos valores de referência
Analysis.updateReferenceValues = function() {
    console.log('Atualizando valores de referência no DOM');
    
    // Verificar se temos valores de referência
    if (!this.referenceValues || Object.keys(this.referenceValues).length === 0) {
        console.warn('Nenhum valor de referência disponível para atualizar');
        return;
    }
    
    // Iterar sobre os valores de referência
    for (const [param, value] of Object.entries(this.referenceValues)) {
        // Obter o elemento de referência
        const refElement = document.getElementById(`ref-${param}`);
        
        if (refElement) {
            // Atualizar o texto do elemento
            const texto = `Referência (${this.selectedSpecies}): ${value}`;
            refElement.textContent = texto;
            refElement.style.display = 'block'; // Garantir que esteja visível
            console.log(`Elemento ref-${param} atualizado com: "${texto}"`);
        } else {
            console.warn(`Elemento ref-${param} não encontrado no DOM`);
        }
    }
    
    console.log('Atualização de valores de referência concluída');
};

// Forçar o carregamento inicial dos valores de referência após um pequeno delay
// para garantir que todos os elementos do DOM estejam prontos
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM carregado, aguardando para carregar valores de referência');
    
    setTimeout(() => {
        console.log('Forçando carregamento inicial dos valores de referência');
        Analysis.loadReferenceValues();
    }, 500);
});
