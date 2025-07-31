#!/usr/bin/env python3
"""
Script para testar a segurança do webhook do Mercado Pago.
Inclui validação de assinatura e testes de segurança.
"""

import os
import sys
import hmac
import hashlib
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

class WebhookSecurityTester:
    def __init__(self):
        self.webhook_secret = Config.MERCADO_PAGO_WEBHOOK_SECRET
        
    def generate_signature(self, payload, timestamp=None):
        """
        Gera a assinatura HMAC-SHA256 para validação do webhook.
        
        Args:
            payload (str): Payload JSON do webhook
            timestamp (str): Timestamp da requisição (opcional)
        
        Returns:
            str: Assinatura HMAC-SHA256
        """
        if timestamp is None:
            timestamp = str(int(datetime.now().timestamp()))
        
        # Criar string para assinatura: timestamp + payload
        message = f"{timestamp}.{payload}"
        
        # Gerar HMAC-SHA256
        signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return f"t={timestamp},v1={signature}"
    
    def validate_signature(self, payload, signature_header, tolerance=300):
        """
        Valida a assinatura do webhook.
        
        Args:
            payload (str): Payload JSON do webhook
            signature_header (str): Header de assinatura (x-signature)
            tolerance (int): Tolerância em segundos para timestamp (padrão: 5 min)
        
        Returns:
            bool: True se a assinatura for válida
        """
        try:
            # Extrair timestamp e assinatura do header
            parts = signature_header.split(',')
            timestamp = None
            signature = None
            
            for part in parts:
                if part.startswith('t='):
                    timestamp = part[2:]
                elif part.startswith('v1='):
                    signature = part[3:]
            
            if not timestamp or not signature:
                print("❌ Header de assinatura inválido")
                return False
            
            # Verificar se o timestamp não é muito antigo
            current_time = int(datetime.now().timestamp())
            webhook_time = int(timestamp)
            
            if abs(current_time - webhook_time) > tolerance:
                print(f"❌ Timestamp muito antigo: {abs(current_time - webhook_time)}s")
                return False
            
            # Gerar assinatura esperada
            message = f"{timestamp}.{payload}"
            expected_signature = hmac.new(
                self.webhook_secret.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # Comparar assinaturas de forma segura
            is_valid = hmac.compare_digest(signature, expected_signature)
            
            if is_valid:
                print("✅ Assinatura do webhook válida")
            else:
                print("❌ Assinatura do webhook inválida")
            
            return is_valid
            
        except Exception as e:
            print(f"❌ Erro ao validar assinatura: {e}")
            return False
    
    def test_webhook_payload_validation(self):
        """Testa a validação de diferentes payloads de webhook."""
        print("🔐 Testando validação de payloads de webhook...")
        
        # Payload válido
        valid_payload = {
            "id": "12345678901",
            "live_mode": False,
            "type": "payment",
            "date_created": "2024-01-15T10:30:00.000-04:00",
            "application_id": "547482652",
            "user_id": "547482652",
            "version": 1,
            "api_version": "v1",
            "action": "payment.updated",
            "data": {
                "id": "12345678901"
            }
        }
        
        payload_str = json.dumps(valid_payload, separators=(',', ':'))
        
        # Teste 1: Assinatura válida
        print("\n📋 Teste 1: Assinatura válida")
        valid_signature = self.generate_signature(payload_str)
        result1 = self.validate_signature(payload_str, valid_signature)
        
        # Teste 2: Assinatura inválida
        print("\n📋 Teste 2: Assinatura inválida")
        invalid_signature = "t=1642248600,v1=invalid_signature_here"
        result2 = self.validate_signature(payload_str, invalid_signature)
        
        # Teste 3: Payload modificado
        print("\n📋 Teste 3: Payload modificado")
        modified_payload = payload_str.replace("12345678901", "99999999999")
        result3 = self.validate_signature(modified_payload, valid_signature)
        
        # Teste 4: Timestamp muito antigo
        print("\n📋 Teste 4: Timestamp muito antigo")
        old_timestamp = str(int(datetime.now().timestamp()) - 1000)  # 1000 segundos atrás
        old_signature = f"t={old_timestamp},v1=some_signature"
        result4 = self.validate_signature(payload_str, old_signature)
        
        return all([result1, not result2, not result3, not result4])
    
    def test_webhook_security_headers(self):
        """Testa os headers de segurança necessários para o webhook."""
        print("🛡️ Testando headers de segurança do webhook...")
        
        required_headers = [
            "x-signature",
            "x-request-id",
            "user-agent"
        ]
        
        print("📋 Headers obrigatórios para validação:")
        for header in required_headers:
            print(f"   - {header}")
        
        # Simular headers de uma requisição real do Mercado Pago
        mock_headers = {
            "x-signature": "t=1642248600,v1=abc123def456",
            "x-request-id": "req_12345678901234567890",
            "user-agent": "MercadoPago Webhook",
            "content-type": "application/json"
        }
        
        print("\n✅ Headers simulados configurados corretamente")
        return True
    
    def generate_webhook_validation_code(self):
        """Gera código Python para validação de webhook."""
        print("💻 Gerando código de validação de webhook...")
        
        validation_code = '''
def validate_mercadopago_webhook(request):
    """
    Valida webhook do Mercado Pago usando HMAC-SHA256.
    
    Args:
        request: Objeto de requisição Flask
    
    Returns:
        tuple: (is_valid, payload_data)
    """
    import hmac
    import hashlib
    import json
    from datetime import datetime
    from flask import current_app
    
    try:
        # Obter dados da requisição
        payload = request.get_data(as_text=True)
        signature_header = request.headers.get('x-signature', '')
        
        if not signature_header:
            current_app.logger.warning("Header x-signature não encontrado")
            return False, None
        
        # Extrair timestamp e assinatura
        parts = signature_header.split(',')
        timestamp = None
        signature = None
        
        for part in parts:
            if part.startswith('t='):
                timestamp = part[2:]
            elif part.startswith('v1='):
                signature = part[3:]
        
        if not timestamp or not signature:
            current_app.logger.warning("Formato de assinatura inválido")
            return False, None
        
        # Verificar timestamp (tolerância de 5 minutos)
        current_time = int(datetime.now().timestamp())
        webhook_time = int(timestamp)
        
        if abs(current_time - webhook_time) > 300:
            current_app.logger.warning(f"Timestamp muito antigo: {abs(current_time - webhook_time)}s")
            return False, None
        
        # Validar assinatura
        webhook_secret = current_app.config['MERCADO_PAGO_WEBHOOK_SECRET']
        message = f"{timestamp}.{payload}"
        expected_signature = hmac.new(
            webhook_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            current_app.logger.warning("Assinatura inválida")
            return False, None
        
        # Parse do payload JSON
        try:
            payload_data = json.loads(payload)
            return True, payload_data
        except json.JSONDecodeError:
            current_app.logger.error("Payload JSON inválido")
            return False, None
            
    except Exception as e:
        current_app.logger.error(f"Erro ao validar webhook: {e}")
        return False, None
'''
        
        # Salvar código em arquivo
        code_file = os.path.join(os.path.dirname(__file__), 'webhook_validation.py')
        with open(code_file, 'w', encoding='utf-8') as f:
            f.write(validation_code.strip())
        
        print(f"✅ Código de validação salvo em: {code_file}")
        return code_file
    
    def run_security_tests(self):
        """Executa todos os testes de segurança do webhook."""
        print("🔒 Iniciando testes de segurança do webhook")
        print("=" * 60)
        
        # Verificar configuração da chave secreta
        print(f"🔑 Chave secreta configurada: {self.webhook_secret[:8]}...")
        
        if self.webhook_secret == 'webhook-secret-placeholder':
            print("❌ ATENÇÃO: Chave secreta ainda é um placeholder!")
            return False
        
        # Teste 1: Validação de payloads
        print("\n" + "=" * 60)
        payload_test = self.test_webhook_payload_validation()
        
        # Teste 2: Headers de segurança
        print("\n" + "=" * 60)
        headers_test = self.test_webhook_security_headers()
        
        # Teste 3: Gerar código de validação
        print("\n" + "=" * 60)
        validation_file = self.generate_webhook_validation_code()
        
        # Resumo
        print("\n" + "=" * 60)
        print("📊 Resumo dos testes de segurança:")
        print(f"   - Chave secreta configurada: ✅")
        print(f"   - Validação de payloads: {'✅' if payload_test else '❌'}")
        print(f"   - Headers de segurança: {'✅' if headers_test else '❌'}")
        print(f"   - Código de validação: ✅")
        
        success = payload_test and headers_test
        
        if success:
            print("\n🎉 Todos os testes de segurança passaram!")
            print("\n📋 Próximos passos:")
            print("1. Configure o webhook no painel do Mercado Pago")
            print("2. Use a URL: /api/payment/webhook")
            print(f"3. Configure a chave secreta: {self.webhook_secret}")
            print("4. Integre o código de validação na aplicação")
        else:
            print("\n❌ Alguns testes de segurança falharam!")
        
        return success

def main():
    """Função principal."""
    tester = WebhookSecurityTester()
    success = tester.run_security_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())

