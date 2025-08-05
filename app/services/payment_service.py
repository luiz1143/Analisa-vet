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
            current_app.logger.info(f"Webhook recebido: {json.dumps(notification_data, indent=2)}")
            
            # Verificar se é uma notificação de pagamento
            notification_type = notification_data.get("type")
            if notification_type not in ["payment", "merchant_order"]:
                current_app.logger.info(f"Notificação ignorada - tipo: {notification_type}")
                return True, f"Notificação ignorada (tipo: {notification_type})"
            
            # Extrair ID do pagamento
            payment_id = None
            if notification_type == "payment":
                payment_id = notification_data.get("data", {}).get("id")
            elif notification_type == "merchant_order":
                # Para merchant_order, precisamos buscar os pagamentos associados
                order_id = notification_data.get("data", {}).get("id")
                if order_id:
                    payment_id = PaymentService._get_payment_from_order(order_id)
            
            if not payment_id:
                current_app.logger.error("ID do pagamento não encontrado na notificação")
                return False, "ID do pagamento não encontrado"
            
            current_app.logger.info(f"Processando pagamento ID: {payment_id}")
            
            # Buscar detalhes do pagamento
            headers = {
                "Authorization": f"Bearer {current_app.config['MERCADO_PAGO_ACCESS_TOKEN']}"
            }
            
            response = requests.get(
                f"https://api.mercadopago.com/v1/payments/{payment_id}",
                headers=headers
            )
            
            current_app.logger.info(f"Resposta da API do MP - Status: {response.status_code}")
            
            if response.status_code != 200:
                current_app.logger.error(f"Erro ao buscar pagamento: {response.text}")
                return False, f"Erro ao buscar pagamento: {response.text}"
            
            payment_data = response.json()
            current_app.logger.info(f"Dados do pagamento: {json.dumps(payment_data, indent=2)}")
            
            # Verificar se o pagamento foi aprovado
            payment_status = payment_data.get("status")
            current_app.logger.info(f"Status do pagamento: {payment_status}")
            
            if payment_status == "approved":
                current_app.logger.info("Pagamento aprovado - processando...")
                return PaymentService._process_approved_payment(payment_data)
            else:
                current_app.logger.info(f"Pagamento não aprovado - status: {payment_status}")
                return True, f"Pagamento com status: {payment_status}"
            
        except Exception as e:
            current_app.logger.error(f"Erro ao processar webhook: {str(e)}", exc_info=True)
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
            payment_id = payment_data.get("id")
            external_reference = payment_data.get("external_reference")
            
            current_app.logger.info(f"Processando pagamento aprovado - ID: {payment_id}, Ref: {external_reference}")
            
            if not external_reference:
                current_app.logger.error("Referência externa não encontrada no pagamento")
                return False, "Referência externa não encontrada"
            
            # Extrair dados da referência externa (formato: user_id_package_id_timestamp)
            parts = external_reference.split("_")
            if len(parts) < 3:
                current_app.logger.error(f"Formato de referência externa inválido: {external_reference}")
                return False, "Formato de referência externa inválido"
            
            user_id = int(parts[0])
            package_id = parts[1]
            
            current_app.logger.info(f"Extraído - User ID: {user_id}, Package ID: {package_id}")
            
            # Verificar se o pagamento já foi processado (evitar duplicatas)
            from ..models.models import Transaction
            existing_transaction = Transaction.query.filter_by(
                payment_id=str(payment_id),
                status='completed'
            ).first()
            
            if existing_transaction:
                current_app.logger.warning(f"Pagamento {payment_id} já foi processado anteriormente")
                return True, f"Pagamento já processado anteriormente"
            
            # Verificar usuário
            user = User.query.get(user_id)
            if not user:
                current_app.logger.error(f"Usuário {user_id} não encontrado")
                return False, "Usuário não encontrado"
            
            current_app.logger.info(f"Usuário encontrado: {user.email}")
            
            # Verificar pacote
            packages = current_app.config['PACOTES_CREDITOS']
            if package_id not in packages:
                current_app.logger.error(f"Pacote {package_id} inválido")
                return False, "Pacote inválido"
            
            package = packages[package_id]
            current_app.logger.info(f"Pacote encontrado: {package}")
            
            # Registrar transação
            transaction = Transaction(
                user_id=user_id,
                payment_id=str(payment_id),
                package_id=package_id,
                credits=package['creditos'],
                amount=package['preco'],
                status='completed'
            )
            
            # Adicionar créditos ao usuário
            credits_before = user.credits
            user.add_credits(package['creditos'])
            credits_after = user.credits
            
            # Salvar no banco
            db.session.add(transaction)
            db.session.commit()
            
            current_app.logger.info(f"Créditos adicionados com sucesso - Antes: {credits_before}, Depois: {credits_after}, Adicionados: {package['creditos']}")
            
            return True, f"Créditos adicionados: {package['creditos']} para usuário {user.email}"
            
        except Exception as e:
            current_app.logger.error(f"Erro ao processar pagamento aprovado: {str(e)}", exc_info=True)
            db.session.rollback()
            return False, f"Erro ao processar pagamento aprovado: {str(e)}"
    
    @staticmethod
    def _get_payment_from_order(order_id):
        """
        Busca o ID do pagamento a partir de uma merchant_order.
        
        Args:
            order_id: ID da merchant order
            
        Returns:
            ID do pagamento ou None
        """
        try:
            headers = {
                "Authorization": f"Bearer {current_app.config['MERCADO_PAGO_ACCESS_TOKEN']}"
            }
            
            response = requests.get(
                f"https://api.mercadopago.com/merchant_orders/{order_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                order_data = response.json()
                payments = order_data.get("payments", [])
                if payments:
                    return payments[0].get("id")
            
            return None
            
        except Exception as e:
            current_app.logger.error(f"Erro ao buscar pagamento da order {order_id}: {str(e)}")
            return None
    
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

