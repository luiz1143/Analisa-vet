"""
Testes para as rotas de análise e valores de referência do aplicativo AnalisaVet.
"""

import json
import pytest
import io

def test_valores_referencia_cao(client):
    """Testa a obtenção de valores de referência para cães."""
    response = client.get('/api/analysis/reference-values?especie=Cão')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['success'] == True
    assert 'hemacias' in data['data']
    assert 'leucocitos' in data['data']
    assert 'plaquetas' in data['data']

def test_valores_referencia_gato(client):
    """Testa a obtenção de valores de referência para gatos."""
    response = client.get('/api/analysis/reference-values?especie=Gato')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['success'] == True
    assert 'hemacias' in data['data']
    assert 'leucocitos' in data['data']
    assert 'plaquetas' in data['data']

def test_valores_referencia_especie_invalida(client):
    """Testa a obtenção de valores de referência para espécie inválida."""
    response = client.get('/api/analysis/reference-values?especie=Cavalo')
    data = json.loads(response.data)
    
    assert response.status_code == 400
    assert data['success'] == False
    assert 'Espécie inválida' in data['error']

def test_valores_referencia_sem_especie(client):
    """Testa a obtenção de valores de referência sem especificar espécie."""
    response = client.get('/api/analysis/reference-values')
    data = json.loads(response.data)
    
    assert response.status_code == 400
    assert data['success'] == False
    assert 'Espécie é obrigatória' in data['error']

def test_analise_hemograma_requer_login(client):
    """Testa que a análise de hemograma requer login."""
    response = client.post('/api/analysis/analyze', 
                          json={'especie': 'Cão', 'hemacias': 6.5, 'hemoglobina': 15.0})
    
    # Deve redirecionar para login ou retornar 401/403
    assert response.status_code in [302, 401, 403]

def test_analise_hemograma_sucesso(client):
    """Testa a análise de hemograma com sucesso."""
    # Primeiro faz login
    client.post('/api/auth/login', 
               json={'email': 'teste@example.com', 'password': 'senha123'})
    
    # Dados do hemograma para análise
    dados_hemograma = {
        'especie': 'Cão',
        'nome_paciente': 'Rex',
        'raca': 'Labrador',
        'idade': '5 anos',
        'sexo': 'Macho',
        'nome_tutor': 'João Silva',
        'hemacias': 6.5,
        'hemoglobina': 15.0,
        'hematocrito': 45.0,
        'vcm': 70.0,
        'hcm': 22.0,
        'chcm': 33.0,
        'leucocitos': 10000,
        'segmentados': 7000,
        'linfocitos': 2500,
        'monocitos': 500,
        'eosinofilos': 200,
        'basofilos': 50,
        'plaquetas': 300000,
        'proteina': 7.0
    }
    
    response = client.post('/api/analysis/analyze', json=dados_hemograma)
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['success'] == True
    assert 'diagnostico' in data['data']
    assert 'credits_remaining' in data['data']
    assert 'analysis_id' in data['data']

def test_analise_hemograma_dados_incompletos(client):
    """Testa a análise de hemograma com dados incompletos."""
    # Primeiro faz login
    client.post('/api/auth/login', 
               json={'email': 'teste@example.com', 'password': 'senha123'})
    
    response = client.post('/api/analysis/analyze', json={})
    data = json.loads(response.data)
    
    assert response.status_code == 400
    assert data['success'] == False
    assert 'inválidos ou incompletos' in data['error']

def test_historico_analises_requer_login(client):
    """Testa que o histórico de análises requer login."""
    response = client.get('/api/analysis/history')
    
    # Deve redirecionar para login ou retornar 401/403
    assert response.status_code in [302, 401, 403]

def test_historico_analises_sucesso(client):
    """Testa a obtenção do histórico de análises com sucesso."""
    # Primeiro faz login
    client.post('/api/auth/login', 
               json={'email': 'teste@example.com', 'password': 'senha123'})
    
    # Realiza uma análise para ter histórico
    dados_hemograma = {
        'especie': 'Cão',
        'hemacias': 6.5,
        'hemoglobina': 15.0,
        'hematocrito': 45.0
    }
    client.post('/api/analysis/analyze', json=dados_hemograma)
    
    # Obtém o histórico
    response = client.get('/api/analysis/history')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['success'] == True
    assert isinstance(data['data'], list)
    # Se houver análises no histórico, verifica a estrutura
    if len(data['data']) > 0:
        assert 'id' in data['data'][0]
        assert 'created_at' in data['data'][0]
        assert 'patient_info' in data['data'][0]
        assert 'analysis_result' in data['data'][0]

def test_upload_arquivo_requer_login(client):
    """Testa que o upload de arquivo requer login."""
    data = {'file': (io.BytesIO(b'test file content'), 'test.pdf')}
    response = client.post('/api/analysis/upload', data=data)
    
    # Deve redirecionar para login ou retornar 401/403
    assert response.status_code in [302, 401, 403]
