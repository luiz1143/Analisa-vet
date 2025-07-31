"""
Utilitários para extração e processamento de arquivos PDF e CSV.
Versão melhorada com separação de dados de paciente e hemograma.
Compatível com Windows usando PyPDF2.
"""

import subprocess
import re
import pandas as pd
import os
import tempfile
from werkzeug.utils import secure_filename

def extrair_texto_pdf(caminho_pdf):
    """
    Extrai texto de um arquivo PDF usando PyPDF2 (compatível com Windows).
    
    Args:
        caminho_pdf: Caminho para o arquivo PDF
        
    Returns:
        Texto extraído do PDF ou None em caso de erro
    """
    try:
        # Tentar usar pdftotext primeiro (se disponível)
        processo = subprocess.run(["pdftotext", "-layout", caminho_pdf, "-"], 
                                 capture_output=True, text=True, check=True, encoding="utf-8")
        return processo.stdout
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"pdftotext não disponível, tentando PyPDF2: {e}")
        # Fallback para PyPDF2
        try:
            import PyPDF2
            texto = ""
            with open(caminho_pdf, 'rb') as arquivo:
                leitor = PyPDF2.PdfReader(arquivo)
                for pagina in leitor.pages:
                    texto += pagina.extract_text() + "\n"
            return texto
        except ImportError:
            print("PyPDF2 não está instalado. Instale com: pip install PyPDF2")
            return None
        except Exception as e2:
            print(f"Erro ao extrair texto com PyPDF2: {e2}")
            return None
    except Exception as e:
        print(f"Erro inesperado ao extrair texto do PDF: {e}")
        return None

