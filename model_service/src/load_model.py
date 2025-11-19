import joblib
import json
import os

def load_model_and_config():
    """
    Carrega o modelo treinado e as configurações do arquivo JSON.
    
    Returns:
        tuple: (pipeline_model, config_dict)
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_dir, "modelo_iris_knn.joblib")
    config_path = os.path.join(current_dir, "config.json")
    
    print(f"Carregando modelo de: {model_path}")
    pipeline_model = joblib.load(model_path)
    print("✓ Modelo carregado com sucesso!")
    
    print(f"Carregando configurações de: {config_path}")
    with open(config_path, "r") as f:
        config = json.load(f)
    print("✓ Configurações carregadas com sucesso!")
    
    return pipeline_model, config
