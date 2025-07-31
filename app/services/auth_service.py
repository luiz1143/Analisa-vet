"""
Serviço de autenticação para o aplicativo AnalisaVet.
"""

from flask_login import login_user, logout_user, current_user
from datetime import datetime
from ..models.models import User, db

class AuthService:
    """Serviço para gerenciar autenticação de usuários."""
    
    @staticmethod
    def register_user(email, password):
        """
        Registra um novo usuário.
        
        Args:
            email: Email do usuário
            password: Senha do usuário
            
        Returns:
            Tupla (sucesso, mensagem, usuário)
        """
        # Verificar se o email já está em uso
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return False, "Este email já está cadastrado.", None
        
        # Criar novo usuário
        try:
            user = User(email=email)
            user.set_password(password)
            user.credits = 5  # Créditos iniciais gratuitos
            
            db.session.add(user)
            db.session.commit()
            
            return True, "Usuário registrado com sucesso.", user
        except Exception as e:
            db.session.rollback()
            return False, f"Erro ao registrar usuário: {str(e)}", None
    
    @staticmethod
    def login_user_with_credentials(email, password):
        """
        Realiza login de um usuário.
        
        Args:
            email: Email do usuário
            password: Senha do usuário
            
        Returns:
            Tupla (sucesso, mensagem, usuário)
        """
        # Buscar usuário pelo email
        user = User.query.filter_by(email=email).first()
        
        # Verificar se o usuário existe e a senha está correta
        if not user or not user.check_password(password):
            return False, "Email ou senha incorretos.", None
        
        # Realizar login
        try:
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            return True, "Login realizado com sucesso.", user
        except Exception as e:
            db.session.rollback()
            return False, f"Erro ao realizar login: {str(e)}", None
    
    @staticmethod
    def logout_current_user():
        """
        Realiza logout do usuário atual.
        
        Returns:
            Tupla (sucesso, mensagem)
        """
        try:
            logout_user()
            return True, "Logout realizado com sucesso."
        except Exception as e:
            return False, f"Erro ao realizar logout: {str(e)}"
    
    @staticmethod
    def get_user_status():
        """
        Obtém o status do usuário atual.
        
        Returns:
            Dicionário com informações do usuário
        """
        if current_user.is_authenticated:
            return {
                "logged_in": True,
                "email": current_user.email,
                "credits": current_user.credits,
                "clinic_info": current_user.get_clinic_info()
            }
        else:
            return {"logged_in": False}
    
    @staticmethod
    def update_clinic_info(user_id, clinic_info):
        """
        Atualiza as informações da clínica de um usuário.
        
        Args:
            user_id: ID do usuário
            clinic_info: Dicionário com informações da clínica
            
        Returns:
            Tupla (sucesso, mensagem)
        """
        user = User.query.get(user_id)
        if not user:
            print(f"AuthService.update_clinic_info: Usuário {user_id} não encontrado.")
            return False, "Usuário não encontrado."
        
        try:
            print(f"AuthService.update_clinic_info: Recebendo clinic_info: {clinic_info}")
            user.clinic_name = clinic_info.get("nome", user.clinic_name)
            user.clinic_address = clinic_info.get("endereco", user.clinic_address)
            user.clinic_phone = clinic_info.get("telefone", user.clinic_phone)
            user.clinic_email = clinic_info.get("email", user.clinic_email)
            user.clinic_crmv = clinic_info.get("crmv", user.clinic_crmv)
            
            db.session.commit()
            print(f"AuthService.update_clinic_info: Informações da clínica atualizadas para: {user.get_clinic_info()}")
            return True, "Informações da clínica atualizadas com sucesso."
        except Exception as e:
            db.session.rollback()
            print(f"AuthService.update_clinic_info: Erro ao atualizar informações da clínica: {str(e)}")
            return False, f"Erro ao atualizar informações da clínica: {str(e)}"
    
    @staticmethod
    def update_clinic_logo(user_id, logo_path):
        """
        Atualiza o logo da clínica de um usuário.
        
        Args:
            user_id: ID do usuário
            logo_path: Caminho para o arquivo de logo
            
        Returns:
            Tupla (sucesso, mensagem)
        """
        user = User.query.get(user_id)
        if not user:
            print(f"AuthService.update_clinic_logo: Usuário {user_id} não encontrado.")
            return False, "Usuário não encontrado."
        
        try:
            print(f"AuthService: Tentando atualizar clinic_logo_path para: {logo_path}")
            user.clinic_logo_path = logo_path
            db.session.commit()
            print(f"AuthService: clinic_logo_path atualizado com sucesso para: {user.clinic_logo_path}")
            return True, "Logo da clínica atualizado com sucesso."
        except Exception as e:
            db.session.rollback()
            print(f"AuthService: Erro ao atualizar logo da clínica no banco de dados: {str(e)}")
            return False, f"Erro ao atualizar logo da clínica: {str(e)}"


