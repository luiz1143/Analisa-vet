"""
Serviço de análise de hemograma para o aplicativo AnalisaVet.
Versão aprimorada com critérios clínicos detalhados e interpretação para tutores.
Implementa a regra de 15% e interpretação conjunta de alterações discretas.
"""

import json
import numpy as np
from ..models.models import Analysis, User, db

class AnalysisService:
    """Serviço para gerenciar análises de hemograma."""
    
    # Valores de referência para cães e gatos
    VALORES_REFERENCIA = {
        "Cão": {
            "hemacias": {"min": 5.5, "max": 8.5, "unidade": "10⁶/µL"},
            "hemoglobina": {"min": 12, "max": 18, "unidade": "g/dL"},
            "hematocrito": {"min": 37, "max": 55, "unidade": "%"},
            "vcm": {"min": 60, "max": 77, "unidade": "fL"},
            "hcm": {"min": 19, "max": 24, "unidade": "pg"},
            "chcm": {"min": 32, "max": 36, "unidade": "%"},
            "reticulocitos": {"min": 11, "max": 92, "unidade": "×10³/µL"},
            "leucocitos": {"min": 6000, "max": 17000, "unidade": "/µL"},
            "segmentados": {"min": 2700, "max": 9400, "unidade": "/µL"},
            "linfocitos": {"min": 900, "max": 4700, "unidade": "/µL"},
            "monocitos": {"min": 100, "max": 1300, "unidade": "/µL"},
            "eosinofilos": {"min": 100, "max": 2100, "unidade": "/µL"},
            "basofilos": {"min": 0, "max": 200, "unidade": "/µL"},
            "plaquetas": {"min": 186000, "max": 545000, "unidade": "/µL"},
            "proteina": {"min": 6.0, "max": 8.0, "unidade": "g/dL"}
        },
        "Gato": {
            "hemacias": {"min": 5.0, "max": 10.0, "unidade": "10⁶/µL"},
            "hemoglobina": {"min": 8, "max": 15, "unidade": "g/dL"},
            "hematocrito": {"min": 31, "max": 48, "unidade": "%"},
            "vcm": {"min": 39, "max": 55, "unidade": "fL"},
            "hcm": {"min": 13, "max": 17, "unidade": "pg"},
            "chcm": {"min": 30, "max": 36, "unidade": "%"},
            "reticulocitos": {"min": 9, "max": 61, "unidade": "×10³/µL"},
            "leucocitos": {"min": 5500, "max": 19500, "unidade": "/µL"},
            "segmentados": {"min": 2300, "max": 11600, "unidade": "/µL"},
            "linfocitos": {"min": 900, "max": 6000, "unidade": "/µL"},
            "monocitos": {"min": 0, "max": 700, "unidade": "/µL"},
            "eosinofilos": {"min": 100, "max": 1800, "unidade": "/µL"},
            "basofilos": {"min": 0, "max": 200, "unidade": "/µL"},
            "plaquetas": {"min": 195000, "max": 624000, "unidade": "/µL"},
            "proteina": {"min": 6.0, "max": 8.0, "unidade": "g/dL"}
        }
    }
    
    # Grupos de parâmetros relacionados para interpretação conjunta
    GRUPOS_PARAMETROS = {
        "anemia": ["hemoglobina", "hematocrito", "vcm", "chcm"],
        "infeccao_bacteriana": ["leucocitos", "segmentados"],
        "infeccao_viral": ["linfocitos", "leucocitos"],
        "inflamacao_cronica": ["monocitos", "segmentados"],
        "alergia_parasitose": ["eosinofilos", "leucocitos"],
        "disturbios_coagulacao": ["plaquetas"]
    }
    
    @staticmethod
    def aplicar_regra_15_porcento(valor, valor_min, valor_max):
        """
        Aplica a regra de 15% para determinar se um valor está alterado.
        
        Args:
            valor: Valor do exame
            valor_min: Limite inferior de referência
            valor_max: Limite superior de referência
            
        Returns:
            dict: {"alterado": bool, "tipo": str, "desvio_percentual": float}
        """
        if valor is None:
            return {"alterado": False, "tipo": "normal", "desvio_percentual": 0}
        
        # Calcular limites ajustados com 15%
        margem_inferior = valor_min * 0.15
        margem_superior = valor_max * 0.15
        
        limite_inferior_ajustado = valor_min - margem_inferior
        limite_superior_ajustado = valor_max + margem_superior
        
        if valor < limite_inferior_ajustado:
            # Valor abaixo do normal com mais de 15% de desvio
            desvio_percentual = ((valor_min - valor) / valor_min) * 100
            
            if desvio_percentual <= 30:
                tipo_alteracao = "leve"
            elif desvio_percentual <= 50:
                tipo_alteracao = "moderada"
            else:
                tipo_alteracao = "grave"
                
            return {
                "alterado": True,
                "tipo": f"baixo_{tipo_alteracao}",
                "desvio_percentual": desvio_percentual
            }
            
        elif valor > limite_superior_ajustado:
            # Valor acima do normal com mais de 15% de desvio
            desvio_percentual = ((valor - valor_max) / valor_max) * 100
            
            if desvio_percentual <= 30:
                tipo_alteracao = "leve"
            elif desvio_percentual <= 50:
                tipo_alteracao = "moderada"
            else:
                tipo_alteracao = "grave"
                
            return {
                "alterado": True,
                "tipo": f"alto_{tipo_alteracao}",
                "desvio_percentual": desvio_percentual
            }
        else:
            # Valor dentro dos limites aceitáveis (incluindo margem de 15%)
            return {"alterado": False, "tipo": "normal", "desvio_percentual": 0}
    
    @staticmethod
    def interpretar_alteracoes_conjuntas(dados_hemograma, especie):
        """
        Identifica padrões clínicos quando múltiplos parâmetros apresentam alterações discretas.
        
        Args:
            dados_hemograma: Dados do hemograma
            especie: Espécie do animal (Cão ou Gato)
            
        Returns:
            list: Lista de interpretações conjuntas identificadas
        """
        valores_referencia = AnalysisService.VALORES_REFERENCIA.get(especie, {})
        interpretacoes = []
        
        for grupo, parametros in AnalysisService.GRUPOS_PARAMETROS.items():
            parametros_alterados = []
            
            for parametro in parametros:
                if parametro in dados_hemograma and parametro in valores_referencia:
                    valor = dados_hemograma[parametro]
                    ref = valores_referencia[parametro]
                    
                    # Verificar se está fora dos valores de referência (mesmo que menos de 15%)
                    if valor is not None and (valor < ref["min"] or valor > ref["max"]):
                        parametros_alterados.append(parametro)
            
            # Se dois ou mais parâmetros do mesmo grupo estão alterados
            if len(parametros_alterados) >= 2:
                interpretacoes.append({
                    "grupo": grupo,
                    "parametros_alterados": parametros_alterados,
                    "recomendacao": f"Múltiplos parâmetros do grupo {grupo} apresentam alterações discretas. Recomenda-se monitoramento e investigação adicional."
                })
        
        return interpretacoes
    
    @staticmethod
    def analisar_hemograma(dados_hemograma, dados_paciente):
        """
        Analisa um hemograma completo aplicando as regras de 15% e interpretação conjunta.
        
        Args:
            dados_hemograma: Dados do hemograma
            dados_paciente: Dados do paciente
            
        Returns:
            dict: Análise completa do hemograma
        """
        especie = dados_paciente.get("especie", "Cão")
        valores_referencia = AnalysisService.VALORES_REFERENCIA.get(especie, {})
        
        resultados = {
            "parametros": {},
            "interpretacoes_individuais": [],
            "interpretacoes_conjuntas": [],
            "resumo_clinico": "",
            "recomendacoes": [],
            "diagnosticos": []
        }
        
        # Analisar cada parâmetro individualmente
        for parametro, valor in dados_hemograma.items():
            if parametro in valores_referencia and valor is not None:
                ref = valores_referencia[parametro]
                analise = AnalysisService.aplicar_regra_15_porcento(valor, ref["min"], ref["max"])
                
                resultados["parametros"][parametro] = {
                    "valor": valor,
                    "referencia": f"{ref['min']} - {ref['max']} {ref['unidade']}",
                    "status": analise["tipo"],
                    "alterado": analise["alterado"],
                    "desvio_percentual": analise["desvio_percentual"]
                }
                
                # Adicionar interpretações para valores alterados
                if analise["alterado"]:
                    resultados["interpretacoes_individuais"].append({
                        "parametro": parametro,
                        "tipo_alteracao": analise["tipo"],
                        "desvio": analise["desvio_percentual"],
                        "interpretacao": AnalysisService._obter_interpretacao_parametro(parametro, analise["tipo"], especie)
                    })
        
        # Analisar alterações conjuntas
        resultados["interpretacoes_conjuntas"] = AnalysisService.interpretar_alteracoes_conjuntas(dados_hemograma, especie)
        
        # Gerar resumo clínico
        resultados["resumo_clinico"] = AnalysisService._gerar_resumo_clinico(resultados)
        
        # Gerar recomendações
        resultados["recomendacoes"] = AnalysisService._gerar_recomendacoes(resultados)
        
        resultados["diagnosticos"] = resultados["interpretacoes_individuais"] + resultados["interpretacoes_conjuntas"]
    
    @staticmethod
    def _obter_interpretacao_parametro(parametro, tipo_alteracao, especie):
        """
        Obtém a interpretação clínica para um parâmetro específico alterado.
        """
        interpretacoes = {
            "hemacias": {
                "baixo_leve": "Discreta diminuição no número de hemácias, possivelmente relacionada a anemia leve.",
                "baixo_moderada": "Diminuição moderada no número de hemácias, sugerindo anemia que requer investigação.",
                "baixo_grave": "Diminuição grave no número de hemácias, indicando anemia severa que necessita atenção imediata.",
                "alto_leve": "Discreto aumento no número de hemácias, possivelmente relacionado a desidratação ou policitemia leve.",
                "alto_moderada": "Aumento moderado no número de hemácias, sugerindo policitemia que requer avaliação.",
                "alto_grave": "Aumento grave no número de hemácias, indicando policitemia severa."
            },
            "hemoglobina": {
                "baixo_leve": "Discreta diminuição da hemoglobina, sugerindo anemia leve.",
                "baixo_moderada": "Diminuição moderada da hemoglobina, indicando anemia que requer investigação.",
                "baixo_grave": "Diminuição grave da hemoglobina, indicando anemia severa que necessita atenção imediata.",
                "alto_leve": "Discreto aumento da hemoglobina, possivelmente relacionado a desidratação.",
                "alto_moderada": "Aumento moderado da hemoglobina, sugerindo policitemia.",
                "alto_grave": "Aumento grave da hemoglobina, indicando policitemia severa."
            },
            "leucocitos": {
                "baixo_leve": "Discreta diminuição dos leucócitos (leucopenia leve), possivelmente relacionada a infecção viral ou estresse.",
                "baixo_moderada": "Diminuição moderada dos leucócitos, sugerindo supressão imunológica que requer investigação.",
                "baixo_grave": "Diminuição grave dos leucócitos, indicando imunossupressão severa.",
                "alto_leve": "Discreto aumento dos leucócitos, possivelmente relacionado a estresse ou inflamação leve.",
                "alto_moderada": "Aumento moderado dos leucócitos, sugerindo infecção ou inflamação.",
                "alto_grave": "Aumento grave dos leucócitos, indicando infecção severa ou processo inflamatório intenso."
            },
            "plaquetas": {
                "baixo_leve": "Discreta diminuição das plaquetas (trombocitopenia leve), requer monitoramento.",
                "baixo_moderada": "Diminuição moderada das plaquetas, aumentando risco de sangramento.",
                "baixo_grave": "Diminuição grave das plaquetas, risco significativo de sangramento espontâneo.",
                "alto_leve": "Discreto aumento das plaquetas, possivelmente reacional.",
                "alto_moderada": "Aumento moderado das plaquetas, sugerindo processo inflamatório ou reacional.",
                "alto_grave": "Aumento grave das plaquetas, possível distúrbio mieloproliferativo."
            }
        }
        
        return interpretacoes.get(parametro, {}).get(tipo_alteracao, f"Alteração {tipo_alteracao} no parâmetro {parametro}.")
    
    @staticmethod
    def _gerar_resumo_clinico(resultados):
        """
        Gera um resumo clínico baseado nos resultados da análise.
        """
        alteracoes_graves = [r for r in resultados["interpretacoes_individuais"] if "grave" in r["tipo_alteracao"]]
        alteracoes_moderadas = [r for r in resultados["interpretacoes_individuais"] if "moderada" in r["tipo_alteracao"]]
        alteracoes_leves = [r for r in resultados["interpretacoes_individuais"] if "leve" in r["tipo_alteracao"]]
        
        if alteracoes_graves:
            return f"Hemograma apresenta {len(alteracoes_graves)} alteração(ões) grave(s) que requer(em) atenção imediata."
        elif alteracoes_moderadas:
            return f"Hemograma apresenta {len(alteracoes_moderadas)} alteração(ões) moderada(s) que requer(em) investigação."
        elif alteracoes_leves:
            return f"Hemograma apresenta {len(alteracoes_leves)} alteração(ões) leve(s) que requer(em) monitoramento."
        else:
            return "Hemograma dentro dos parâmetros de normalidade considerando a margem de 15%."
    
    @staticmethod
    def _gerar_recomendacoes(resultados):
        """
        Gera recomendações baseadas nos resultados da análise.
        """
        recomendacoes = []
        
        # Recomendações baseadas em alterações graves
        alteracoes_graves = [r for r in resultados["interpretacoes_individuais"] if "grave" in r["tipo_alteracao"]]
        if alteracoes_graves:
            recomendacoes.append("Consulta veterinária urgente devido a alterações graves identificadas.")
        
        # Recomendações baseadas em alterações moderadas
        alteracoes_moderadas = [r for r in resultados["interpretacoes_individuais"] if "moderada" in r["tipo_alteracao"]]
        if alteracoes_moderadas:
            recomendacoes.append("Consulta veterinária para investigação das alterações moderadas identificadas.")
        
        # Recomendações baseadas em interpretações conjuntas
        if resultados["interpretacoes_conjuntas"]:
            recomendacoes.append("Monitoramento adicional recomendado devido a múltiplas alterações discretas relacionadas.")
        
        # Recomendações gerais
        if not recomendacoes:
            recomendacoes.append("Manter acompanhamento veterinário de rotina.")
        
        return recomendacoes
    
    @staticmethod
    def obter_valores_referencia(especie):
        """Obtém os valores de referência para uma espécie específica."""
        return AnalysisService.VALORES_REFERENCIA.get(especie, {})
    
    @staticmethod
    def salvar_analise(user_id, dados_hemograma, dados_paciente, resultados_analise):
        """
        Salva uma análise de hemograma no banco de dados.
        
        Args:
            user_id: ID do usuário
            dados_hemograma: Dados do hemograma
            dados_paciente: Dados do paciente
            resultados_analise: Resultados da análise
            
        Returns:
            Analysis: Instância da análise salva
        """
        try:
            analysis = Analysis(
                user_id=user_id,
                patient_name=dados_paciente.get("nome", ""),
                patient_species=dados_paciente.get("especie", ""),
                patient_breed=dados_paciente.get("raca", ""),
                patient_age=dados_paciente.get("idade", ""),
                patient_sex=dados_paciente.get("sexo", ""),
                owner_name=dados_paciente.get("tutor", ""),
                hemogram_data=json.dumps(dados_hemograma),
                analysis_results=json.dumps(resultados_analise)
            )
            
            db.session.add(analysis)
            db.session.commit()
            
            return analysis
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def obter_analises_usuario(user_id, limit=10):
        """
        Obtém as análises de um usuário específico.
        
        Args:
            user_id: ID do usuário
            limit: Limite de análises a retornar
            
        Returns:
            list: Lista de análises do usuário
        """
        return Analysis.query.filter_by(user_id=user_id).order_by(Analysis.created_at.desc()).limit(limit).all()

