/**
 * Arquivo principal de inicialização do aplicativo AnalisaVet
 */

// Espera o DOM ser carregado completamente
document.addEventListener("DOMContentLoaded", function() {
    // Inicializa todos os módulos
    initializeApp();
});

// Função principal de inicialização
function initializeApp() {
    console.log("Inicializando aplicativo AnalisaVet...");
    
    // Inicializa o módulo de autenticação
    Auth.init();
    
    // Inicializa o módulo de análise
    Analysis.init();
    
    // Inicializa o módulo de upload
    Upload.init();
    
    // Inicializa o módulo de laudos
    Reports.init();
    
    // Inicializa o módulo de configurações da clínica
    ClinicConfig.init();

    // Adiciona listener para o botão da clínica
    const btnClinicConfig = document.getElementById("btn-clinic-config");
    if (btnClinicConfig) {
        btnClinicConfig.addEventListener("click", ClinicConfig.toggleClinicConfig.bind(ClinicConfig));
    }
    
    // Configura listeners adicionais
    setupAdditionalListeners();
    
    console.log("Aplicativo AnalisaVet inicializado com sucesso!");
}

// Configura listeners adicionais
function setupAdditionalListeners() {
    // Listener para o botão de limpar formulário
    const btnLimpar = document.getElementById("btn-limpar");
    if (btnLimpar) {
        btnLimpar.addEventListener("click", function() {
            // Oculta a seção de resultados
            Utils.toggleElement("resultado-section", false);
            
            // Limpa a mensagem de status do upload
            Utils.clearStatusMessage("upload-status");
            
            // Limpa o input de arquivo
            const fileInput = document.getElementById("hemograma-file");
            if (fileInput) {
                fileInput.value = "";
            }
        });
    }
    
    // Listener para tecla Enter nos campos de formulário
    const formInputs = document.querySelectorAll(".hemogram-form input");
    formInputs.forEach(input => {
        input.addEventListener("keypress", function(e) {
            if (e.key === "Enter") {
                e.preventDefault();
                const btnAnalisar = document.getElementById("btn-analisar");
                if (btnAnalisar && !btnAnalisar.disabled) {
                    btnAnalisar.click();
                }
            }
        });
    });
    
    // Destaca campos com valores fora da referência
    const hemogramInputs = document.querySelectorAll(".hemogram-form input[type=\"number\"]");
    hemogramInputs.forEach(input => {
        input.addEventListener("change", function() {
            highlightAbnormalValue(input);
        });
        input.addEventListener("input", function() {
            highlightAbnormalValue(input);
        });
    });
}

// Destaca campos com valores fora da referência
function highlightAbnormalValue(input) {
    // Remove classes anteriores
    input.classList.remove("alto", "baixo", "normal");
    
    // Se o campo estiver vazio, retorna
    if (!input.value) return;
    
    // Obtém o ID do parâmetro
    const paramId = input.id;
    
    // Obtém o valor de referência
    const refElement = document.getElementById(`ref-${paramId}`);
    if (!refElement || !refElement.textContent) return;
    
    // Extrai os valores mínimo e máximo da referência
    const refText = refElement.textContent;
    const match = refText.match(/(\d+(\.\d+)?)-(\d+(\.\d+)?)/);
    
    if (match) {
        const min = parseFloat(match[1]);
        const max = parseFloat(match[3]);
        const value = parseFloat(input.value);
        
        // Classifica o valor
        if (value < min) {
            input.classList.add("baixo");
        } else if (value > max) {
            input.classList.add("alto");
        } else {
            input.classList.add("normal");
        }
    }
}


