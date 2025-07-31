#!/usr/bin/env python3
"""
Script para criar a tabela de transações no banco de dados.
"""

import os
import sqlite3
from datetime import datetime

def create_transactions_table():
    """Cria a tabela de transações no banco de dados."""
    db_path = os.path.join(os.path.dirname(__file__), 'app', 'instance', 'analisavet.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Criar tabela de transações
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type VARCHAR(50) NOT NULL,
                amount DECIMAL(10, 2),
                credits INTEGER,
                description TEXT,
                payment_id VARCHAR(100),
                status VARCHAR(20) DEFAULT 'pending',
                created_at DATETIME NOT NULL,
                updated_at DATETIME,
                FOREIGN KEY(user_id) REFERENCES users (id)
            )
        """)
        
        # Criar índices para melhor performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_transactions_payment_id ON transactions(payment_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at)
        """)
        
        conn.commit()
        print("✅ Tabela 'transactions' criada com sucesso!")
        
        # Verificar se a tabela foi criada
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transactions'")
        result = cursor.fetchone()
        
        if result:
            print("✅ Tabela 'transactions' confirmada no banco de dados")
            
            # Mostrar estrutura da tabela
            cursor.execute("PRAGMA table_info(transactions)")
            columns = cursor.fetchall()
            
            print("\n📋 Estrutura da tabela 'transactions':")
            for column in columns:
                print(f"   - {column[1]} ({column[2]})")
        else:
            print("❌ Erro: Tabela 'transactions' não foi encontrada")
            
    except Exception as e:
        print(f"❌ Erro ao criar tabela: {e}")
    finally:
        if conn:
            conn.close()

def create_payments_table():
    """Cria a tabela de pagamentos no banco de dados."""
    db_path = os.path.join(os.path.dirname(__file__), 'app', 'instance', 'analisavet.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Criar tabela de pagamentos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                mercadopago_id VARCHAR(100) UNIQUE,
                preference_id VARCHAR(100),
                status VARCHAR(20) DEFAULT 'pending',
                amount DECIMAL(10, 2) NOT NULL,
                credits INTEGER NOT NULL,
                package_id VARCHAR(10),
                payer_email VARCHAR(120),
                payment_method VARCHAR(50),
                created_at DATETIME NOT NULL,
                updated_at DATETIME,
                approved_at DATETIME,
                FOREIGN KEY(user_id) REFERENCES users (id)
            )
        """)
        
        # Criar índices
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_payments_mercadopago_id ON payments(mercadopago_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status)
        """)
        
        conn.commit()
        print("✅ Tabela 'payments' criada com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao criar tabela de pagamentos: {e}")
    finally:
        if conn:
            conn.close()

def main():
    """Função principal."""
    print("🔧 Criando tabelas necessárias para o sistema de pagamentos...")
    print("=" * 60)
    
    # Criar tabela de transações
    create_transactions_table()
    
    print("\n" + "=" * 60)
    
    # Criar tabela de pagamentos
    create_payments_table()
    
    print("\n✅ Todas as tabelas foram criadas com sucesso!")

if __name__ == "__main__":
    main()

