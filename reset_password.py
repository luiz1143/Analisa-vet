import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from app import create_app
from models.models import db, User
from werkzeug.security import generate_password_hash

app = create_app()

if len(sys.argv) != 3:
    print("Uso: python3 reset_password.py <email> <nova_senha>")
    sys.exit(1)

email = sys.argv[1]
nova_senha = sys.argv[2]

with app.app_context():
    user = User.query.filter_by(email=email).first()

    if user:
        user.password_hash = generate_password_hash(nova_senha)
        db.session.commit()
        print(f"Senha do usuário {email} redefinida com sucesso para: {nova_senha}")
    else:
        print(f"Usuário {email} não encontrado.")

