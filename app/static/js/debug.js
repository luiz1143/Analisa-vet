/**
 * Script de depuração para identificar problemas na exibição dos valores de referência
 */

console.log('Script de depuração carregado');

// Adicionar logs detalhados à função de carregamento de valores de referência
const originalLoadReferenceValues = Analysis.loadReferenceValues;
Analysis.loadReferenceValues = async function() {
    console.log('Iniciando carregamento de valores de referência para:', this.selectedSpecies);
    
    try {
        const url = `/api/analysis/reference-values?especie=${this.selectedSpecies}`;
        console.log('Fazendo requisição para:', url);
        
        const response = await Utils.fetchAPI(url);
        console.log('Resposta recebida:', response);
        
        if (response.success) {
            console.log('Valores de referência obtidos com sucesso:', response.data);
            this.referenceValues = response.data;
            
            console.log('Chamando updateReferenceValues()');
            this.updateReferenceValues();
        } else {
            console.error('Erro na resposta da API:', response);
        }
    } catch (error) {
        console.error('Erro ao carregar valores de referência:', error);
    }
};

// Adicionar logs detalhados à função de atualização dos valores de referência
const originalUpdateReferenceValues = Analysis.updateReferenceValues;
Analysis.updateReferenceValues = function() {
    console.log('Atualizando valores de referência no DOM');
    console.log('Valores disponíveis:', this.referenceValues);
    
    for (const [param, value] of Object.entries(this.referenceValues)) {
        const refElement = document.getElementById(`ref-${param}`);
        console.log(`Procurando elemento ref-${param}:`, refElement ? 'Encontrado' : 'Não encontrado');
        
        if (refElement) {
            const texto = `Referência (${this.selectedSpecies}): ${value}`;
            console.log(`Definindo texto para ref-${param}:`, texto);
            refElement.textContent = texto;
        }
    }
    
    console.log('Atualização de valores de referência concluída');
};

// Verificar se o módulo Analysis foi inicializado corretamente
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM carregado, verificando inicialização do Analysis');
    
    // Verificar se o init foi chamado
    setTimeout(() => {
        console.log('Estado atual do Analysis:', {
            selectedSpecies: Analysis.selectedSpecies,
            referenceValues: Analysis.referenceValues
        });
        
        // Forçar carregamento dos valores de referência
        console.log('Forçando carregamento dos valores de referência');
        Analysis.loadReferenceValues();
    }, 1000);
});
