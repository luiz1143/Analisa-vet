/**
 * Módulo de pagamento para o aplicativo AnalisaVet
 */

const Payment = {
    selectedPackage: null,
    
    // Inicializa o módulo de pagamento
    init: function() {
        console.log("Payment.init() called!");
        // Adiciona listeners para os cartões de pacotes
        const packageCards = document.querySelectorAll('.package-card');
        packageCards.forEach(card => {
            card.addEventListener('click', this.selectPackage.bind(this));
        });
        
        // Adiciona listener para o botão de pagamento
        const btnPay = document.getElementById('btn-pay');
        if (btnPay) {
            btnPay.addEventListener('click', this.processPayment.bind(this));
        }
        
        // Atualiza créditos atuais
        this.updateCurrentCredits();
    },
    
    // Seleciona um pacote de créditos
    selectPackage: function(event) {
        console.log("Package card clicked!");
        const card = event.currentTarget;
        const packageId = card.dataset.packageId;
        
        // Remove seleção anterior
        document.querySelectorAll('.package-card').forEach(c => {
            c.classList.remove('selected');
        });
        
        // Adiciona seleção atual
        card.classList.add('selected');
        this.selectedPackage = packageId;
        
        // Mostra seção de pagamento
        this.showPaymentSection(packageId);
    },
    
    // Mostra a seção de pagamento com informações do pacote selecionado
    showPaymentSection: function(packageId) {
        const paymentSection = document.getElementById('payment-section');
        const packageInfo = document.getElementById('selected-package-info');
        
        // Buscar informações do pacote
        this.getPackageInfo(packageId).then(packageData => {
            if (packageData) {
                packageInfo.innerHTML = `
                    <div style="background-color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                        <h4>Pacote Selecionado</h4>
                        <p><strong>${packageData.descricao}</strong></p>
                        <p>Valor: <strong>R$ ${packageData.preco.toFixed(2)}</strong></p>
                        <p>Você receberá: <strong>${packageData.creditos} créditos</strong></p>
                    </div>
                `;
                
                paymentSection.style.display = 'block';
                paymentSection.scrollIntoView({ behavior: 'smooth' });
            }
        });
    },
    
    // Busca informações do pacote via API
    getPackageInfo: async function(packageId) {
        try {
            const response = await Utils.fetchAPI('/api/payment/packages');
            if (response.success && response.data[packageId]) {
                return response.data[packageId];
            }
            return null;
        } catch (error) {
            console.error('Erro ao buscar informações do pacote:', error);
            return null;
        }
    },
    
    // Processa o pagamento
    processPayment: async function() {
        if (!this.selectedPackage) {
            Utils.showStatusMessage('payment-status', 'Selecione um pacote primeiro.', 'error');
            return;
        }
        
        try {
            Utils.showStatusMessage('payment-status', 'Criando preferência de pagamento...', 'info');
            
            const response = await Utils.fetchAPI('/api/payment/create-preference', {
                method: 'POST',
                body: {
                    package_id: this.selectedPackage
                }
            });
            
            if (response.success) {
                // Redirecionar para o Mercado Pago
                const initPoint = response.data.sandbox_init_point || response.data.init_point;
                Utils.showStatusMessage('payment-status', 'Redirecionando para o Mercado Pago...', 'success');
                
                // Aguardar um momento antes de redirecionar
                setTimeout(() => {
                    window.location.href = initPoint;
                }, 1500);
            } else {
                Utils.showStatusMessage('payment-status', response.error || 'Erro ao criar pagamento.', 'error');
            }
        } catch (error) {
            console.error('Erro ao processar pagamento:', error);
            Utils.showStatusMessage('payment-status', 'Erro ao processar pagamento. Tente novamente.', 'error');
        }
    },
    
    // Atualiza a exibição de créditos atuais
    updateCurrentCredits: async function() {
        try {
            const response = await Utils.fetchAPI('/api/auth/status');
            if (response.success && response.data.logged_in) {
                const creditsDisplay = document.getElementById("current-credits-display");
                if (creditsDisplay) {
                    creditsDisplay.textContent = response.data.credits;
                }
            }
        } catch (error) {
            console.error('Erro ao atualizar créditos:', error);
        }
    }
};

// Inicializa o módulo quando o DOM estiver carregado
document.addEventListener("DOMContentLoaded", function() {
    console.log("DOMContentLoaded event fired. Initializing Payment module.");
    Payment.init();
});

