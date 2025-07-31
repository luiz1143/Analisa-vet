"""
Script para validação manual das rotas principais do AnalisaVet.
"""

import json
from app import create_app

def test_valores_referencia():
    """Testa a obtenção de valores de referência para cães e gatos."""
    app = create_app('development')
    with app.test_client() as client:
        # Teste para cães
        response_cao = client.get('/api/analysis/reference-values?especie=Cão')
        data_cao = json.loads(response_cao.data)
        print("\n=== VALORES DE REFERÊNCIA PARA CÃO ===")
        print(json.dumps(data_cao, indent=2))
        
        # Teste para gatos
        response_gato = client.get('/api/analysis/reference-values?especie=Gato')
        data_gato = json.loads(response_gato.data)
        print("\n=== VALORES DE REFERÊNCIA PARA GATO ===")
        print(json.dumps(data_gato, indent=2))

def test_autenticacao():
    """Testa o fluxo de autenticação (registro, login, status)."""
    app = create_app('development')
    with app.test_client() as client:
        # Teste de registro
        response_registro = client.post('/api/auth/register', 
                                      json={'email': 'teste_manual@example.com', 'password': 'senha123'})
        data_registro = json.loads(response_registro.data)
        print("\n=== REGISTRO DE USUÁRIO ===")
        print(json.dumps(data_registro, indent=2))
        
        # Teste de login
        response_login = client.post('/api/auth/login', 
                                   json={'email': 'teste_manual@example.com', 'password': 'senha123'})
        data_login = json.loads(response_login.data)
        print("\n=== LOGIN DE USUÁRIO ===")
        print(json.dumps(data_login, indent=2))
        
        # Teste de status
        response_status = client.get('/api/auth/status')
        data_status = json.loads(response_status.data)
        print("\n=== STATUS DO USUÁRIO ===")
        print(json.dumps(data_status, indent=2))

if __name__ == "__main__":
    print("Iniciando validação manual das rotas principais...")
    test_valores_referencia()
    test_autenticacao()
    print("\nValidação manual concluída!")
