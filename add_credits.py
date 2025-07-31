import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app import create_app
from models.models import db, User

app = create_app()

with app.app_context():
    users_to_update = ['luizqsinclusao@gmail.com', 'teste@clinicavet.com']
    credits_to_add = 1000000

    for email in users_to_update:
        user = User.query.filter_by(email=email).first()
        if user:
            user.credits += credits_to_add
            db.session.commit()
            print(f'Créditos adicionados a {email}. Novo saldo: {user.credits}')
        else:
            print(f'Usuário {email} não encontrado.')


