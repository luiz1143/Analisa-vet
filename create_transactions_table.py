#!/usr/bin/env python3
"""
Script para criar a tabela de transações no banco de dados.
"""

import sys
import os

# Adicionar o diretório do projeto ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'analisavet/analisavet_render_ready/analisavet_project'))

from app.app import create_app
from app.models.models import db, Transaction

def create_transactions_table():
    """Cria a tabela de transações no banco de dados."""
    app = create_app()
    
    with app.app_context():
        try:
            # Criar a tabela de transações
            db.create_all()
            print("✅ Tabela de transações criada com sucesso!")
            
            # Verificar se a tabela foi criada
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'transactions' in tables:
                print("✅ Tabela 'transactions' confirmada no banco de dados")
                
                # Mostrar colunas da tabela
                columns = inspector.get_columns('transactions')
                print("\n📋 Colunas da tabela 'transactions':")
                for column in columns:
                    print(f"  - {column['name']}: {column['type']}")
            else:
                print("❌ Tabela 'transactions' não foi encontrada")
                
        except Exception as e:
            print(f"❌ Erro ao criar tabela: {str(e)}")

if __name__ == "__main__":
    create_transactions_table()

