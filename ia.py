import pandas as pd
import joblib
import json
import os
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler 
from sklearn.pipeline import Pipeline           
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, classification_report

print("Carregando configurações...")
config = {
    "model_name": "modelo_iris_knn.joblib",
    "config_name": "config.json",
    "test_size": 0.2,
    "random_state": 42,
    "n_neighbors": 3,
    "feature_names": None, 
    "target_names": None   
}

# Carregar os Dados
iris = load_iris()
X = iris.data
y = iris.target

# Salva os nomes das features e alvos na configuração
config["feature_names"] = iris.feature_names
config["target_names"] = list(iris.target_names) # Converte para lista p/ JSON

print(f"Dataset carregado. Features: {config['feature_names']}")
print(f"Alvos: {config['target_names']}\n")

# Dividir os Dados (usando a config)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    test_size=config['test_size'], 
    random_state=config['random_state']
)

print(f"Dados divididos: {len(X_train)} para treino, {len(X_test)} para teste.\n")


steps = [
    ('scaler', StandardScaler()), # Padronizar os dados
    ('knn', KNeighborsClassifier(n_neighbors=config['n_neighbors'])) # Rodar o KNN
]

# Cria o pipeline
pipeline_model = Pipeline(steps)

print("Iniciando o treinamento do Pipeline (Scaler + KNN)...")
# Treina o pipeline inteiro 
pipeline_model.fit(X_train, y_train)
print("Treinamento concluído!\n")

# Avaliar o Pipeline
print("Avaliando o pipeline com os dados de teste...")
y_pred = pipeline_model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print("--- Relatório da Avaliação ---")
print(f"Acurácia: {accuracy * 100:.2f}%")
print("\nRelatório de Classificação:\n", classification_report(y_test, y_pred, target_names=config['target_names']))


# Salva o Pipeline inteiro (o scaler e o knn juntos)
joblib.dump(pipeline_model, config['model_name'])
print(f"--- Modelo Salvo ---")
print(f"Pipeline treinado foi salvo como: {config['model_name']}\n")

# Salva o arquivo de configuração JSON
with open(config['config_name'], 'w') as f:
    json.dump(config, f, indent=4)
print(f"Configurações salvas como: {config['config_name']}\n")


# --- Teste de Previsão ---
flor_nova = [[6.4, 3.7, 4.1, 3.3]]
previsao = pipeline_model.predict(flor_nova)
previsao_nome = config['target_names'][previsao[0]]

print(f"--- Teste de Previsão ---")
print(f"Previsão para a flor {flor_nova}:")
print(f"Índice previsto: {previsao[0]}")
print(f"Nome da espécie: {previsao_nome}")