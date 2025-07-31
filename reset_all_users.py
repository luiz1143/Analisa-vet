import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from app import create_app
from models.models import db, User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Excluir todos os usuários
    User.query.delete()
    db.session.commit()
    print("Todas as contas foram excluídas.")
    
    # Criar nova conta
    email = "admin@analisavet.com"
    senha = "admin123"
    
    new_user = User(
        email=email,
        password_hash=generate_password_hash(senha),
        credits=1000000  # 1 milhão de créditos
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    print(f"Nova conta criada:")
    print(f"Email: {email}")
    print(f"Senha: {senha}")
    print(f"Créditos: 1,000,000")

