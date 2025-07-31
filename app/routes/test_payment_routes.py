"""
Rotas de teste para pagamento sem dependência da API do Mercado Pago.
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models.models import db, User
from datetime import datetime
import json

test_payment_bp = Blueprint('test_payment', __name__)

@test_payment_bp.route('/test-payment/packages', methods=['GET'])
def get_test_packages():
    """Rota para obter pacotes de créditos disponíveis (teste)."""
    try:
        packages = {
            '1': {'creditos': 1, 'preco': 2.00, 'descricao': '1 crédito'},
            '10': {'creditos': 10, 'preco': 18.00, 'descricao': '10 créditos (10% desconto)'},
            '25': {'creditos': 25, 'preco': 45.00, 'descricao': '25 créditos (10% desconto)'},
            '50': {'creditos': 50, 'preco': 80.00, 'descricao': '50 créditos (20% desconto)'},
            '100': {'creditos': 100, 'preco': 140.00, 'descricao': '100 créditos (30% desconto)'}
        }
        return jsonify({
            'success': True,
            'data': packages
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro ao obter pacotes: {str(e)}'
        }), 500

@test_payment_bp.route("/test-payment/simulate", methods=["POST"])
@login_required
def simulate_payment():
    """Rota para simular um pagamento (teste)."""
    try:
        data = request.json
        package_id = data.get("package_id")
        
        if not package_id:
            return jsonify({
                "success": False,
                "error": "ID do pacote é obrigatório."
            }), 400
        
        packages = {
            '1': {'creditos': 1, 'preco': 2.00, 'descricao': '1 crédito'},
            '10': {'creditos': 10, 'preco': 18.00, 'descricao': '10 créditos (10% desconto)'},
            '25': {'creditos': 25, 'preco': 45.00, 'descricao': '25 créditos (10% desconto)'},
            '50': {'creditos': 50, 'preco': 80.00, 'descricao': '50 créditos (20% desconto)'},
            '100': {'creditos': 100, 'preco': 140.00, 'descricao': '100 créditos (30% desconto)'}
        }
        
        if package_id not in packages:
            return jsonify({
                "success": False,
                "error": "Pacote de créditos inválido."
            }), 400
        
        package = packages[package_id]
        
        # Simular pagamento aprovado - adicionar créditos diretamente
        try:
            current_user.credits = (current_user.credits or 0) + package['creditos']
            db.session.commit()
            
            return jsonify({
                "success": True,
                "message": f"Pagamento simulado com sucesso! {package['creditos']} créditos adicionados.",
                "data": {
                    "credits_added": package['creditos'],
                    "total_credits": current_user.credits,
                    "package_description": package['descricao'],
                    "amount_paid": package['preco']
                }
            }), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "success": False,
                "error": f"Erro ao adicionar créditos: {str(e)}"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Erro interno: {str(e)}"
        }), 500

@test_payment_bp.route("/test-buy-credits-page", methods=["GET", "POST"])
@login_required
def test_buy_credits_page():
    """Página de teste para compra de créditos."""
    packages = {
        '1': {'creditos': 1, 'preco': 2.00, 'descricao': '1 crédito'},
        '10': {'creditos': 10, 'preco': 18.00, 'descricao': '10 créditos (10% desconto)'},
        '25': {'creditos': 25, 'preco': 45.00, 'descricao': '25 créditos (10% desconto)'},
        '50': {'creditos': 50, 'preco': 80.00, 'descricao': '50 créditos (20% desconto)'},
        '100': {'creditos': 100, 'preco': 140.00, 'descricao': '100 créditos (30% desconto)'}
    }
    return render_template("payment/test_buy_credits.html", packages=packages, current_user=current_user)

@test_payment_bp.route('/test-payment/success')
def test_payment_success():
    """Página de sucesso do pagamento (teste)."""
    return render_template('payment/success.html')

@test_payment_bp.route('/test-payment/add-credits', methods=['POST'])
@login_required
def add_credits_directly():
    """Adiciona créditos diretamente para teste."""
    try:
        data = request.json
        credits_to_add = data.get('credits', 1)
        
        if not isinstance(credits_to_add, int) or credits_to_add <= 0:
            return jsonify({
                "success": False,
                "error": "Número de créditos inválido."
            }), 400
        
        current_user.credits = (current_user.credits or 0) + credits_to_add
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"{credits_to_add} créditos adicionados com sucesso!",
            "total_credits": current_user.credits
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": f"Erro ao adicionar créditos: {str(e)}"
        }), 500

