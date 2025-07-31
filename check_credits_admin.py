#!/usr/bin/env python3
"""
Script para verificar os créditos atuais do usuário admin@analisavet.com
"""

import sys
import os

# Adicionar o diretório do app ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app import create_app
from models.models import User

def check_credits():
    """Verifica os créditos atuais do usuário admin."""
    app = create_app()
    
    with app.app_context():
        # Buscar o usuário admin
        user = User.query.filter_by(email='admin@analisavet.com').first()
        
        if not user:
            print("❌ Usuário admin@analisavet.com não encontrado!")
            return
        
        print(f"👤 Usuário: {user.email}")
        print(f"💰 Créditos atuais: {user.credits}")

if __name__ == "__main__":
    check_credits()

