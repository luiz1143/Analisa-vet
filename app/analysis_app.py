"""
Versão do app.py com os blueprints de autenticação e análise ativados.
"""

from flask import Flask, render_template, send_from_directory, jsonify
# Importações necessárias
from flask_login import LoginManager
from config import config
from models.models import db, User

# Importando blueprints de autenticação e análise
from routes.auth_routes import auth_bp
from routes.analysis_routes import analysis_bp
# Comentando o blueprint de relatórios
# from routes.report_routes import report_bp

def create_app(config_name='development'):
    """Cria e configura a aplicação Flask."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Inicializar extensões
    db.init_app(app)
    
    # Configurando login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Registrando blueprints de autenticação e análise
    app.register_blueprint(auth_bp)
    app.register_blueprint(analysis_bp)
    # app.register_blueprint(report_bp)
    
    # Criar tabelas do banco de dados
    with app.app_context():
        db.create_all()
        print("Tabelas do banco de dados verificadas/criadas.")
    
    # Rota para servir arquivos estáticos
    @app.route('/static/<path:filename>')
    def serve_static(filename):
        return send_from_directory(app.static_folder, filename)
    
    # Rota principal simplificada para teste
    @app.route('/')
    def index():
        return "Servidor AnalisaVet - Versão com blueprints de autenticação e análise"
    
    # Rota de teste para API
    @app.route('/api/test')
    def test_api():
        return jsonify({
            'success': True,
            'message': 'API de teste funcionando!'
        })
    
    # Rotas de autenticação
    @app.route('/login')
    def login():
        return render_template('login.html')
    
    @app.route('/register')
    def register():
        return render_template('register.html')
    
    return app

# Criar aplicação
app = create_app()

if __name__ == '__main__':
    print("Iniciando servidor Flask com blueprints de autenticação e análise...")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
