"""
Aplicativo Flask simplificado para testar rotas básicas.
Este arquivo é uma versão simplificada do app.py original,
sem modo debug e sem auto-reload para evitar deadlocks.
"""

from flask import Flask, jsonify, request
import urllib.parse

app = Flask(__name__)

@app.route('/')
def index():
    return "Servidor de teste funcionando!"

@app.route('/api/test')
def test_api():
    return jsonify({
        'success': True,
        'message': 'API de teste funcionando!'
    })

@app.route('/api/reference-values')
def test_reference_values():
    # Obter o parâmetro especie bruto
    especie_raw = request.args.get('especie', 'Cão')
    
    # Imprimir para debug
    print(f"Parâmetro especie bruto: '{especie_raw}', tipo: {type(especie_raw)}")
    print(f"Representação bytes: {[ord(c) for c in especie_raw]}")
    
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
    
    print(f"Espécie normalizada: '{especie_normalizada}'")
    
    valores = {
        'Cão': {
            'hemacias': '5.5-8.5 10⁶/µL',
            'hemoglobina': '12-18 g/dL',
            'hematocrito': '37-55 %',
            'vcm': '60-77 fL',
            'hcm': '19-24 pg',
            'chcm': '32-36 %',
            'leucocitos': '6000-17000 /µL',
            'segmentados': '3000-11500 /µL',
            'linfocitos': '1000-4800 /µL',
            'monocitos': '150-1350 /µL',
            'eosinofilos': '100-1250 /µL',
            'basofilos': '0-100 /µL',
            'plaquetas': '200000-500000 /µL',
            'proteina': '6.0-8.0 g/dL',
            'reticulocitos': '0-60000 /µL'
        },
        'Gato': {
            'hemacias': '5.0-10.0 10⁶/µL',
            'hemoglobina': '8-15 g/dL',
            'hematocrito': '24-45 %',
            'vcm': '39-55 fL',
            'hcm': '13-17 pg',
            'chcm': '30-36 %',
            'leucocitos': '5500-19500 /µL',
            'segmentados': '2500-12500 /µL',
            'linfocitos': '1500-7000 /µL',
            'monocitos': '0-850 /µL',
            'eosinofilos': '0-1500 /µL',
            'basofilos': '0-100 /µL',
            'plaquetas': '300000-700000 /µL',
            'proteina': '6.0-8.0 g/dL',
            'reticulocitos': '0-60000 /µL'
        }
    }
    
    # Verificar se conseguimos normalizar a espécie
    if especie_normalizada and especie_normalizada in valores:
        return jsonify({
            'success': True,
            'data': valores[especie_normalizada]
        })
    else:
        # Retornar valores para Cão como fallback para garantir que algo seja exibido
        return jsonify({
            'success': True,
            'data': valores['Cão'],
            'note': f'Espécie não reconhecida: "{especie_raw}". Usando valores padrão para Cão.'
        })

if __name__ == '__main__':
    print("Iniciando servidor Flask simplificado...")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
