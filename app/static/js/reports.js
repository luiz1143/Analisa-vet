/**
 * Módulo de geração de laudos para o aplicativo AnalisaVet
 */

const Reports = {
    // Inicializa o módulo de laudos
    init: function() {
        // Adiciona listeners para os botões de geração de laudos
        const btnLaudoTecnico = document.getElementById('btn-laudo-tecnico');
        const btnLaudoSimplificado = document.getElementById('btn-laudo-simplificado');
        
        if (btnLaudoTecnico) {
            btnLaudoTecnico.addEventListener('click', () => this.generateReport('technical'));
        }
        
        if (btnLaudoSimplificado) {
            btnLaudoSimplificado.addEventListener('click', () => this.generateReport('simplified'));
        }
    },
    
    // Gera um laudo (técnico ou simplificado)
    generateReport: async function(type) {
        // Verifica se o usuário está logado
        if (!Auth.isLoggedIn()) {
            alert('Você precisa estar logado para gerar laudos.');
            return;
        }
        
        // Verifica se há uma análise para gerar o laudo
        const analysisId = Analysis.getLastAnalysisId();
        if (!analysisId) {
            alert('Nenhuma análise disponível. Por favor, realize uma análise primeiro.');
            return;
        }
        
        // Define a URL com base no tipo de laudo
        const url = type === 'technical' 
            ? `/api/reports/technical/${analysisId}` 
            : `/api/reports/simplified/${analysisId}`;
        
        try {
            // Exibe mensagem de carregamento
            const reportType = type === 'technical' ? 'técnico' : 'simplificado';
            alert(`Gerando laudo ${reportType}. O download começará em instantes.`);
            
            // Faz a requisição para gerar o laudo
            const blob = await Utils.fetchAPI(url);
            
            // Define o nome do arquivo
            const filename = type === 'technical' 
                ? `laudo_tecnico_${analysisId}.pdf` 
                : `laudo_simplificado_${analysisId}.pdf`;
            
            // Faz o download do arquivo
            Utils.downloadFile(blob, filename);
        } catch (error) {
            console.error(`Erro ao gerar laudo ${type}:`, error);
            alert(`Erro ao gerar laudo. Por favor, tente novamente.`);
        }
    }
};
