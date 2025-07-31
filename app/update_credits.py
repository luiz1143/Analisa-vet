"""
Script para listar e atualizar créditos dos usuários no sistema AnalisaVet.
"""

from app import create_app
from models.models import db, User

def main():
    """Função principal para listar e atualizar créditos dos usuários."""
    app = create_app()
    
    with app.app_context():
        # Listar todos os usuários
        print("Usuários encontrados:")
        users = User.query.all()
        
        if not users:
            print("Nenhum usuário encontrado no banco de dados.")
            return
        
        for user in users:
            print(f"ID: {user.id}, Email: {user.email}, Créditos: {user.credits}")
        
        # Atualizar créditos para 1 milhão para todos os usuários
        for user in users:
            user.credits = 1000000
            db.session.commit()
            print(f"Usuário {user.email} atualizado para 1.000.000 créditos.")
        
        # Verificar atualização
        print("\nVerificando atualização:")
        users = User.query.all()
        for user in users:
            print(f"ID: {user.id}, Email: {user.email}, Créditos: {user.credits}")

if __name__ == "__main__":
    main()
