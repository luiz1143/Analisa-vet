#!/usr/bin/env python3
"""
Script para simular um pagamento aprovado do Mercado Pago
e adicionar créditos ao usuário admin@analisavet.com
"""

import sys
import os

# Adicionar o diretório do app ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app import create_app
from models.models import User, db
from services.payment_service import PaymentService

def simulate_payment():
    """Simula um pagamento aprovado e adiciona créditos ao usuário."""
    app = create_app()
    
    with app.app_context():
        # Buscar o usuário admin
        user = User.query.filter_by(email='admin@analisavet.com').first()
        
        if not user:
            print("❌ Usuário admin@analisavet.com não encontrado!")
            return
        
        print(f"👤 Usuário encontrado: {user.email}")
        print(f"💰 Créditos atuais: {user.credits}")
        
        # Simular dados de pagamento aprovado
        payment_data = {
            "status": "approved",
            "external_reference": f"{user.id}_100_1721485200"  # user_id_package_id_timestamp
        }
        
        # Processar o pagamento aprovado
        success, message = PaymentService._process_approved_payment(payment_data)
        
        if success:
            print(f"✅ {message}")
            
            # Verificar créditos após o pagamento
            user = User.query.filter_by(email='admin@analisavet.com').first()
            print(f"💰 Créditos após pagamento: {user.credits}")
        else:
            print(f"❌ Erro ao processar pagamento: {message}")

if __name__ == "__main__":
    simulate_payment()

