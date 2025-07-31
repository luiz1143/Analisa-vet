"""
Configurações do aplicativo AnalisaVet.
"""

import os
import secrets

class Config:
    """Configuração base para o aplicativo Flask."""
    # Configurações gerais
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(16)
    DEBUG = False
    TESTING = False
    
    # Configurações do banco de dados
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///analisavet.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configurações de upload
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    ALLOWED_EXTENSIONS = {'pdf', 'csv'}
    
    # Configurações de sessão
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = 86400  # 24 horas em segundos
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Configurações específicas do AnalisaVet
    CREDITOS_POR_ANALISE = 1
    
    # Configurações do Mercado Pago
    MERCADO_PAGO_ACCESS_TOKEN = os.environ.get("MERCADO_PAGO_ACCESS_TOKEN") or "APP_USR-2264711140391280-052816-ced30592a1aec42b7e2a3d10d393760e-547482652"
    MERCADO_PAGO_PUBLIC_KEY = os.environ.get("MERCADO_PAGO_PUBLIC_KEY") or "APP_USR-e874aaba-0c2f-4fa7-8104-4bbdd829c0e3"
    MERCADO_PAGO_WEBHOOK_SECRET = os.environ.get("MERCADO_PAGO_WEBHOOK_SECRET") or "9a23766731c8550e52885e357275412ed02f6163be52edfc4c7ca40cb52835fd"
    
    # Configurações de pagamento
    PRECO_POR_ANALISE = 2.00  # R$ 2,00 por análise
    PACOTES_CREDITOS = {
        '1': {'creditos': 1, 'preco': 2.00, 'descricao': '1 crédito'},
        '10': {'creditos': 10, 'preco': 18.00, 'descricao': '10 créditos (10% desconto)'},
        '25': {'creditos': 25, 'preco': 45.00, 'descricao': '25 créditos (10% desconto)'},
        '50': {'creditos': 50, 'preco': 80.00, 'descricao': '50 créditos (20% desconto)'},
        '100': {'creditos': 100, 'preco': 140.00, 'descricao': '100 créditos (30% desconto)'}
    }
    
    @staticmethod
    def init_app(app):
        """Inicializa o aplicativo com as configurações."""
        # Criar diretório de uploads se não existir
        if not os.path.exists(Config.UPLOAD_FOLDER):
            os.makedirs(Config.UPLOAD_FOLDER)


class DevelopmentConfig(Config):
    """Configuração para ambiente de desenvolvimento."""
    DEBUG = True
    SESSION_COOKIE_SECURE = False  # Permitir cookies sem HTTPS em desenvolvimento
    SESSION_COOKIE_SAMESITE = 'Lax'  # Permitir cookies cross-site em desenvolvimento
    
    # URL base para desenvolvimento
    BASE_URL = os.environ.get("BASE_URL") or "https://5000-irptf51rfmrza92v5jgs9-6b0cb216.manus.computer"


class TestingConfig(Config):
    """Configuração para ambiente de testes."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Configuração para ambiente de produção."""
    DEBUG = False
    TESTING = False
    
    # Configurações de segurança para produção
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # URL base para produção (será definida via variável de ambiente)
    BASE_URL = os.environ.get("BASE_URL") or "https://analisavet.onrender.com"
    
    # Configuração do banco de dados para produção (PostgreSQL no Render)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///analisavet.db'


# Mapeamento de configurações
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
