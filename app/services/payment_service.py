"""
Serviço de pagamento para o aplicativo AnalisaVet.
Integração com Mercado Pago para compra de créditos.
"""

import requests
import json
import hashlib
import hmac
from datetime import datetime
from flask import current_app
from ..models.models import User, db

class PaymentService:
    """Serviço para gerenciar pagamentos via Mercado Pago."""
    
    @staticmethod
    def create_payment_preference(user_id, package_id):
        """
        Cria uma preferência de pagamento no Mercado Pago.
        
        Args:
            user_id: ID do usuário
            package_id: ID do pacote de créditos
            
        Returns:
            Tupla (sucesso, dados_resposta_ou_erro)
        """
        try:
            # Verificar se o usuário existe
            user = User.query.get(user_id)
            if not user:
                return False, "Usuário não encontrado."
            
            # Verificar se o pacote existe
            packages = current_app.config['PACOTES_CREDITOS']
            if package_id not in packages:
                return False, "Pacote de créditos inválido."
            
            package = packages[package_id]
            
            # Obter URL base da configuração
            base_url = current_app.config.get('BASE_URL', 'https://5000-irptf51rfmrza92v5jgs9-6b0cb216.manus.computer')
            
            # Dados da preferência
            preference_data = {
                "items": [
                    {
                        "title": f"AnalisaVet - {package['descricao']}",
                        "description": f"Compra de {package['creditos']} créditos para análises de hemograma",
                        "quantity": 1,
                        "currency_id": "BRL",
                        "unit_price": package['preco']
                    }
                ],
                "payer": {
                    "email": user.email
                },
                "back_urls": {
                    "success": f"{base_url}/payment/success",
                    "failure": f"{base_url}/payment/failure",
                    "pending": f"{base_url}/payment/pending"
                },
                "auto_return": "approved",
                "external_reference": f"{user_id}_{package_id}_{int(datetime.now().timestamp())}",
                "notification_url": f"{base_url}/api/payment/webhook"
            }
            
            # Headers para a requisição
            headers = {
                "Authorization": f"Bearer {current_app.config['MERCADO_PAGO_ACCESS_TOKEN']}",
                "Content-Type": "application/json"
            }
            
            # Fazer requisição para o Mercado Pago
            response = requests.post(
                "https://api.mercadopago.com/checkout/preferences",
                headers=headers,
                           data=json.dumps(preference_data)
            )
            if response.status_code == 201:
                preference = response.json()
                return True, {
                    "preference_id": preference["id"],
                    "init_point": preference["init_point"],
                    "sandbox_init_point": preference.get("sandbox_init_point")
                }
            else:
                current_app.logger.error(f"Erro ao criar preferência no Mercado Pago: Status {response.status_code}, Resposta: {response.text}")
                return False, f"Erro ao criar preferência: {response.text}"
                
        except Exception as e:
            return False, f"Erro interno: {str(e)}"
    
    @staticmethod
    def process_webhook_notification(notification_data):
        """
        Processa notificação de webhook do Mercado Pago.
        
        Args:
            notification_data: Dados da notificação
            
        Returns:
            Tupla (sucesso, mensagem)
        """
        try:
            # Verificar se é uma notificação de pagamento
            if notification_data.get("type") != "payment":
                return True, "Notificação ignorada (não é pagamento)"
            
            payment_id = notification_data.get("data", {}).get("id")
            if not payment_id:
                return False, "ID do pagamento não encontrado"
            
            # Buscar detalhes do pagamento
            headers = {
                "Authorization": f"Bearer {current_app.config['MERCADO_PAGO_ACCESS_TOKEN']}"
            }
            
            response = requests.get(
                f"https://api.mercadopago.com/v1/payments/{payment_id}",
                headers=headers
            )
            
            if response.status_code != 200:
                return False, f"Erro ao buscar pagamento: {response.text}"
            
            payment_data = response.json()
            
            # Verificar se o pagamento foi aprovado
            if payment_data.get("status") == "approved":
                return PaymentService._process_approved_payment(payment_data)
            
            return True, f"Pagamento com status: {payment_data.get('status')}"
            
        except Exception as e:
            return False, f"Erro ao processar webhook: {str(e)}"
    
    @staticmethod
    def _process_approved_payment(payment_data):
        """
        Processa um pagamento aprovado, adicionando créditos ao usuário.
        
        Args:
            payment_data: Dados do pagamento aprovado
            
        Returns:
            Tupla (sucesso, mensagem)
        """
        try:
            external_reference = payment_data.get("external_reference")
            if not external_reference:
                return False, "Referência externa não encontrada"
            
            # Extrair dados da referência externa (formato: user_id_package_id_timestamp)
            parts = external_reference.split("_")
            if len(parts) < 3:
                return False, "Formato de referência externa inválido"
            
            user_id = int(parts[0])
            package_id = parts[1]
            
            # Verificar usuário
            user = User.query.get(user_id)
            if not user:
                return False, "Usuário não encontrado"
            
            # Verificar pacote
            packages = current_app.config['PACOTES_CREDITOS']
            if package_id not in packages:
                return False, "Pacote inválido"
            
            package = packages[package_id]
            
            # Adicionar créditos ao usuário
            user.add_credits(package['creditos'])
            db.session.commit()
            
            return True, f"Créditos adicionados: {package['creditos']} para usuário {user.email}"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Erro ao processar pagamento aprovado: {str(e)}"
    
    @staticmethod
    def verify_webhook_signature(request_data, signature):
        """
        Verifica a assinatura do webhook do Mercado Pago.
        
        Args:
            request_data: Dados da requisição
            signature: Assinatura recebida
            
        Returns:
            Boolean indicando se a assinatura é válida
        """
        try:
            secret = current_app.config['MERCADO_PAGO_WEBHOOK_SECRET']
            expected_signature = hmac.new(
                secret.encode('utf-8'),
                request_data,
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
        except Exception:
            return False
    
    @staticmethod
    def get_available_packages():
        """
        Retorna os pacotes de créditos disponíveis.
        
        Returns:
            Dicionário com os pacotes disponíveis
        """
        return current_app.config['PACOTES_CREDITOS']
    
    @staticmethod
    def get_payment_status(payment_id):
        """
        Consulta o status de um pagamento no Mercado Pago.
        
        Args:
            payment_id: ID do pagamento
            
        Returns:
            Tupla (sucesso, dados_do_pagamento_ou_erro)
        """
        try:
            headers = {
                "Authorization": f"Bearer {current_app.config['MERCADO_PAGO_ACCESS_TOKEN']}"
            }
            
            response = requests.get(
                f"https://api.mercadopago.com/v1/payments/{payment_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, f"Erro ao consultar pagamento: {response.text}"
                
        except Exception as e:
            return False, f"Erro interno: {str(e)}"

