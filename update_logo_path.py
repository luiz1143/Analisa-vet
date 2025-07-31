import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from app import create_app
from models.models import db, User

app = create_app()

with app.app_context():
    # Encontre o usuário de teste
    user = User.query.filter_by(email='teste@clinicavet.com').first()

    if user:
        user.clinic_logo_path = 'uploads/una.jpg'
        db.session.commit()
        print(f"Logo path atualizado para a clínica do usuário {user.email}: {user.clinic_logo_path}")
    else:
        print("Usuário teste@clinicavet.com não encontrado.")

    # Encontre o usuário luizqsinclusao@gmail.com
    user_luiz = User.query.filter_by(email='luizqsinclusao@gmail.com').first()

    if user_luiz:
        user_luiz.clinic_logo_path = 'uploads/una.jpg'
        db.session.commit()
        print(f"Logo path atualizado para a clínica do usuário {user_luiz.email}: {user_luiz.clinic_logo_path}")
    else:
        print("Usuário luizqsinclusao@gmail.com não encontrado.")


