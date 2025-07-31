/**
 * Módulo de autenticação para o aplicativo AnalisaVet
 */

const Auth = {
    // Estado do usuário
    user: {
        loggedIn: false,
        email: null,
        credits: 0
    },
    
    // Inicializa o módulo de autenticação
    init: function() {
        // Adiciona listeners para os botões de login, registro e logout
        const loginBtn = document.getElementById('login-btn');
        const registerBtn = document.getElementById('register-btn');
        const logoutBtn = document.getElementById('logout-btn');
        
        if (logoutBtn) {
            logoutBtn.addEventListener('click', this.logout.bind(this));
        }
        
        // Verifica o status de autenticação ao carregar a página
        this.checkAuthStatus();
    },
    
    // Verifica o status de autenticação do usuário
    checkAuthStatus: async function() {
        try {
            const response = await Utils.fetchAPI('/api/auth/status');
            
            if (response.success) {
                const status = response.data;
                
                if (status.logged_in) {
                    this.user.loggedIn = true;
                    this.user.email = status.email;
                    this.user.credits = status.credits;
                    
                    // Atualiza a interface para usuário logado
                    this.updateUI(true);
                } else {
                    // Atualiza a interface para usuário não logado
                    this.updateUI(false);
                }
            }
        } catch (error) {
            console.error('Erro ao verificar status de autenticação:', error);
            // Em caso de erro, assume que o usuário não está logado
            this.updateUI(false);
        }
    },
    
    // Realiza o logout do usuário
    logout: async function() {
        try {
            const response = await Utils.fetchAPI('/api/auth/logout', {
                method: 'POST'
            });
            
            if (response.success) {
                // Limpa os dados do usuário
                this.user.loggedIn = false;
                this.user.email = null;
                this.user.credits = 0;
                
                // Atualiza a interface para usuário não logado
                this.updateUI(false);
                
                // Redireciona para a página inicial
                window.location.href = '/';
            }
        } catch (error) {
            console.error('Erro ao realizar logout:', error);
            alert('Erro ao realizar logout. Por favor, tente novamente.');
        }
    },
    
    // Atualiza a interface de acordo com o status de autenticação
    updateUI: function(isLoggedIn) {
        const loginRegisterSection = document.getElementById('login-register-section');
        const userInfoSection = document.getElementById('user-info-section');
        const userDisplay = document.getElementById('user-display');
        const creditsDisplay = document.getElementById('credits-display');
        
        if (isLoggedIn) {
            // Mostra informações do usuário e esconde botões de login/registro
            if (loginRegisterSection) loginRegisterSection.style.display = 'none';
            if (userInfoSection) userInfoSection.style.display = 'block';
            
            // Atualiza as informações exibidas
            if (userDisplay) userDisplay.textContent = this.user.email;
            if (creditsDisplay) creditsDisplay.textContent = this.user.credits;
            
            // Habilita funcionalidades que requerem autenticação
            const btnAnalisar = document.getElementById('btn-analisar');
            if (btnAnalisar) {
                btnAnalisar.disabled = false;
                btnAnalisar.title = '';
            }
        } else {
            // Mostra botões de login/registro e esconde informações do usuário
            if (loginRegisterSection) loginRegisterSection.style.display = 'block';
            if (userInfoSection) userInfoSection.style.display = 'none';
            
            // Desabilita funcionalidades que requerem autenticação
            const btnAnalisar = document.getElementById('btn-analisar');
            if (btnAnalisar) {
                btnAnalisar.disabled = true;
                btnAnalisar.title = 'Faça login para analisar hemogramas';
            }
        }
    },
    
    // Verifica se o usuário está logado
    isLoggedIn: function() {
        return this.user.loggedIn;
    },
    
    // Obtém os créditos do usuário
    getCredits: function() {
        return this.user.credits;
    },
    
    // Atualiza os créditos do usuário
    updateCredits: function(newCredits) {
        this.user.credits = newCredits;
        
        // Atualiza a exibição dos créditos
        const creditsDisplay = document.getElementById('credits-display');
        if (creditsDisplay) {
            creditsDisplay.textContent = newCredits;
        }
    }
};


        const buyCreditsBtn = document.getElementById('btn-buy-credits');
        if (buyCreditsBtn) {
            buyCreditsBtn.addEventListener('click', function() {
                window.location.href = '/comprar-creditos';
            });
        }

