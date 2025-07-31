"""
Rotas de pagamento para o aplicativo AnalisaVet.
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from flask_login import login_required, current_user
from ..services.payment_service import PaymentService
import json

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/api/payment/packages', methods=['GET'])
def get_packages():
    """Rota para obter pacotes de créditos disponíveis."""
    try:
        packages = PaymentService.get_available_packages()
        return jsonify({
            'success': True,
            'data': packages
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro ao obter pacotes: {str(e)}'
        }), 500

@payment_bp.route("/api/payment/create-preference", methods=["POST"])
@login_required
def create_payment_preference():
    """Rota para criar preferência de pagamento."""
    try:
        data = request.json
        package_id = data.get("package_id")
        
        if not package_id:
            return jsonify({
                "success": False,
                "error": "ID do pacote é obrigatório."
            }), 400
        
        success, result = PaymentService.create_payment_preference(
            current_user.id, package_id
        )
        
        if success:
            return jsonify({
                "success": True,
                "data": result
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": result
            }), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Erro interno: {str(e)}"
        }), 500

@payment_bp.route('/api/payment/webhook', methods=['POST'])
def payment_webhook():
    """Rota para receber notificações do Mercado Pago."""
    try:
        # Verificar assinatura (se configurada)
        signature = request.headers.get('x-signature')
        if signature:
            if not PaymentService.verify_webhook_signature(request.data, signature):
                return jsonify({'error': 'Assinatura inválida'}), 401
        
        notification_data = request.json
        success, message = PaymentService.process_webhook_notification(notification_data)
        
        if success:
            return jsonify({'status': 'ok', 'message': message}), 200
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@payment_bp.route('/api/payment/status/<payment_id>', methods=['GET'])
@login_required
def get_payment_status(payment_id):
    """Rota para consultar status de um pagamento."""
    try:
        success, result = PaymentService.get_payment_status(payment_id)
        
        if success:
            return jsonify({
                'success': True,
                'data': result
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

# Rotas de retorno do Mercado Pago
@payment_bp.route('/payment/success')
def payment_success():
    """Página de sucesso do pagamento."""
    return render_template('payment/success.html')

@payment_bp.route('/payment/failure')
def payment_failure():
    """Página de falha do pagamento."""
    return render_template('payment/failure.html')

@payment_bp.route('/payment/pending')
def payment_pending():
    """Página de pagamento pendente."""
    return render_template('payment/pending.html')

@payment_bp.route('/comprar-creditos')
def buy_credits_page():
    """Página para compra de créditos."""
    packages = PaymentService.get_available_packages()
    return render_template("payment/buy_credits.html", packages=packages, current_user=current_user)
