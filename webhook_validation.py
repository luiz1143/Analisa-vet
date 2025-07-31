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