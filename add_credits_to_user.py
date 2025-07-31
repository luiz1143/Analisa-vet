import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from app import create_app
from models.models import db, User

app = create_app()

with app.app_context():
    user = User.query.filter_by(email='luizqsinclusao@gmail.com').first()

    if user:
        user.credits += 10000000  # Adiciona 10 milhões de créditos
        db.session.commit()
        print(f"Créditos atualizados para o usuário {user.email}: {user.credits}")
    else:
        print("Usuário luizqsinclusao@gmail.com não encontrado. Criando novo usuário com 10 milhões de créditos.")
        user = User(email='luizqsinclusao@gmail.com')
        user.set_password('initial_password') # Definir uma senha inicial, pode ser alterada depois
        user.credits = 10000000
        db.session.add(user)
        db.session.commit()
        print(f"Novo usuário luizqsinclusao@gmail.com criado com {user.credits} créditos.")


