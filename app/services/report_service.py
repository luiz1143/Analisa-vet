
"""
Serviço de geração de laudos para o aplicativo AnalisaVet.
Versão corrigida para suportar múltiplos diagnósticos e explicações.
"""

import os
import tempfile
from datetime import datetime
from xhtml2pdf import pisa
from jinja2 import Environment, FileSystemLoader
from flask import current_app

class ReportService:
    """Serviço para geração de laudos técnicos e simplificados."""
    
    @staticmethod
    def generate_technical_report(analysis_data, patient_info, clinic_info):
        """
        Gera um laudo técnico em PDF.
        
        Args:
            analysis_data: Dados da análise
            patient_info: Informações do paciente
            clinic_info: Informações da clínica
            
        Returns:
            Caminho para o arquivo PDF gerado ou None em caso de erro
        """
        try:
            # Configurar ambiente Jinja2
            template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates', 'reports')
            env = Environment(loader=FileSystemLoader(template_dir))
            template = env.get_template('technical.html')
            
            # Construir o caminho relativo para o logo, se existir
            logo_relative_path = None
            if clinic_info and 'logo_path' in clinic_info and clinic_info['logo_path']:
                # Assumindo que o logo_path é relativo à pasta 'static' dentro do app
                logo_relative_path = f"/static/{clinic_info['logo_path']}"
                clinic_info['logo_path'] = logo_relative_path

            # Preparar dados para o template
            data = {
                'clinic': clinic_info,
                'patient': patient_info,
                'analysis': analysis_data,
                'date': datetime.now().strftime('%d/%m/%Y'),
                'time': datetime.now().strftime('%H:%M')
            }
            
            # Renderizar HTML
            html_content = template.render(data)
            
            # Criar arquivo PDF temporário
            fd, temp_path = tempfile.mkstemp(suffix='.pdf')
            os.close(fd)
            
            # Gerar PDF
            pisa_status = pisa.CreatePDF(
                html_content,                # the HTML to convert
                dest=temp_path)  # file handle to receive result
            if pisa_status.err:
                raise Exception(f"Erro ao gerar PDF com xhtml2pdf: {pisa_status.err}")
            
            return temp_path
        
        except Exception as e:
            print(f"Erro ao gerar laudo técnico: {str(e)}")
            return None
    
    @staticmethod
    def generate_simplified_report(analysis_data, patient_info, clinic_info):
        """
        Gera um laudo simplificado em PDF para tutores.
        
        Args:
            analysis_data: Dados da análise
            patient_info: Informações do paciente
            clinic_info: Informações da clínica
            
        Returns:
            Caminho para o arquivo PDF gerado ou None em caso de erro
        """
        try:
            # Configurar ambiente Jinja2
            template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates', 'reports')
            env = Environment(loader=FileSystemLoader(template_dir))
            template = env.get_template('simplified.html')
            
            # Construir o caminho relativo para o logo, se existir
            logo_relative_path = None
            if clinic_info and 'logo_path' in clinic_info and clinic_info['logo_path']:
                # Assumindo que o logo_path é relativo à pasta 'static'
                logo_relative_path = f"/static/{clinic_info['logo_path']}"
                clinic_info['logo_path'] = logo_relative_path

            # Preparar dados para o template
            data = {
                'clinic': clinic_info,
                'patient': patient_info,
                'analysis': analysis_data,
                'date': datetime.now().strftime('%d/%m/%Y'),
                'time': datetime.now().strftime('%H:%M')
            }
            
            # Renderizar HTML
            html_content = template.render(data)
            
            # Criar arquivo PDF temporário
            fd, temp_path = tempfile.mkstemp(suffix='.pdf')
            os.close(fd)
            
            # Gerar PDF
            pisa_status = pisa.CreatePDF(
                html_content,                # the HTML to convert
                dest=temp_path)  # file handle to receive result
            if pisa_status.err:
                raise Exception(f"Erro ao gerar PDF com xhtml2pdf: {pisa_status.err}")
            
            return temp_path
        
        except Exception as e:
            print(f"Erro ao gerar laudo simplificado: {str(e)}")
            return None








