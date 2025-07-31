#!/usr/bin/env python3
"""
Script para gerar uma chave secreta forte para o webhook do Mercado Pago.
"""

import secrets
import string

def generate_webhook_secret(length=32):
    """
    Gera uma chave secreta forte para o webhook.
    
    Args:
        length (int): Comprimento da chave secreta (padrão: 32)
    
    Returns:
        str: Chave secreta gerada
    """
    # Usar caracteres alfanuméricos e alguns símbolos seguros
    alphabet = string.ascii_letters + string.digits + '-_'
    secret = ''.join(secrets.choice(alphabet) for _ in range(length))
    return secret

if __name__ == "__main__":
    # Gerar chave secreta
    webhook_secret = generate_webhook_secret()
    
    print("Chave secreta gerada para o webhook do Mercado Pago:")
    print(f"MERCADO_PAGO_WEBHOOK_SECRET={webhook_secret}")
    print()
    print("Instruções:")
    print("1. Copie a chave secreta acima")
    print("2. Configure esta chave no painel do Mercado Pago")
    print("3. Atualize a variável MERCADO_PAGO_WEBHOOK_SECRET no config.py")
    print("4. Configure o webhook para apontar para: /api/payment/webhook")

