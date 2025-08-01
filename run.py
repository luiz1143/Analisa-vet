#!/usr/bin/env python3
"""
Arquivo principal para execução da aplicação AnalisaVet em produção.
"""

import os
from app.app import create_app

# Determinar o ambiente baseado na variável de ambiente
config_name = os.environ.get("FLASK_ENV", "production")

# Criar a aplicação
app = create_app(config_name)

if __name__ == "__main__":
    # Para desenvolvimento local
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)