def extrair_dados_hemograma(texto):
    """
    Extrai valores de hemograma e informações do paciente do texto usando regex.
    
    Args:
        texto: Texto extraído do PDF
        
    Returns:
        Dicionário com dados do hemograma e informações do paciente separados
    """
    dados_hemograma = {}
    dados_paciente = {}
    
    # Regex para parâmetros do hemograma - padrões mais flexíveis
    padroes_hemograma = {
        "hemacias": r"(?:Hemácias|Eritrócitos|RBC)[^\d]*([\d.,]+)",
        "hemoglobina": r"(?:Hemoglobina|Hb|HGB)[^\d]*([\d.,]+)",
        "hematocrito": r"(?:Hematócrito|Ht|HCT)[^\d]*([\d.,]+)",
        "vcm": r"(?:VCM|MCV)[^\d]*([\d.,]+)",
        "hcm": r"(?:HCM|MCH)[^\d]*([\d.,]+)",
        "chcm": r"(?:CHCM|MCHC)[^\d]*([\d.,]+)",
        "reticulocitos": r"(?:Reticulócitos|Retic)[^\d]*([\d.,]+)",
        "leucocitos": r"(?:Leucócitos|Leuco|WBC)[^\d]*([\d.,]+)",
        "segmentados": r"(?:Segmentados|Neutrófilos|Neutro|Seg)[^\d]*([\d.,]+)",
        "linfocitos": r"(?:Linfócitos|Linfo|Lymph)[^\d]*([\d.,]+)",
        "monocitos": r"(?:Monócitos|Mono)[^\d]*([\d.,]+)",
        "eosinofilos": r"(?:Eosinófilos|Eosino|Eos)[^\d]*([\d.,]+)",
        "basofilos": r"(?:Basófilos|Baso)[^\d]*([\d.,]+)",
        "plaquetas": r"(?:Plaquetas|PLT)[^\d]*([\d.,]+)",
        "proteina": r"(?:Proteína|Proteinas|PPT|TP)[^\d]*([\d.,]+)"
    }
    
    # Regex para informações do paciente - padrões mais robustos
    padroes_paciente = {
        "nome": r"(?:Nome.*?Paciente|Paciente|Animal|Nome)[:\s]\s*([A-Za-zÀ-ÖØ-öø-ÿ\s]+?)(?:\n|,|\s{2,}|$)",
        "especie": r"(?:Espécie|Especie)[:\s]\s*([A-Za-zÀ-ÖØ-öø-ÿ\s]+?)(?:\n|,|\s{2,}|$)",
        "raca": r"(?:Raça|Raca)[:\s]\s*([A-Za-zÀ-ÖØ-öø-ÿ\s]+?)(?:\n|,|\s{2,}|$)",
        "idade": r"(?:Idade)[:\s]\s*([0-9,.\s]+(?:anos?|meses?|dias?|semanas?))(?:\n|,|\s{2,}|$)",
        "sexo": r"(?:Sexo)[:\s]\s*([A-Za-zÀ-ÖØ-öø-ÿ\s]+?)(?:\n|,|\s{2,}|$)",
        "tutor": r"(?:Proprietário|Tutor|Responsável|Responsavel|Dono)[:\s]\s*([A-Za-zÀ-ÖØ-öø-ÿ\s]+?)(?:\n|,|\s{2,}|$)"
    }
    
    # Padrões alternativos para informações do paciente (formato tabular)
    padroes_paciente_alt = {
        "nome": r"(?:Nome|Paciente|Animal)\s*[:\|]\s*([A-Za-zÀ-ÖØ-öø-ÿ\s]+)",
        "especie": r"(?:Espécie|Especie)\s*[:\|]\s*([A-Za-zÀ-ÖØ-öø-ÿ\s]+)",
        "raca": r"(?:Raça|Raca)\s*[:\|]\s*([A-Za-zÀ-ÖØ-öø-ÿ\s]+)",
        "idade": r"(?:Idade)\s*[:\|]\s*([0-9,.\s]+(?:anos?|meses?|dias?|semanas?)?)",
        "sexo": r"(?:Sexo)\s*[:\|]\s*([A-Za-zÀ-ÖØ-öø-ÿ\s]+)",
        "tutor": r"(?:Proprietário|Tutor|Responsável|Responsavel|Dono)\s*[:\|]\s*([A-Za-zÀ-ÖØ-öø-ÿ\s]+)"
    }
    
    # Tentar encontrar a espécie (simples)
    if re.search(r"(?:Cão|Canino|Canine)", texto, re.IGNORECASE):
        dados_paciente["especie"] = "Cão"
    elif re.search(r"(?:Gato|Felino|Feline)", texto, re.IGNORECASE):
        dados_paciente["especie"] = "Gato"
    else:
        dados_paciente["especie"] = None  # Não conseguiu identificar
    
    # Extrair parâmetros do hemograma
    for chave, padrao in padroes_hemograma.items():
        match = re.search(padrao, texto, re.IGNORECASE | re.DOTALL)
        if match:
            valor_str = match.group(1).replace(".", "").replace(",", ".")  # Normalizar para ponto decimal
            try:
                dados_hemograma[chave] = float(valor_str)
            except ValueError:
                print(f"Aviso: Não foi possível converter '{match.group(1)}' para float para a chave '{chave}'.")
                dados_hemograma[chave] = None
        else:
            dados_hemograma[chave] = None  # Não encontrou o padrão
    
    # Extrair informações do paciente
    for chave, padrao in padroes_paciente.items():
        match = re.search(padrao, texto, re.IGNORECASE | re.DOTALL)
        if match:
            dados_paciente[chave] = match.group(1).strip()
        else:
            # Tentar padrão alternativo
            alt_match = re.search(padroes_paciente_alt[chave], texto, re.IGNORECASE | re.DOTALL)
            if alt_match:
                dados_paciente[chave] = alt_match.group(1).strip()
            else:
                dados_paciente[chave] = None  # Não encontrou o padrão
    
    # Retornar dados separados em hemograma e paciente
    return {
        "hemograma": dados_hemograma,
        "paciente": dados_paciente
    }

