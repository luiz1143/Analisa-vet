/**
 * Módulo de upload e extração de arquivos para o aplicativo AnalisaVet
 */

const Upload = {
    // Inicializa o módulo de upload
    init: function() {
        // Adiciona listener para o botão de upload
        const btnUpload = document.getElementById('btn-upload');
        if (btnUpload) {
            btnUpload.addEventListener('click', this.uploadFile.bind(this));
        }
        
        // Adiciona listener para o input de arquivo
        const fileInput = document.getElementById('hemograma-file');
        if (fileInput) {
            fileInput.addEventListener('change', this.handleFileSelect.bind(this));
        }
    },
    
    // Manipula a seleção de arquivo
    handleFileSelect: function(event) {
        const fileInput = event.target;
        const statusElement = document.getElementById('upload-status');
        
        // Limpa mensagem de status anterior
        Utils.clearStatusMessage('upload-status');
        
        // Verifica se um arquivo foi selecionado
        if (fileInput.files.length === 0) {
            return;
        }
        
        const file = fileInput.files[0];
        
        // Verifica o tipo de arquivo
        const fileType = file.name.split('.').pop().toLowerCase();
        if (fileType !== 'pdf' && fileType !== 'csv') {
            Utils.showStatusMessage('upload-status', 'Formato de arquivo não suportado. Por favor, selecione um arquivo PDF ou CSV.', 'error');
            fileInput.value = '';
            return;
        }
        
        // Exibe o nome do arquivo selecionado
        Utils.showStatusMessage('upload-status', `Arquivo selecionado: ${file.name}`, 'info');
    },
    
    // Faz upload do arquivo e extrai os dados
    uploadFile: async function() {
        // Verifica se o usuário está logado
        if (!Auth.isLoggedIn()) {
            alert('Você precisa estar logado para fazer upload de arquivos.');
            return;
        }
        
        const fileInput = document.getElementById('hemograma-file');
        const statusElement = document.getElementById('upload-status');
        
        // Verifica se um arquivo foi selecionado
        if (!fileInput || fileInput.files.length === 0) {
            Utils.showStatusMessage('upload-status', 'Por favor, selecione um arquivo para upload.', 'error');
            return;
        }
        
        const file = fileInput.files[0];
        
        // Cria um objeto FormData para enviar o arquivo
        const formData = new FormData();
        formData.append('file', file);
        
        // Exibe mensagem de carregamento
        Utils.showStatusMessage('upload-status', 'Enviando arquivo e extraindo dados...', 'info');
        
        try {
            const response = await Utils.fetchAPI('/api/analysis/upload', {
                method: 'POST',
                body: formData
            });
            
            if (response.success) {
                // Exibe mensagem de sucesso
                Utils.showStatusMessage('upload-status', 'Arquivo processado com sucesso! Dados extraídos preenchidos automaticamente.', 'success');
                
                // Preenche os campos do formulário com os dados extraídos
                this.fillFormWithExtractedData(response.data);
            }
        } catch (error) {
            console.error('Erro ao fazer upload do arquivo:', error);
            Utils.showStatusMessage('upload-status', error.message || 'Erro ao processar o arquivo. Por favor, tente novamente.', 'error');
        }
    },
    
    // Preenche o formulário com os dados extraídos
    fillFormWithExtractedData: function(data) {
        // Preenche os dados do hemograma
        if (data.hemograma) {
            for (const [param, value] of Object.entries(data.hemograma)) {
                const element = document.getElementById(param);
                if (element && value !== null) {
                    element.value = value;
                }
            }
        }
        
        // Preenche os dados do paciente
        if (data.paciente) {
            // Mapeia os campos do paciente para os IDs dos elementos
            const patientFieldMap = {
                'nome': 'nome-paciente',
                'tutor': 'nome-tutor',
                'raca': 'raca',
                'idade': 'idade',
                'sexo': 'sexo',
                'especie': 'especie'
            };
            
            for (const [field, value] of Object.entries(data.paciente)) {
                const elementId = patientFieldMap[field];
                if (elementId && value) {
                    const element = document.getElementById(elementId);
                    if (element) {
                        element.value = value;
                    }
                }
            }
            
            // Se a espécie foi extraída, seleciona a espécie correspondente
            if (data.paciente.especie) {
                const especie = data.paciente.especie.trim();
                if (especie.toLowerCase() === 'cão' || especie.toLowerCase() === 'cao' || especie.toLowerCase() === 'canino') {
                    Analysis.selectSpecies('Cão');
                } else if (especie.toLowerCase() === 'gato' || especie.toLowerCase() === 'felino') {
                    Analysis.selectSpecies('Gato');
                }
            }
        }
    }
};
