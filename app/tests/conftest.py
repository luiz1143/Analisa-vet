"""
Configurações para testes do aplicativo AnalisaVet.
"""

import pytest
import os
import tempfile
from app import create_app
from models.models import db, User

@pytest.fixture
def app():
    """Cria e configura uma instância de aplicativo Flask para testes."""
    # Criar um arquivo de banco de dados temporário
    db_fd, db_path = tempfile.mkstemp()
    
    # Configurar aplicativo para testes
    app = create_app('testing')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SERVER_NAME'] = 'localhost.localdomain'
    
    # Criar contexto de aplicativo e tabelas do banco de dados
    with app.app_context():
        db.create_all()
        # Criar um usuário de teste
        user = User(email='teste@example.com')
        user.set_password('senha123')
        user.credits = 10
        db.session.add(user)
        db.session.commit()
    
    yield app
    
    # Limpar após os testes
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """Cria um cliente de teste para o aplicativo Flask."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Cria um runner de linha de comando para o aplicativo Flask."""
    return app.test_cli_runner()
