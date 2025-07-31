"""
Arquivo principal do aplicativo AnalisaVet.
"""

from flask import Flask, render_template, send_from_directory, redirect, url_for
from flask_login import LoginManager
import os
import logging

from .config import config
from .models.models import db, User
from .routes.auth_routes import auth_bp
from .routes.analysis_routes import analysis_bp
from .routes.report_routes import report_bp
from .routes.payment_routes import payment_bp
from .routes.test_payment_routes import test_payment_bp

def create_app(config_name='development'):
    """Cria e configura a aplicação Flask."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Configurar logging para o console
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Inicializar extensões
    db.init_app(app)
    
    # Configurar login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Registrar blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(test_payment_bp)
    
    # Criar tabelas do banco de dados
    with app.app_context():
        db.create_all()
        print("Tabelas do banco de dados verificadas/criadas.")
    
    # Rota para servir arquivos estáticos
    @app.route('/static/<path:filename>')
    def serve_static(filename):
        return send_from_directory(app.static_folder, filename)
    
    # Rota principal
    @app.route("/")
    def index():
        from flask_login import current_user
        user_credits = current_user.credits if current_user.is_authenticated else 0
        return render_template('index.html', user_credits=user_credits)
    
    # Rotas de autenticação
    @app.route('/login')
    def login():
        return render_template('login.html')
    
    @app.route('/register')
    def register():
        return render_template('register.html')
    
    # Rota de redirecionamento para o teste de compra de créditos
    @app.route("/test-comprar-creditos")
    def redirect_test_buy_credits():
        return redirect(url_for("test_payment.test_buy_credits_page"))

    return app  # <-- aqui estava o erro (agora está correto)

# Rodar o servidor local
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
