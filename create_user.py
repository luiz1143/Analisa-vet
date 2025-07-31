import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from app import create_app, db
from models.models import User

app = create_app("development")

with app.app_context():
    # Criar um usuário de teste
    email = "test@example.com"
    password = "password123"
    
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print(f"Usuário {email} criado com sucesso.")
    else:
        print(f"Usuário {email} já existe.")

    # Adicionar créditos ao usuário (opcional, para testes)
    user.add_credits(10) # Adiciona 10 créditos
    db.session.commit()
    print(f"10 créditos adicionados ao usuário {email}.")


