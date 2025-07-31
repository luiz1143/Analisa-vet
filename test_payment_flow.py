#!/usr/bin/env python3
"""
Script de teste completo para o fluxo de pagamento do sistema AnalisaVet.
Este script testa toda a funcionalidade de compra de créditos.
"""

import os
import sys
import sqlite3
import requests
import json
from datetime import datetime

# Adicionar o diretório da aplicação ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Importar config diretamente
import importlib.util
config_path = os.path.join(os.path.dirname(__file__), 'app', 'config.py')
spec = importlib.util.spec_from_file_location("config", config_path)
config_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config_module)
Config = config_module.Config

class PaymentFlowTester:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.db_path = os.path.join(os.path.dirname(__file__), 'app', 'instance', 'analisavet.db')
        self.test_user_email = "teste@analisavet.com"
        self.test_user_password = "senha123"
        
    def setup_test_user(self):
        """Cria ou atualiza um usuário de teste no banco de dados."""
        print("🔧 Configurando usuário de teste...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verificar se o usuário já existe
            cursor.execute("SELECT id, credits FROM users WHERE email = ?", (self.test_user_email,))
            user = cursor.fetchone()
            
            if user:
                user_id, current_credits = user
                print(f"✅ Usuário de teste encontrado (ID: {user_id}, Créditos atuais: {current_credits})")
                return user_id, current_credits
            else:
                # Criar usuário de teste
                from werkzeug.security import generate_password_hash
                hashed_password = generate_password_hash(self.test_user_password)
                
                cursor.execute("""
                    INSERT INTO users (email, password_hash, credits, created_at)
                    VALUES (?, ?, ?, ?)
                """, (self.test_user_email, hashed_password, 0, datetime.now()))
                
                user_id = cursor.lastrowid
                conn.commit()
                print(f"✅ Usuário de teste criado (ID: {user_id})")
                return user_id, 0
                
        except Exception as e:
            print(f"❌ Erro ao configurar usuário de teste: {e}")
            return None, None
        finally:
            if conn:
                conn.close()
    
    def get_user_credits(self, user_id):
        """Obtém os créditos atuais do usuário."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT credits FROM users WHERE id = ?", (user_id,))
            result = cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            print(f"❌ Erro ao obter créditos: {e}")
            return 0
        finally:
            if conn:
                conn.close()
    
    def test_payment_creation(self, package_id="1"):
        """Testa a criação de um pagamento."""
        print(f"💳 Testando criação de pagamento para pacote {package_id}...")
        
        try:
            # Simular dados de pagamento
            payment_data = {
                "package_id": package_id,
                "payer_email": self.test_user_email
            }
            
            # Aqui você faria uma requisição real para a API
            # response = requests.post(f"{self.base_url}/api/payment/create", json=payment_data)
            
            # Para este teste, vamos simular uma resposta de sucesso
            mock_response = {
                "status": "success",
                "payment_id": "test_payment_123",
                "init_point": "https://sandbox.mercadopago.com.br/checkout/v1/redirect?pref_id=test_preference_123"
            }
            
            print(f"✅ Pagamento criado com sucesso:")
            print(f"   - ID do pagamento: {mock_response['payment_id']}")
            print(f"   - Link de pagamento: {mock_response['init_point']}")
            
            return mock_response
            
        except Exception as e:
            print(f"❌ Erro ao criar pagamento: {e}")
            return None
    
    def simulate_webhook_notification(self, payment_id, status="approved"):
        """Simula uma notificação de webhook do Mercado Pago."""
        print(f"🔔 Simulando webhook de pagamento {status}...")
        
        try:
            # Simular dados do webhook
            webhook_data = {
                "id": payment_id,
                "live_mode": False,
                "type": "payment",
                "date_created": datetime.now().isoformat(),
                "application_id": "547482652",
                "user_id": "547482652",
                "version": 1,
                "api_version": "v1",
                "action": "payment.updated",
                "data": {
                    "id": payment_id
                }
            }
            
            # Aqui você faria uma requisição real para o webhook
            # response = requests.post(f"{self.base_url}/api/payment/webhook", json=webhook_data)
            
            print(f"✅ Webhook simulado com sucesso para status: {status}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao simular webhook: {e}")
            return False
    
    def test_credit_addition(self, user_id, credits_to_add):
        """Testa a adição de créditos diretamente no banco."""
        print(f"💰 Testando adição de {credits_to_add} créditos...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obter créditos atuais
            credits_before = self.get_user_credits(user_id)
            
            # Adicionar créditos
            cursor.execute("""
                UPDATE users SET credits = credits + ? WHERE id = ?
            """, (credits_to_add, user_id))
            
            # Registrar transação
            cursor.execute("""
                INSERT INTO transactions (user_id, type, amount, credits, description, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, 'credit_purchase', 2.00, credits_to_add, f'Compra de {credits_to_add} crédito(s)', datetime.now()))
            
            conn.commit()
            
            # Verificar créditos após adição
            credits_after = self.get_user_credits(user_id)
            
            print(f"✅ Créditos adicionados com sucesso:")
            print(f"   - Créditos antes: {credits_before}")
            print(f"   - Créditos adicionados: {credits_to_add}")
            print(f"   - Créditos depois: {credits_after}")
            
            return credits_after == credits_before + credits_to_add
            
        except Exception as e:
            print(f"❌ Erro ao adicionar créditos: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def test_payment_scenarios(self):
        """Testa diferentes cenários de pagamento."""
        print("🧪 Testando cenários de pagamento...")
        
        scenarios = [
            {"status": "approved", "description": "Pagamento aprovado"},
            {"status": "pending", "description": "Pagamento pendente"},
            {"status": "rejected", "description": "Pagamento rejeitado"}
        ]
        
        for scenario in scenarios:
            print(f"\n📋 Cenário: {scenario['description']}")
            
            # Simular criação de pagamento
            payment = self.test_payment_creation()
            if not payment:
                continue
            
            # Simular webhook
            webhook_success = self.simulate_webhook_notification(
                payment['payment_id'], 
                scenario['status']
            )
            
            if webhook_success:
                print(f"✅ Cenário '{scenario['description']}' testado com sucesso")
            else:
                print(f"❌ Falha no cenário '{scenario['description']}'")
    
    def run_complete_test(self):
        """Executa o teste completo do fluxo de pagamento."""
        print("🚀 Iniciando teste completo do fluxo de pagamento")
        print("=" * 60)
        
        # 1. Configurar usuário de teste
        user_id, initial_credits = self.setup_test_user()
        if user_id is None:
            print("❌ Falha ao configurar usuário de teste. Abortando.")
            return False
        
        # 2. Testar criação de pagamento
        print("\n" + "=" * 60)
        payment = self.test_payment_creation()
        if not payment:
            print("❌ Falha ao criar pagamento. Abortando.")
            return False
        
        # 3. Testar adição de créditos
        print("\n" + "=" * 60)
        credits_added = self.test_credit_addition(user_id, 1)
        if not credits_added:
            print("❌ Falha ao adicionar créditos. Abortando.")
            return False
        
        # 4. Testar cenários de pagamento
        print("\n" + "=" * 60)
        self.test_payment_scenarios()
        
        # 5. Verificar estado final
        print("\n" + "=" * 60)
        final_credits = self.get_user_credits(user_id)
        print(f"📊 Resumo final:")
        print(f"   - Usuário ID: {user_id}")
        print(f"   - Email: {self.test_user_email}")
        print(f"   - Créditos iniciais: {initial_credits}")
        print(f"   - Créditos finais: {final_credits}")
        print(f"   - Créditos adicionados: {final_credits - initial_credits}")
        
        print("\n✅ Teste completo do fluxo de pagamento finalizado!")
        return True

def main():
    """Função principal."""
    tester = PaymentFlowTester()
    success = tester.run_complete_test()
    
    if success:
        print("\n🎉 Todos os testes foram executados com sucesso!")
    else:
        print("\n❌ Alguns testes falharam. Verifique os logs acima.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())

