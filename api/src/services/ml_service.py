import requests
import os

ML_SERVICE_URL = os.getenv('ML_SERVICE_URL', 'http://model_service:8002')

def check_ml_health():
    try:
        response = requests.get(f'{ML_SERVICE_URL}/health', timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f'Erro ao verificar ML service: {e}')
        return False

def get_model_info():
    try:
        response = requests.get(f'{ML_SERVICE_URL}/model-info', timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f'Erro ao buscar info do modelo: {e}')
        return None

def predict(features):
    try:
        response = requests.post(
            f'{ML_SERVICE_URL}/predict',
            json={'features': features},
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, response.json().get('error', 'Erro desconhecido')
    except Exception as e:
        print(f'Erro ao fazer predição: {e}')
        return None, str(e)
