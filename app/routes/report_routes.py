"""
Rotas de laudos para o aplicativo AnalisaVet.
"""

from flask import Blueprint, request, jsonify, send_file, current_app
from flask_login import login_required, current_user
from ..services.report_service import ReportService
from ..models.models import Analysis, User
import os
import tempfile

report_bp = Blueprint("report", __name__)

@report_bp.route("/api/reports/technical/<int:analysis_id>", methods=["GET"])
@login_required
def generate_technical_report(analysis_id):
    """Rota para gerar laudo técnico."""
    # Verificar se a análise existe e pertence ao usuário
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=current_user.id).first()
    
    if not analysis:
        return jsonify({
            "success": False,
            "error": "Análise não encontrada ou sem permissão para acessá-la."
        }), 404
    
    # Obter dados da análise
    analysis_data = analysis.get_analysis_result()
    
    # Obter informações do paciente
    patient_info = analysis.get_patient_info()
    
    # Obter informações da clínica
    clinic_info = current_user.get_clinic_info()
    
    # Adicionar caminho do logo ao clinic_info, se existir
    if current_user.clinic_logo_path:
        clinic_info["logo_path"] = current_user.clinic_logo_path
    
    print(f"*** Debug: clinic_info antes de passar para o ReportService (Technical): {clinic_info}")

    # Gerar laudo
    pdf_path = ReportService.generate_technical_report(
        analysis_data, patient_info, clinic_info)
    
    if not pdf_path:
        return jsonify({
            "success": False,
            "error": "Erro ao gerar laudo técnico."
        }), 500
    
    # Enviar arquivo
    try:
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"laudo_tecnico_{analysis_id}.pdf",
            mimetype="application/pdf"
        )
    finally:
        # Remover arquivo temporário após envio
        os.unlink(pdf_path)

@report_bp.route("/api/reports/simplified/<int:analysis_id>", methods=["GET"])
@login_required
def generate_simplified_report(analysis_id):
    """Rota para gerar laudo simplificado para tutores."""
    # Verificar se a análise existe e pertence ao usuário
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=current_user.id).first()
    
    if not analysis:
        return jsonify({
            "success": False,
            "error": "Análise não encontrada ou sem permissão para acessá-la."
        }), 404
    
    # Obter dados da análise
    analysis_data = analysis.get_analysis_result()
    
    # Obter informações do paciente
    patient_info = analysis.get_patient_info()
    
    # Obter informações da clínica
    clinic_info = current_user.get_clinic_info()
    
    # Adicionar caminho do logo ao clinic_info, se existir
    if current_user.clinic_logo_path:
        clinic_info["logo_path"] = current_user.clinic_logo_path
    
    print(f"*** Debug: clinic_info antes de passar para o ReportService (Simplified): {clinic_info}")

    # Gerar laudo
    pdf_path = ReportService.generate_simplified_report(
        analysis_data, patient_info, clinic_info)
    
    if not pdf_path:
        return jsonify({
            "success": False,
            "error": "Erro ao gerar laudo simplificado."
        }), 500
    
    # Enviar arquivo
    try:
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"laudo_simplificado_{analysis_id}.pdf",
            mimetype="application/pdf"
        )
    finally:
        # Remover arquivo temporário após envio
        os.unlink(pdf_path)




