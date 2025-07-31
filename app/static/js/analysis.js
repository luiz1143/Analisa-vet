/**
 * Módulo de análise de hemograma para o aplicativo AnalisaVet
 */

const Analysis = {
    // Espécie selecionada (padrão: Cão)
    selectedSpecies: 'Cão',
    
    // Valores de referência para a espécie selecionada
    referenceValues: {},
    
    // Resultado da última análise
    lastAnalysisResult: null,
    
    // Inicializa o módulo de análise
    init: function() {
        // Adiciona listeners para os botões de espécie
        const btnCao = document.getElementById('btn-cao');
        const btnGato = document.getElementById('btn-gato');
        
        if (btnCao) {
            btnCao.addEventListener('click', () => this.selectSpecies('Cão'));
        }
        
        if (btnGato) {
            btnGato.addEventListener('click', () => this.selectSpecies('Gato'));
        }
        
        // Adiciona listener para o botão de análise
        const btnAnalisar = document.getElementById('btn-analisar');
        if (btnAnalisar) {
            btnAnalisar.addEventListener('click', this.analyzeHemogram.bind(this));
        }
        
        // Adiciona listener para o botão de limpar
        const btnLimpar = document.getElementById('btn-limpar');
        if (btnLimpar) {
            btnLimpar.addEventListener('click', this.clearForm.bind(this));
        }
        
        // Carrega os valores de referência para a espécie padrão
        this.loadReferenceValues();
    },
    
    // Seleciona uma espécie e atualiza a interface
    selectSpecies: function(species) {
        this.selectedSpecies = species;
        
        // Atualiza os botões de espécie
        const btnCao = document.getElementById('btn-cao');
        const btnGato = document.getElementById('btn-gato');
        
        if (btnCao) {
            btnCao.classList.toggle('active', species === 'Cão');
        }
        
        if (btnGato) {
            btnGato.classList.toggle('active', species === 'Gato');
        }
        
        // Carrega os valores de referência para a espécie selecionada
        this.loadReferenceValues();
    },
    
    // Carrega os valores de referência para a espécie selecionada
    loadReferenceValues: async function() {
        try {
            const response = await Utils.fetchAPI(`/api/analysis/reference-values?especie=${this.selectedSpecies}`);
            
            if (response.success) {
                this.referenceValues = response.data;
                this.updateReferenceValues();
            }
        } catch (error) {
            console.error('Erro ao carregar valores de referência:', error);
        }
    },
    
    // Atualiza a exibição dos valores de referência
    updateReferenceValues: function() {
        for (const [param, value] of Object.entries(this.referenceValues)) {
            const refElement = document.getElementById(`ref-${param}`);
            if (refElement) {
                refElement.textContent = `Referência (${this.selectedSpecies}): ${value}`;
            }
        }
    },
    
    // Analisa o hemograma com os dados do formulário
    analyzeHemogram: async function() {
        // Verifica se o usuário está logado
        if (!Auth.isLoggedIn()) {
            alert('Você precisa estar logado para analisar hemogramas.');
            return;
        }
        
        // Coleta os dados do formulário
        const hemogramData = this.collectHemogramData();
        
        // Adiciona a espécie selecionada
        hemogramData.especie = this.selectedSpecies;
        
        // Exibe a seção de resultados com o indicador de carregamento
        Utils.toggleElement('resultado-section', true);
        Utils.toggleElement('loading-results', true);
        Utils.toggleElement('results-content', false);
        Utils.toggleElement('error-message', false);
        
        try {
            const response = await Utils.fetchAPI('/api/analysis/analyze', {
                method: 'POST',
                body: hemogramData
            });
            
            if (response.success) {
                // Armazena o resultado da análise
                this.lastAnalysisResult = response.data;
                
                // Atualiza os créditos do usuário
                Auth.updateCredits(response.data.credits_remaining);
                
                // Exibe os resultados
                this.displayResults(response.data.diagnostico);
                
                // Oculta o indicador de carregamento e exibe os resultados
                Utils.toggleElement('loading-results', false);
                Utils.toggleElement('results-content', true);
            }
        } catch (error) {
            console.error('Erro ao analisar hemograma:', error);
            
            // Exibe mensagem de erro
            const errorElement = document.getElementById('error-message');
            if (errorElement) {
                errorElement.textContent = error.message || 'Erro ao analisar hemograma. Por favor, tente novamente.';
                Utils.toggleElement('error-message', true);
            }
            
            // Oculta o indicador de carregamento
            Utils.toggleElement('loading-results', false);
        }
    },
    
    // Coleta os dados do hemograma do formulário
    collectHemogramData: function() {
        // Lista de IDs dos campos do hemograma
        const hemogramFields = [
            'hemacias', 'hemoglobina', 'hematocrito', 'reticulocitos',
            'vcm', 'hcm', 'chcm',
            'leucocitos', 'segmentados', 'linfocitos', 'monocitos', 'eosinofilos', 'basofilos',
            'plaquetas', 'proteina'
        ];
        
        // Lista de IDs dos campos do paciente
        const patientFields = [
            'nome_paciente', 'nome_tutor', 'raca', 'idade', 'sexo', 'finalidade_exame'
        ];
        
        // Coleta os dados do hemograma
        const hemogramData = Utils.collectFormData(hemogramFields);
        
        // Coleta os dados do paciente
        const patientData = Utils.collectFormData(patientFields);
        
        // Combina os dados
        return { ...hemogramData, ...patientData };
    },
    
    // Exibe os resultados da análise
    displayResults: function(results) {
        console.log('Exibindo resultados:', results); // Debug
        
        // Exibe o diagnóstico
        const diagnosticoElement = document.getElementById('diagnostico');
        if (diagnosticoElement) {
            // Limpa o conteúdo anterior
            diagnosticoElement.innerHTML = '';
            
            // Verifica se há diagnósticos
            if (results.diagnosticos && results.diagnosticos.length > 0) {
                // Cria uma lista para os diagnósticos
                const ul = document.createElement('ul');
                
                // Adiciona cada diagnóstico como um item da lista
                results.diagnosticos.forEach(diagnostico => {
                    const li = document.createElement('li');
                    li.textContent = diagnostico;
                    ul.appendChild(li);
                });
                
                diagnosticoElement.appendChild(ul);
            } else {
                // Caso não haja diagnósticos ou a estrutura seja antiga
                diagnosticoElement.textContent = results.diagnostico || 'Sem diagnóstico disponível';
            }
        }
        
        // Exibe a explicação
        const explicacaoElement = document.getElementById('explicacao');
        if (explicacaoElement) {
            // Limpa o conteúdo anterior
            explicacaoElement.innerHTML = '';
            
            // Verifica se há explicações no novo formato
            if (results.explicacoes && Array.isArray(results.explicacoes) && results.explicacoes.length > 0) {
                // Para cada explicação, cria um parágrafo
                results.explicacoes.forEach(explicacao => {
                    const p = document.createElement('p');
                    // Prioriza interpretacao, depois para_tutor, depois qualquer string
                    const texto = explicacao.interpretacao || explicacao.para_tutor || explicacao;
                    p.textContent = texto;
                    explicacaoElement.appendChild(p);
                });
            } 
            // Verifica se há explicação no formato antigo
            else if (results.explicacao && results.explicacao.interpretacao) {
                explicacaoElement.textContent = results.explicacao.interpretacao;
            }
            // Verifica se explicacoes é um objeto único
            else if (results.explicacoes && typeof results.explicacoes === 'object' && !Array.isArray(results.explicacoes)) {
                const p = document.createElement('p');
                const texto = results.explicacoes.interpretacao || results.explicacoes.para_tutor || 'Sem explicação disponível';
                p.textContent = texto;
                explicacaoElement.appendChild(p);
            }
            else {
                explicacaoElement.textContent = 'Sem explicação disponível';
            }
        }
        
        // Exibe as recomendações
        const recomendacoesElement = document.getElementById('recomendacoes');
        if (recomendacoesElement) {
            // Limpa o conteúdo anterior
            recomendacoesElement.innerHTML = '';
            
            // Verifica se há explicações no novo formato
            if (results.explicacoes && Array.isArray(results.explicacoes) && results.explicacoes.length > 0) {
                // Para cada explicação, cria um parágrafo com a recomendação
                results.explicacoes.forEach(explicacao => {
                    if (explicacao.recomendacao) {
                        const p = document.createElement('p');
                        p.textContent = explicacao.recomendacao;
                        recomendacoesElement.appendChild(p);
                    }
                });
            } 
            // Verifica se há explicação no formato antigo
            else if (results.explicacao && results.explicacao.recomendacao) {
                recomendacoesElement.textContent = results.explicacao.recomendacao;
            }
            // Verifica se explicacoes é um objeto único
            else if (results.explicacoes && typeof results.explicacoes === 'object' && !Array.isArray(results.explicacoes) && results.explicacoes.recomendacao) {
                recomendacoesElement.textContent = results.explicacoes.recomendacao;
            }
            else {
                recomendacoesElement.textContent = 'Sem recomendações disponíveis';
            }
        }
        
        // Exibe as alterações
        const alteracoesElement = document.getElementById('alteracoes');
        if (alteracoesElement) {
            // Limpa o conteúdo anterior
            alteracoesElement.innerHTML = '';
            
            // Adiciona cada alteração
            if (results.alteracoes && results.alteracoes.length > 0) {
                results.alteracoes.forEach(alteracao => {
                    const li = document.createElement('li');
                    
                    const paramSpan = document.createElement('span');
                    paramSpan.className = 'parametro';
                    paramSpan.textContent = this.getParameterName(alteracao.parametro) + ':';
                    
                    const valorSpan = document.createElement('span');
                    valorSpan.className = 'valor ' + alteracao.classificacao;
                    valorSpan.textContent = Utils.formatValue(alteracao.valor);
                    
                    const classSpan = document.createElement('span');
                    classSpan.className = 'classificacao';
                    classSpan.textContent = `(${alteracao.classificacao.toUpperCase()})`;
                    
                    const refSpan = document.createElement('span');
                    refSpan.className = 'reference';
                    refSpan.textContent = `Referência: ${alteracao.referencia}`;
                    
                    li.appendChild(paramSpan);
                    li.appendChild(document.createTextNode(' '));
                    li.appendChild(valorSpan);
                    li.appendChild(document.createTextNode(' '));
                    li.appendChild(classSpan);
                    li.appendChild(document.createElement('br'));
                    li.appendChild(refSpan);
                    
                    alteracoesElement.appendChild(li);
                });
            } else {
                const li = document.createElement('li');
                li.textContent = 'Sem alterações significativas';
                alteracoesElement.appendChild(li);
            }
        }
    },
    
    // Limpa o formulário
    clearForm: function() {
        // Lista de IDs dos campos do hemograma
        const hemogramFields = [
            'hemacias', 'hemoglobina', 'hematocrito', 'reticulocitos',
            'vcm', 'hcm', 'chcm',
            'leucocitos', 'segmentados', 'linfocitos', 'monocitos', 'eosinofilos', 'basofilos',
            'plaquetas', 'proteina'
        ];
        
        // Lista de IDs dos campos do paciente
        const patientFields = [
            'nome_paciente', 'nome_tutor', 'raca', 'idade', 'sexo', 'finalidade_exame'
        ];
        
        // Limpa os campos
        [...hemogramFields, ...patientFields].forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.value = '';
            }
        });
        
        // Oculta a seção de resultados
        Utils.toggleElement('resultado-section', false);
    },
    
    // Obtém o nome amigável de um parâmetro
    getParameterName: function(param) {
        const paramNames = {
            'hemacias': 'Hemácias',
            'hemoglobina': 'Hemoglobina',
            'hematocrito': 'Hematócrito',
            'reticulocitos': 'Reticulócitos',
            'vcm': 'VCM',
            'hcm': 'HCM',
            'chcm': 'CHCM',
            'leucocitos': 'Leucócitos',
            'segmentados': 'Segmentados',
            'linfocitos': 'Linfócitos',
            'monocitos': 'Monócitos',
            'eosinofilos': 'Eosinófilos',
            'basofilos': 'Basófilos',
            'plaquetas': 'Plaquetas',
            'proteina': 'Proteína Total'
        };
        
        return paramNames[param] || param;
    },
    
    // Obtém o ID da última análise
    getLastAnalysisId: function() {
        return this.lastAnalysisResult ? this.lastAnalysisResult.analysis_id : null;
    }
};
