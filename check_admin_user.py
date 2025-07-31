import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from app import create_app
from models.models import db, User

app = create_app()

with app.app_context():
    email = "admin@analisavet.com"
    password = "admin123"
    
    user = User.query.filter_by(email=email).first()
    
    if user:
        print(f"Usuário {email} encontrado.")
        if user.check_password(password):
            print("Senha correta.")
            print(f"Créditos: {user.credits}")
        else:
            print("Senha incorreta.")
    else:
        print(f"Usuário {email} não encontrado.")

