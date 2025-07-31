/**
 * Módulo de configurações da clínica para o aplicativo AnalisaVet
 */

const ClinicConfig = {
    // Inicializa o módulo de configurações da clínica
    init: function() {
        // Adiciona listeners para os botões
        const btnSaveClinicInfo = document.getElementById("btn-save-clinic-info");
        const btnUploadLogo = document.getElementById("btn-upload-logo");
        const btnBuyCredits = document.getElementById("btn-buy-credits");
        
        if (btnSaveClinicInfo) {
            btnSaveClinicInfo.addEventListener("click", this.saveClinicInfo.bind(this));
        }
        
        if (btnUploadLogo) {
            btnUploadLogo.addEventListener("click", this.uploadLogo.bind(this));
        }
        
        // Carrega as informações da clínica quando o usuário faz login
        this.loadClinicInfo();
    },
    
    // Alterna a visibilidade da seção de configurações da clínica
    toggleClinicConfig: function() {
        const section = document.getElementById("clinic-config-section");
        if (section) {
            const isVisible = section.style.display !== "none";
            section.style.display = isVisible ? "none" : "block";
            
            if (!isVisible) {
                // Carrega as informações quando a seção é exibida
                this.loadClinicInfo();
                // Rola para a seção
                section.scrollIntoView({ behavior: "smooth" });
            }
        }
    },
    
    // Carrega as informações da clínica do servidor
    loadClinicInfo: async function() {
        if (!Auth.isLoggedIn()) return;
        
        try {
            const response = await Utils.fetchAPI("/api/auth/clinic-info");
            
            if (response.success) {
                const clinicInfo = response.data;
                
                // Preenche os campos com as informações da clínica
                document.getElementById("clinic-name").value = clinicInfo.nome || "";
                document.getElementById("clinic-email").value = clinicInfo.email || "";
                document.getElementById("clinic-address").value = clinicInfo.endereco || "";
                document.getElementById("clinic-phone").value = clinicInfo.telefone || "";
                document.getElementById("clinic-crmv").value = clinicInfo.crmv || "";
                
                // Exibe o logo atual se existir
                if (clinicInfo.logo_path) {
                    const logoPreview = document.getElementById("current-logo-preview");
                    const logoImg = document.getElementById("current-logo-img");
                    
                    // Certifica-se de que o caminho do logo está correto para o frontend
                    logoImg.src = `/static/${clinicInfo.logo_path}`;
                    logoPreview.style.display = "block";
                }
            }
        } catch (error) {
            console.error("Erro ao carregar informações da clínica:", error);
        }
    },
    
    // Salva as informações da clínica
    saveClinicInfo: async function() {
        if (!Auth.isLoggedIn()) {
            Utils.showStatusMessage("clinic-config-status", "Você precisa estar logado para salvar as informações.", "error");
            return;
        }
        
        // Coleta os dados do formulário
        const clinicInfo = {
            nome: document.getElementById("clinic-name").value,
            email: document.getElementById("clinic-email").value,
            endereco: document.getElementById("clinic-address").value,
            telefone: document.getElementById("clinic-phone").value,
            crmv: document.getElementById("clinic-crmv").value
        };
        
        try {
            Utils.showStatusMessage("clinic-config-status", "Salvando informações...", "info");
            
            const response = await Utils.fetchAPI("/api/auth/clinic-info", {
                method: "PUT",
                body: clinicInfo
            });
            
            if (response.success) {
                Utils.showStatusMessage("clinic-config-status", "Informações salvas com sucesso!", "success");
            } else {
                Utils.showStatusMessage("clinic-config-status", response.error || "Erro ao salvar informações.", "error");
            }
        } catch (error) {
            console.error("Erro ao salvar informações da clínica:", error);
            Utils.showStatusMessage("clinic-config-status", "Erro ao salvar informações. Tente novamente.", "error");
        }
    },
    
    // Faz upload do logo da clínica
    uploadLogo: async function() {
        if (!Auth.isLoggedIn()) {
            Utils.showStatusMessage("clinic-config-status", "Você precisa estar logado para fazer upload do logo.", "error");
            return;
        }
        
        const logoFile = document.getElementById("clinic-logo").files[0];
        
        if (!logoFile) {
            Utils.showStatusMessage("clinic-config-status", "Selecione um arquivo de logo primeiro.", "error");
            return;
        }
        
        // Verificar tamanho do arquivo (máximo 5MB)
        if (logoFile.size > 5 * 1024 * 1024) {
            Utils.showStatusMessage("clinic-config-status", "O arquivo é muito grande. Máximo 5MB.", "error");
            return;
        }
        
        // Criar FormData para upload
        const formData = new FormData();
        formData.append("logo", logoFile);
        
        try {
            Utils.showStatusMessage("clinic-config-status", "Fazendo upload do logo...", "info");
            
            const response = await Utils.fetchAPI("/api/auth/clinic-logo", {
                method: "POST",
                body: formData
            });
            
            if (response.success) {
                Utils.showStatusMessage("clinic-config-status", "Logo atualizado com sucesso!", "success");
                
                // Atualiza a prévia do logo
                const logoPreview = document.getElementById("current-logo-preview");
                const logoImg = document.getElementById("current-logo-img");
                
                // O caminho retornado pelo backend já deve ser o caminho relativo correto para o static
                logoImg.src = `/static/${response.data.logo_path}?t=${Date.now()}`; // Cache bust
                logoPreview.style.display = "block";
                
                // Limpa o campo de arquivo
                document.getElementById("clinic-logo").value = "";
            } else {
                Utils.showStatusMessage("clinic-config-status", response.error || "Erro ao fazer upload do logo.", "error");
            }
        } catch (error) {
            console.error("Erro ao fazer upload do logo:", error);
            Utils.showStatusMessage("clinic-config-status", "Erro ao fazer upload do logo. Tente novamente.", "error");
        }
    }
};

