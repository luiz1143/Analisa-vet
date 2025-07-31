"""
Modelos de dados para o aplicativo AnalisaVet.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """Modelo de usuário para autenticação e gerenciamento de créditos."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    credits = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Informações da clínica
    clinic_name = db.Column(db.String(100), default="Clínica Veterinária")
    clinic_address = db.Column(db.String(200), default="Rua Exemplo, 123")
    clinic_phone = db.Column(db.String(20), default="(11) 1234-5678")
    clinic_email = db.Column(db.String(120), default="contato@clinicavet.com")
    clinic_crmv = db.Column(db.String(20), default="CRMV-XX 12345")
    clinic_logo_path = db.Column(db.String(200))
    
    # Relacionamentos
    analyses = db.relationship('Analysis', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """Define a senha do usuário usando hash."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica se a senha está correta."""
        return check_password_hash(self.password_hash, password)
    
    def add_credits(self, amount):
        """Adiciona créditos à conta do usuário."""
        self.credits += amount
        return self.credits
    
    def use_credits(self, amount=1):
        """Utiliza créditos da conta do usuário."""
        if self.credits >= amount:
            self.credits -= amount
            return True
        return False
    
    def get_clinic_info(self):
        """Retorna as informações da clínica como dicionário."""
        return {
            'nome': self.clinic_name,
            'endereco': self.clinic_address,
            'telefone': self.clinic_phone,
            'email': self.clinic_email,
            'crmv': self.clinic_crmv,
            'logo_path': self.clinic_logo_path
        }
    
    def __repr__(self):
        return f'<User {self.email}>'


class Analysis(db.Model):
    """Modelo para armazenar análises de hemograma."""
    __tablename__ = 'analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Dados do paciente
    patient_name = db.Column(db.String(100))
    patient_species = db.Column(db.String(50))
    patient_breed = db.Column(db.String(100))
    patient_age = db.Column(db.String(50))
    patient_gender = db.Column(db.String(20))
    owner_name = db.Column(db.String(100))
    exam_purpose = db.Column(db.String(50))  # Finalidade do exame
    
    # Dados do hemograma (armazenados como JSON)
    hemogram_data = db.Column(db.Text)
    
    # Resultado da análise (armazenado como JSON)
    analysis_result = db.Column(db.Text)
    
    def set_hemogram_data(self, data):
        """Define os dados do hemograma como JSON."""
        self.hemogram_data = json.dumps(data)
    
    def get_hemogram_data(self):
        """Retorna os dados do hemograma como dicionário."""
        return json.loads(self.hemogram_data) if self.hemogram_data else {}
    
    def set_analysis_result(self, result):
        """Define o resultado da análise como JSON."""
        self.analysis_result = json.dumps(result)
    
    def get_analysis_result(self):
        """Retorna o resultado da análise como dicionário."""
        return json.loads(self.analysis_result) if self.analysis_result else {}
    
    def get_patient_info(self):
        """Retorna as informações do paciente como dicionário."""
        return {
            'nome': self.patient_name,
            'especie': self.patient_species,
            'raca': self.patient_breed,
            'idade': self.patient_age,
            'sexo': self.patient_gender,
            'tutor': self.owner_name,
            'finalidade_exame': self.exam_purpose
        }
    
    def __repr__(self):
        return f'<Analysis {self.id} for {self.patient_name}>'
