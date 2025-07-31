"""
Script para testar o algoritmo de interpretação de hemograma e geração de laudos.
"""

from app import create_app
from services.analysis_service import AnalysisService
from services.report_service import ReportService
import json
import os

def main():
    """Função principal para testar o algoritmo de interpretação e geração de laudos."""
    app = create_app()
    
    with app.app_context():
        print("=== Teste do Algoritmo de Interpretação de Hemograma e Geração de Laudos ===\n")
        
        # Casos de teste para diferentes condições
        casos_teste = [
            {
                "nome": "Anemia Leve em Cão",
                "dados": {
                    "especie": "Cão",
                    "hemacias": 5.0,
                    "hemoglobina": 11.0,
                    "hematocrito": 35.0,
                    "vcm": 70.0,
                    "hcm": 22.0,
                    "chcm": 33.0,
                    "reticulocitos": 50.0,
                    "leucocitos": 10000.0,
                    "segmentados": 6000.0,
                    "linfocitos": 3000.0,
                    "monocitos": 800.0,
                    "eosinofilos": 500.0,
                    "basofilos": 50.0,
                    "plaquetas": 300000.0,
                    "proteina": 7.0
                },
                "paciente": {
                    "nome_paciente": "Rex",
                    "especie": "Cão",
                    "raca": "Labrador",
                    "idade": "5 anos",
                    "sexo": "Macho",
                    "nome_tutor": "João Silva"
                }
            },
            {
                "nome": "Anemia Grave com Resposta Regenerativa em Gato",
                "dados": {
                    "especie": "Gato",
                    "hemacias": 3.0,
                    "hemoglobina": 6.0,
                    "hematocrito": 14.0,
                    "vcm": 45.0,
                    "hcm": 15.0,
                    "chcm": 33.0,
                    "reticulocitos": 100.0,
                    "leucocitos": 15000.0,
                    "segmentados": 10000.0,
                    "linfocitos": 3000.0,
                    "monocitos": 500.0,
                    "eosinofilos": 800.0,
                    "basofilos": 50.0,
                    "plaquetas": 250000.0,
                    "proteina": 6.5
                },
                "paciente": {
                    "nome_paciente": "Luna",
                    "especie": "Gato",
                    "raca": "SRD",
                    "idade": "3 anos",
                    "sexo": "Fêmea",
                    "nome_tutor": "Maria Oliveira"
                }
            },
            {
                "nome": "Infecção Bacteriana Aguda em Cão",
                "dados": {
                    "especie": "Cão",
                    "hemacias": 6.0,
                    "hemoglobina": 14.0,
                    "hematocrito": 42.0,
                    "vcm": 70.0,
                    "hcm": 22.0,
                    "chcm": 33.0,
                    "reticulocitos": 50.0,
                    "leucocitos": 25000.0,
                    "segmentados": 20000.0,
                    "linfocitos": 3000.0,
                    "monocitos": 1000.0,
                    "eosinofilos": 500.0,
                    "basofilos": 50.0,
                    "plaquetas": 300000.0,
                    "proteina": 7.0
                },
                "paciente": {
                    "nome_paciente": "Thor",
                    "especie": "Cão",
                    "raca": "Golden Retriever",
                    "idade": "4 anos",
                    "sexo": "Macho",
                    "nome_tutor": "Carlos Santos"
                }
            },
            {
                "nome": "Trombocitopenia Grave em Gato",
                "dados": {
                    "especie": "Gato",
                    "hemacias": 6.0,
                    "hemoglobina": 12.0,
                    "hematocrito": 35.0,
                    "vcm": 45.0,
                    "hcm": 15.0,
                    "chcm": 33.0,
                    "reticulocitos": 30.0,
                    "leucocitos": 12000.0,
                    "segmentados": 8000.0,
                    "linfocitos": 3000.0,
                    "monocitos": 500.0,
                    "eosinofilos": 800.0,
                    "basofilos": 50.0,
                    "plaquetas": 30000.0,
                    "proteina": 6.5
                },
                "paciente": {
                    "nome_paciente": "Mia",
                    "especie": "Gato",
                    "raca": "Siamês",
                    "idade": "2 anos",
                    "sexo": "Fêmea",
                    "nome_tutor": "Ana Pereira"
                }
            },
            {
                "nome": "Hemograma Normal em Cão",
                "dados": {
                    "especie": "Cão",
                    "hemacias": 7.0,
                    "hemoglobina": 15.0,
                    "hematocrito": 45.0,
                    "vcm": 70.0,
                    "hcm": 22.0,
                    "chcm": 33.0,
                    "reticulocitos": 50.0,
                    "leucocitos": 10000.0,
                    "segmentados": 6000.0,
                    "linfocitos": 3000.0,
                    "monocitos": 800.0,
                    "eosinofilos": 500.0,
                    "basofilos": 50.0,
                    "plaquetas": 300000.0,
                    "proteina": 7.0
                },
                "paciente": {
                    "nome_paciente": "Max",
                    "especie": "Cão",
                    "raca": "Beagle",
                    "idade": "3 anos",
                    "sexo": "Macho",
                    "nome_tutor": "Pedro Costa"
                }
            }
        ]
        
        # Informações da clínica para os laudos
        clinic_info = {
            "nome": "Clínica Veterinária Exemplo",
            "endereco": "Rua Exemplo, 123 - São Paulo/SP",
            "telefone": "(11) 1234-5678",
            "email": "contato@clinicaexemplo.com.br",
            "crmv": "CRMV-SP 12345"
        }
        
        # Diretório para salvar os laudos gerados
        output_dir = os.path.join(os.getcwd(), "laudos_teste")
        os.makedirs(output_dir, exist_ok=True)
        
        # Testar cada caso
        for i, caso in enumerate(casos_teste):
            print(f"\n--- Caso {i+1}: {caso['nome']} ---")
            
            # Analisar hemograma
            success, message, result = AnalysisService.analyze_hemogram(
                user_id=1,  # ID fictício para teste
                hemogram_data=caso["dados"],
                patient_info=caso["paciente"]
            )
            
            if not success:
                print(f"Erro na análise: {message}")
                continue
            
            # Exibir diagnósticos
            print("Diagnósticos:")
            for diagnostico in result["diagnostico"]["diagnosticos"]:
                print(f"- {diagnostico}")
            
            # Exibir explicações para tutores
            print("\nExplicações para tutores:")
            for explicacao in result["diagnostico"]["explicacoes"]:
                print(f"- {explicacao['para_tutor'][:100]}...")
            
            # Gerar laudos
            try:
                # Laudo técnico
                technical_path = ReportService.generate_technical_report(
                    analysis_data=result["diagnostico"],
                    patient_info=caso["paciente"],
                    clinic_info=clinic_info
                )
                
                if technical_path:
                    tech_output = os.path.join(output_dir, f"laudo_tecnico_{i+1}.pdf")
                    os.rename(technical_path, tech_output)
                    print(f"\nLaudo técnico gerado: {tech_output}")
                
                # Laudo simplificado
                simplified_path = ReportService.generate_simplified_report(
                    analysis_data=result["diagnostico"],
                    patient_info=caso["paciente"],
                    clinic_info=clinic_info
                )
                
                if simplified_path:
                    simp_output = os.path.join(output_dir, f"laudo_simplificado_{i+1}.pdf")
                    os.rename(simplified_path, simp_output)
                    print(f"Laudo simplificado gerado: {simp_output}")
                
            except Exception as e:
                print(f"Erro ao gerar laudos: {str(e)}")
        
        print("\n=== Teste concluído ===")
        print(f"Laudos gerados no diretório: {output_dir}")

if __name__ == "__main__":
    main()
