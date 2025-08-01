"""
Utilitários para extração e processamento de arquivos PDF e CSV.
Versão melhorada com separação de dados de paciente e hemograma.
Compatível com Windows usando PyPDF2.
"""

import subprocess
import re
import os
import tempfile
import csv
import io
from werkzeug.utils import secure_filename

def extrair_texto_pdf(caminho_pdf):
    """
    Extrai texto de um arquivo PDF usando PyPDF2 (compatível com Windows).
    
    Args:
        caminho_pdf: Caminho para o arquivo PDF
        
    Returns:
        str: Texto extraído do PDF
    """
    try:
        from PyPDF2 import PdfReader
        
        with open(caminho_pdf, 'rb') as arquivo:
            leitor = PdfReader(arquivo)
            texto = ""
            for pagina in leitor.pages:
                texto += pagina.extract_text() + "\n"
        
        return texto
    except ImportError:
        # Fallback para pdfplumber se PyPDF2 não estiver disponível
        try:
            import pdfplumber
            with pdfplumber.open(caminho_pdf) as pdf:
                texto = ""
                for pagina in pdf.pages:
                    texto += pagina.extract_text() + "\n"
            return texto
        except ImportError:
            raise ImportError("Nenhuma biblioteca de PDF disponível. Instale PyPDF2 ou pdfplumber.")

def processar_arquivo_csv(caminho_csv):
    """
    Processa arquivo CSV de hemograma.
    
    Args:
        caminho_csv: Caminho para o arquivo CSV
        
    Returns:
        dict: Dados processados do hemograma
    """
    try:
        dados = {}
        
        with open(caminho_csv, 'r', encoding='utf-8') as arquivo:
            # Detectar delimitador
            sample = arquivo.read(1024)
            arquivo.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.DictReader(arquivo, delimiter=delimiter)
            
            for row in reader:
                for key, value in row.items():
                    if key and value:
                        # Tentar converter para float se possível
                        try:
                            dados[key.strip().lower()] = float(value.strip())
                        except ValueError:
                            dados[key.strip().lower()] = value.strip()
        
        return dados
        
    except Exception as e:
        print(f"Erro ao processar CSV: {e}")
        return {}

def processar_arquivo_hemograma(arquivo):
    """
    Processa arquivo de hemograma (PDF ou CSV) e extrai dados estruturados.
    
    Args:
        arquivo: Objeto de arquivo do Flask
        
    Returns:
        dict: Dados estruturados do hemograma
    """
    if not arquivo or arquivo.filename == '':
        return {"erro": "Nenhum arquivo fornecido"}
    
    filename = secure_filename(arquivo.filename)
    
    # Criar arquivo temporário
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
        arquivo.save(temp_file.name)
        temp_path = temp_file.name
    
    try:
        if filename.lower().endswith('.pdf'):
            texto = extrair_texto_pdf(temp_path)
            dados = extrair_dados_hemograma_texto(texto)
        elif filename.lower().endswith('.csv'):
            dados = processar_arquivo_csv(temp_path)
        else:
            return {"erro": "Formato de arquivo não suportado"}
        
        return dados
        
    except Exception as e:
        return {"erro": f"Erro ao processar arquivo: {str(e)}"}
        
    finally:
        # Limpar arquivo temporário
        try:
            os.unlink(temp_path)
        except:
            pass

def extrair_dados_hemograma_texto(texto):
    """
    Extrai dados de hemograma de texto usando regex.
    
    Args:
        texto: Texto extraído do PDF
        
    Returns:
        dict: Dados estruturados do hemograma
    """
    dados = {}
    
    # Padrões regex para extração de dados
    padroes = {
        'hemacias': r'hem[aá]cias?\s*:?\s*([0-9,\.]+)',
        'hemoglobina': r'hemoglobina\s*:?\s*([0-9,\.]+)',
        'hematocrito': r'hemat[oó]crito\s*:?\s*([0-9,\.]+)',
        'vcm': r'vcm\s*:?\s*([0-9,\.]+)',
        'hcm': r'hcm\s*:?\s*([0-9,\.]+)',
        'chcm': r'chcm\s*:?\s*([0-9,\.]+)',
        'leucocitos': r'leuc[oó]citos?\s*:?\s*([0-9,\.]+)',
        'segmentados': r'segmentados?\s*:?\s*([0-9,\.]+)',
        'linfocitos': r'linf[oó]citos?\s*:?\s*([0-9,\.]+)',
        'monocitos': r'mon[oó]citos?\s*:?\s*([0-9,\.]+)',
        'eosinofilos': r'eosin[oó]filos?\s*:?\s*([0-9,\.]+)',
        'basofilos': r'bas[oó]filos?\s*:?\s*([0-9,\.]+)',
        'plaquetas': r'plaquetas?\s*:?\s*([0-9,\.]+)',
        'proteina_total': r'prote[ií]na\s*total\s*:?\s*([0-9,\.]+)',
        'reticulocitos': r'retic[uú]l[oó]citos?\s*:?\s*([0-9,\.]+)'
    }
    
    texto_lower = texto.lower()
    
    for campo, padrao in padroes.items():
        match = re.search(padrao, texto_lower, re.IGNORECASE)
        if match:
            try:
                valor = match.group(1).replace(',', '.')
                dados[campo] = float(valor)
            except ValueError:
                continue
    
    return dados

