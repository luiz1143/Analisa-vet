"""
Correção para a rota de valores de referência no backend principal do AnalisaVet.
Esta correção implementa um tratamento robusto para parâmetros acentuados.
"""

from flask import Blueprint, request, jsonify, send_file
from flask_login import login_required, current_user
from ..services.analysis_service import AnalysisService
from ..utils.pdf_parser import processar_arquivo_hemograma
import os
import tempfile
import urllib.parse

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/api/analysis/reference-values', methods=['GET'])
def get_reference_values():
    """Rota para obter valores de referência com tratamento robusto de acentuação."""
    # Obter o parâmetro especie bruto
    especie_raw = request.args.get('especie')
    
    if not especie_raw:
        return jsonify({
            'success': False,
            'error': 'Espécie é obrigatória.'
        }), 400
    
    # Mapeamento direto para garantir que funcione independente da codificação
    especies_map = {
        'Cão': 'Cão',
        'Cao': 'Cão',
        'cao': 'Cão',
        'cão': 'Cão',
        'CÃO': 'Cão',
        'CAO': 'Cão',
        'Gato': 'Gato',
        'gato': 'Gato',
        'GATO': 'Gato',
        # Adicionar variações com possíveis problemas de encoding
        'CÃ£o': 'Cão',
        'CÃƒÂ£o': 'Cão',
        'C\u00c3\u00a3o': 'Cão',
        'C\u00e3o': 'Cão'
    }
    
    # Tentar encontrar a espécie no mapeamento
    especie_normalizada = especies_map.get(especie_raw)
    if not especie_normalizada:
        # Tentar normalizar para minúsculas
        especie_normalizada = especies_map.get(especie_raw.lower())
    
    # Se ainda não encontrou, usar o valor original
    if not especie_normalizada:
        especie_normalizada = especie_raw
    
    valores_ref = AnalysisService.obter_valores_referencia(especie_normalizada)
    
    if not valores_ref:
        # Tentar com valores padrão para Cão como fallback
        valores_ref = AnalysisService.get_reference_values('Cão')
        if valores_ref:
            # Formatar valores de referência para exibição
            formatted_values = {}
            for param, info in valores_ref.items():
                formatted_values[param] = f"{info['min']}-{info['max']} {info['unidade']}"
            
            return jsonify({
                'success': True,
                'data': formatted_values,
                'note': f'Espécie não reconhecida: "{especie_raw}". Usando valores padrão para Cão.'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'Espécie inválida: {especie_raw}. Use "Cão" ou "Gato".'
            }), 400
    
    # Formatar valores de referência para exibição
    formatted_values = {}
    for param, info in valores_ref.items():
        formatted_values[param] = f"{info['min']}-{info['max']} {info['unidade']}"
    
    return jsonify({
        'success': True,
        'data': formatted_values
    }), 200

@analysis_bp.route('/api/analysis/analyze', methods=['POST'])
@login_required
def analyze_hemogram():
    """Rota para analisar hemograma."""
    data = request.json
    
    if not data or 'especie' not in data:
        return jsonify({
            'success': False,
            'error': 'Dados do hemograma inválidos ou incompletos.'
        }), 400
    
    # Extrair informações do paciente, se fornecidas
    patient_info = {
        'nome_paciente': data.get('nome_paciente'),
        'raca': data.get('raca'),
        'idade': data.get('idade'),
        'sexo': data.get('sexo'),
        'nome_tutor': data.get('nome_tutor')
    }
    
    # Remover informações do paciente dos dados do hemograma
    hemogram_data = {k: v for k, v in data.items() if k not in patient_info}
    
    result = AnalysisService.analisar_hemograma(hemogram_data, patient_info)
    success = True
    message = "Análise concluída com sucesso."
    
    if success:
        return jsonify({
            'success': True,
            'data': result
        }), 200
    else:
        return jsonify({
            'success': False,
            'error': message
        }), 400

@analysis_bp.route('/api/analysis/upload', methods=['POST'])
@login_required
def upload_and_extract():
    """Rota para upload e extração de arquivo de hemograma."""
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': 'Nenhum arquivo enviado.'
        }), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({
            'success': False,
            'error': 'Nenhum arquivo selecionado.'
        }), 400
    
    # Verificar extensão
    allowed_extensions = {'pdf', 'csv'}
    if '.' not in file.filename or \
       file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return jsonify({
            'success': False,
            'error': 'Formato de arquivo não permitido. Use PDF ou CSV.'
        }), 400
    
    # Processar arquivo
    extracted_data = processar_arquivo_hemograma(file)
    
    if not extracted_data:
        return jsonify({
            'success': False,
            'error': 'Não foi possível extrair dados do arquivo.'
        }), 400
    
    return jsonify({
        'success': True,
        'data': extracted_data
    }), 200

@analysis_bp.route('/api/analysis/history', methods=['GET'])
@login_required
def get_analysis_history():
    """Rota para obter histórico de análises."""
    limit = request.args.get('limit', 10, type=int)
    
    history = AnalysisService.get_analysis_history(current_user.id, limit)
    
    return jsonify({
        'success': True,
        'data': history
    }), 200

@analysis_bp.route('/api/analysis/<int:analysis_id>', methods=['GET'])
@login_required
def get_analysis(analysis_id):
    """Rota para obter uma análise específica."""
    analysis = AnalysisService.get_analysis_by_id(analysis_id, current_user.id)
    
    if not analysis:
        return jsonify({
            'success': False,
            'error': 'Análise não encontrada ou sem permissão para acessá-la.'
        }), 404
    
    return jsonify({
        'success': True,
        'data': analysis
    }), 200
