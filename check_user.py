import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from app import create_app
from models.models import db, User

app = create_app()

if len(sys.argv) != 2:
    print("Uso: python3 check_user.py <email>")
    sys.exit(1)

email = sys.argv[1]

with app.app_context():
    user = User.query.filter_by(email=email).first()

    if user:
        print(f"Usuário encontrado: {user.email}")
        print(f"Créditos atuais: {user.credits}")
        print(f"ID: {user.id}")
    else:
        print(f"Usuário {email} não encontrado.")

