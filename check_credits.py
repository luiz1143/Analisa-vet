import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from app import create_app
from models.models import db, User

app = create_app()

with app.app_context():
    user = User.query.filter_by(email='teste@clinicavet.com').first()

    if user:
        print(f"Créditos atuais para o usuário {user.email}: {user.credits}")
    else:
        print("Usuário teste@clinicavet.com não encontrado.")


