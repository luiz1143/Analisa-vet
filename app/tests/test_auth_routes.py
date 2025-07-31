"""
Testes para as rotas de autenticação do aplicativo AnalisaVet.
"""

import json
import pytest

def test_registro_usuario_sucesso(client):
    """Testa o registro de um novo usuário com sucesso."""
    response = client.post('/api/auth/register', 
                          json={'email': 'novo@example.com', 'password': 'senha123'})
    data = json.loads(response.data)
    
    assert response.status_code == 201
    assert data['success'] == True
    assert 'user_id' in data['data']
    assert data['data']['email'] == 'novo@example.com'

def test_registro_usuario_email_existente(client):
    """Testa o registro de um usuário com email já existente."""
    response = client.post('/api/auth/register', 
                          json={'email': 'teste@example.com', 'password': 'senha123'})
    data = json.loads(response.data)
    
    assert response.status_code == 400
    assert data['success'] == False
    assert 'já está cadastrado' in data['error']

def test_registro_usuario_dados_incompletos(client):
    """Testa o registro de um usuário com dados incompletos."""
    response = client.post('/api/auth/register', json={'email': 'incompleto@example.com'})
    data = json.loads(response.data)
    
    assert response.status_code == 400
    assert data['success'] == False
    assert 'obrigatórios' in data['error']

def test_login_usuario_sucesso(client):
    """Testa o login de um usuário com sucesso."""
    response = client.post('/api/auth/login', 
                          json={'email': 'teste@example.com', 'password': 'senha123'})
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['success'] == True
    assert 'user_id' in data['data']
    assert data['data']['email'] == 'teste@example.com'
    assert 'credits' in data['data']

def test_login_usuario_credenciais_invalidas(client):
    """Testa o login de um usuário com credenciais inválidas."""
    response = client.post('/api/auth/login', 
                          json={'email': 'teste@example.com', 'password': 'senhaerrada'})
    data = json.loads(response.data)
    
    assert response.status_code == 401
    assert data['success'] == False
    assert 'incorretos' in data['error']

def test_login_usuario_dados_incompletos(client):
    """Testa o login de um usuário com dados incompletos."""
    response = client.post('/api/auth/login', json={'email': 'teste@example.com'})
    data = json.loads(response.data)
    
    assert response.status_code == 400
    assert data['success'] == False
    assert 'obrigatórios' in data['error']

def test_status_usuario(client):
    """Testa a verificação de status do usuário."""
    # Primeiro faz login
    client.post('/api/auth/login', 
               json={'email': 'teste@example.com', 'password': 'senha123'})
    
    # Depois verifica o status
    response = client.get('/api/auth/status')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['success'] == True
    assert data['data']['logged_in'] == True
    assert data['data']['email'] == 'teste@example.com'
    assert 'credits' in data['data']
    assert 'clinic_info' in data['data']

def test_status_usuario_sem_login(client):
    """Testa a verificação de status sem usuário logado."""
    response = client.get('/api/auth/status')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['success'] == True
    assert data['data']['logged_in'] == False

def test_logout_usuario(client):
    """Testa o logout de um usuário."""
    # Primeiro faz login
    client.post('/api/auth/login', 
               json={'email': 'teste@example.com', 'password': 'senha123'})
    
    # Depois faz logout
    response = client.post('/api/auth/logout')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['success'] == True
    
    # Verifica se realmente deslogou
    status_response = client.get('/api/auth/status')
    status_data = json.loads(status_response.data)
    assert status_data['data']['logged_in'] == False