def parse_csv_hemograma(caminho_csv):
    """
    Extrai valores de hemograma e informações do paciente de um arquivo CSV.
    
    Args:
        caminho_csv: Caminho para o arquivo CSV
        
    Returns:
        Dicionário com dados do hemograma e informações do paciente separados
    """
    try:
        df = pd.read_csv(caminho_csv, delimiter=None, engine="python")  # Tenta detectar delimitador
        dados_hemograma = {}
        dados_paciente = {}
        
        # Mapeamento flexível de possíveis nomes de colunas para nossas chaves
        mapeamento_hemograma = {
            "hemacias": ["hemacias", "eritrocitos", "rbc"],
            "hemoglobina": ["hemoglobina", "hb", "hgb"],
            "hematocrito": ["hematocrito", "ht", "hct"],
            "vcm": ["vcm", "mcv"],
            "hcm": ["hcm", "mch"],
            "chcm": ["chcm", "mchc"],
            "reticulocitos": ["reticulocitos", "retic"],
            "leucocitos": ["leucocitos", "leuco", "wbc"],
            "segmentados": ["segmentados", "neutrofilos", "neutro", "seg"],
            "linfocitos": ["linfocitos", "linfo", "lymph"],
            "monocitos": ["monocitos", "mono"],
            "eosinofilos": ["eosinofilos", "eosino", "eos"],
            "basofilos": ["basofilos", "baso"],
            "plaquetas": ["plaquetas", "plt"],
            "proteina": ["proteina", "proteinas", "ppt", "tp"]
        }
        
        # Mapeamento para informações do paciente
        mapeamento_paciente = {
            "nome": ["nome", "paciente", "animal", "pet", "nome_paciente"],
            "raca": ["raca", "breed"],
            "idade": ["idade", "age"],
            "sexo": ["sexo", "gender"],
            "tutor": ["tutor", "proprietario", "dono", "responsavel", "owner"],
            "especie": ["especie", "animal", "species"]
        }
        
        df.columns = df.columns.str.lower().str.strip()  # Normalizar nomes das colunas
        
        # Assumir que os dados estão na primeira linha
        if not df.empty:
            primeira_linha = df.iloc[0]
            
            # Extrair dados do hemograma
            for chave, nomes_possiveis in mapeamento_hemograma.items():
                valor = None
                for nome_coluna in nomes_possiveis:
                    if nome_coluna in df.columns:
                        valor_bruto = primeira_linha[nome_coluna]
                        if pd.isna(valor_bruto):
                            valor = None
                            break
                        try:
                            # Tentar converter para float, tratando vírgula como decimal
                            valor = float(str(valor_bruto).replace(",", "."))
                        except (ValueError, TypeError):
                            valor = None
                        break  # Encontrou a coluna, para de procurar
                dados_hemograma[chave] = valor
            
            # Extrair informações do paciente
            for chave, nomes_possiveis in mapeamento_paciente.items():
                valor = None
                for nome_coluna in nomes_possiveis:
                    if nome_coluna in df.columns:
                        valor_bruto = primeira_linha[nome_coluna]
                        if pd.isna(valor_bruto):
                            valor = None
                            break
                        
                        if chave == "especie":
                            valor_str = str(valor_bruto).strip().lower()
                            if "cão" in valor_str or "canino" in valor_str:
                                valor = "Cão"
                            elif "gato" in valor_str or "felino" in valor_str:
                                valor = "Gato"
                            else:
                                valor = str(valor_bruto).strip()
                        else:
                            valor = str(valor_bruto).strip()
                        break  # Encontrou a coluna, para de procurar
                dados_paciente[chave] = valor
        
        # Retornar dados separados em hemograma e paciente
        return {
            "hemograma": dados_hemograma,
            "paciente": dados_paciente
        }
    
    except Exception as e:
        print(f"Erro ao processar CSV: {e}")
        return None

def processar_arquivo_hemograma(arquivo, diretorio_temp=None):
    """
    Processa um arquivo de hemograma (PDF ou CSV) e extrai os dados.
    
    Args:
        arquivo: Objeto de arquivo do Flask (request.files)
        diretorio_temp: Diretório temporário para salvar o arquivo (opcional)
        
    Returns:
        Dicionário com dados extraídos separados em hemograma e paciente
    """
    if not arquivo or arquivo.filename == '':
        return None
    
    # Verificar extensão do arquivo
    extensao = arquivo.filename.rsplit('.', 1)[1].lower() if '.' in arquivo.filename else ''
    if extensao not in ['pdf', 'csv']:
        return None
    
    # Criar diretório temporário se não fornecido
    if diretorio_temp is None:
        diretorio_temp = tempfile.mkdtemp()
    
    # Salvar arquivo temporariamente
    nome_arquivo = secure_filename(arquivo.filename)
    caminho_temp = os.path.join(diretorio_temp, nome_arquivo)
    
    try:
        arquivo.save(caminho_temp)
        
        # Processar arquivo de acordo com o tipo
        if extensao == 'pdf':
            texto = extrair_texto_pdf(caminho_temp)
            if texto:
                dados = extrair_dados_hemograma(texto)
            else:
                dados = {"hemograma": {}, "paciente": {}}
        else:  # CSV
            dados = parse_csv_hemograma(caminho_temp)
            if not dados:
                dados = {"hemograma": {}, "paciente": {}}
        
        # Limpar arquivo temporário
        os.remove(caminho_temp)
        
        # Garantir que os dados estão no formato esperado pelo frontend
        if "hemograma" not in dados:
            dados = {"hemograma": {}, "paciente": {}}
        
        return dados
    
    except Exception as e:
        print(f"Erro ao processar arquivo: {e}")
        # Tentar limpar arquivo temporário em caso de erro
        if os.path.exists(caminho_temp):
            os.remove(caminho_temp)
        return {"hemograma": {}, "paciente": {}}

