"""
Rotas de autenticação para o aplicativo AnalisaVet.
"""

from flask import Blueprint, request, jsonify, session, current_app, send_from_directory
from flask_login import login_required, current_user
from ..services.auth_service import AuthService
import os
from werkzeug.utils import secure_filename

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/api/auth/register", methods=["POST"])
def register():
    """Rota para registro de novos usuários."""
    data = request.json
    
    if not data or "email" not in data or "password" not in data:
        return jsonify({
            "success": False,
            "error": "Email e senha são obrigatórios."
        }), 400
    
    email = data.get("email")
    password = data.get("password")
    
    success, message, user = AuthService.register_user(email, password)
    
    if success:
        return jsonify({
            "success": True,
            "data": {
                "message": message,
                "user_id": user.id,
                "email": user.email
            }
        }), 201
    else:
        return jsonify({
            "success": False,
            "error": message
        }), 400

@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    """Rota para login de usuários."""
    data = request.json
    
    if not data or "email" not in data or "password" not in data:
        return jsonify({
            "success": False,
            "error": "Email e senha são obrigatórios."
        }), 400
    
    email = data.get("email")
    password = data.get("password")
    
    success, message, user = AuthService.login_user_with_credentials(email, password)
    
    if success:
        return jsonify({
            "success": True,
            "data": {
                "message": message,
                "user_id": user.id,
                "email": user.email,
                "credits": user.credits
            }
        }), 200
    else:
        return jsonify({
            "success": False,
            "error": message
        }), 401

@auth_bp.route("/api/auth/logout", methods=["POST"])
def logout():
    """Rota para logout de usuários."""
    success, message = AuthService.logout_current_user()
    
    if success:
        return jsonify({
            "success": True,
            "data": {
                "message": message
            }
        }), 200
    else:
        return jsonify({
            "success": False,
            "error": message
        }), 500

@auth_bp.route("/api/auth/status", methods=["GET"])
def user_status():
    """Rota para verificar o status do usuário atual."""
    status = AuthService.get_user_status()
    
    return jsonify({
        "success": True,
        "data": status
    }), 200

@auth_bp.route("/api/auth/clinic-info", methods=["PUT"])
@login_required
def update_clinic_info():
    """Rota para atualizar informações da clínica."""
    data = request.json
    
    if not data:
        return jsonify({
            "success": False,
            "error": "Dados da clínica são obrigatórios."
        }), 400
    
    success, message = AuthService.update_clinic_info(current_user.id, data)
    
    if success:
        return jsonify({
            "success": True,
            "data": {
                "message": message
            }
        }), 200
    else:
        return jsonify({
            "success": False,
            "error": message
        }), 400

@auth_bp.route("/api/auth/clinic-logo", methods=["POST"])
@login_required
def update_clinic_logo():
    """Rota para atualizar o logo da clínica."""
    print("*** Início da função update_clinic_logo ***")
    if "logo" not in request.files:
        print("Erro: Nenhum arquivo 'logo' encontrado em request.files")
        return jsonify({
            "success": False,
            "error": "Nenhum arquivo enviado."
        }), 400
    
    logo_file = request.files["logo"]
    print(f"Arquivo recebido: {logo_file.filename}")
    print(f"Tamanho do arquivo: {logo_file.content_length} bytes")
    
    if logo_file.filename == "":
        print("Erro: Nome do arquivo vazio.")
        return jsonify({
            "success": False,
            "error": "Nenhum arquivo selecionado."
        }), 400
    
    if logo_file:
        print(f"Tipo de objeto logo_file: {type(logo_file)}")
        # Verificar extensão
        allowed_extensions = {"png", "jpg", "jpeg", "gif", "svg"}
        if "." not in logo_file.filename or \
           logo_file.filename.rsplit(".", 1)[1].lower() not in allowed_extensions:
            print(f"Erro: Formato de arquivo não permitido: {logo_file.filename.rsplit('.', 1)[1].lower()}")
            return jsonify({
                "success": False,
                "error": "Formato de arquivo não permitido. Use PNG, JPG, JPEG, GIF ou SVG."
            }), 400
        
        # Salvar arquivo
        filename = secure_filename(logo_file.filename)
        logo_dir = os.path.join(current_app.root_path, "static", "uploads")
        print(f"Diretório de destino do logo: {logo_dir}")
        
        # Criar diretório se não existir
        if not os.path.exists(logo_dir):
            print(f"Criando diretório: {logo_dir}")
            os.makedirs(logo_dir)
        
        # Gerar nome único baseado no ID do usuário
        file_ext = filename.rsplit(".", 1)[1].lower()
        unique_filename = f"logo_{current_user.id}.{file_ext}"
        file_path = os.path.join(logo_dir, unique_filename)
        print(f"Caminho completo para salvar o logo: {file_path}")
        
        try:
            logo_file.save(file_path)
            print(f"Logo salvo com sucesso em: {file_path}")
            if os.path.exists(file_path):
                print(f"Verificação: Arquivo existe em {file_path}")
            else:
                print(f"Verificação: Arquivo NÃO existe em {file_path} após save.")
        except Exception as e:
            print(f"Erro ao salvar o logo: {e}")
            return jsonify({
                "success": False,
                "error": f"Erro ao salvar o arquivo do logo: {str(e)}"
            }), 500
        
        # Atualizar caminho no banco de dados
        relative_path = os.path.join("uploads", unique_filename)
        print(f"Caminho relativo para o banco de dados: {relative_path}")
        success, message = AuthService.update_clinic_logo(current_user.id, relative_path)
        
        if success:
            print("Caminho do logo atualizado no banco de dados com sucesso.")
            return jsonify({
                "success": True,
                "data": {
                    "message": message,
                    "logo_path": relative_path
                }
            }), 200
        else:
            print(f"Erro ao atualizar o caminho do logo no banco de dados: {message}")
            return jsonify({
                "success": False,
                "error": message
            }), 500
    
    print("Erro: Condição 'if logo_file' não atendida.")
    return jsonify({
        "success": False,
        "error": "Erro ao processar o arquivo."
    }), 500

@auth_bp.route("/api/auth/clinic-info", methods=["GET"])
@login_required
def get_clinic_info():
    """Rota para obter informações da clínica do usuário atual."""
    clinic_info = current_user.get_clinic_info()
    
    return jsonify({
        "success": True,
        "data": clinic_info
    }), 200

@auth_bp.route("/static/uploads/<filename>")
def serve_logo(filename):
    """Rota para servir arquivos de logo das clínicas."""
    logo_dir = os.path.join(current_app.root_path, "static", "uploads")
    return send_from_directory(logo_dir, filename)





