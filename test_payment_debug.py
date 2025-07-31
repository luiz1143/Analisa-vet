import sys
import os
import requests
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from app import create_app, db
from models.models import User
from services.payment_service import PaymentService

app = create_app("development")

with app.app_context():
    # Buscar usuário de teste
    user = User.query.filter_by(email="test@example.com").first()
    if not user:
        print("Usuário de teste não encontrado.")
        exit(1)
    
    print(f"Usuário encontrado: {user.email} (ID: {user.id})")
    print(f"Créditos atuais: {user.credits}")
    
    # Testar criação de preferência de pagamento
    print("\n=== Testando criação de preferência de pagamento ===")
    
    success, result = PaymentService.create_payment_preference(user.id, "1")
    
    if success:
        print("✅ Preferência criada com sucesso!")
        print(f"Preference ID: {result['preference_id']}")
        print(f"Init Point: {result['init_point']}")
        if 'sandbox_init_point' in result:
            print(f"Sandbox Init Point: {result['sandbox_init_point']}")
    else:
        print("❌ Erro ao criar preferência:")
        print(result)
    
    # Testar validação das credenciais do Mercado Pago
    print("\n=== Testando credenciais do Mercado Pago ===")
    
    access_token = app.config['MERCADO_PAGO_ACCESS_TOKEN']
    public_key = app.config['MERCADO_PAGO_PUBLIC_KEY']
    
    print(f"Access Token: {access_token[:20]}...")
    print(f"Public Key: {public_key[:20]}...")
    
    # Testar acesso à API do Mercado Pago
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get("https://api.mercadopago.com/users/me", headers=headers)
        if response.status_code == 200:
            user_info = response.json()
            print("✅ Credenciais válidas!")
            print(f"Usuário MP: {user_info.get('email', 'N/A')}")
            print(f"País: {user_info.get('site_id', 'N/A')}")
        else:
            print("❌ Credenciais inválidas!")
            print(f"Status: {response.status_code}")
            print(f"Resposta: {response.text}")
    except Exception as e:
        print(f"❌ Erro ao validar credenciais: {str(e)}")

