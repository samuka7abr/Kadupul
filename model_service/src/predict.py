import numpy as np

def make_prediction(pipeline_model, features, config):
    """
    Realiza a predição usando o pipeline treinado.
    
    Args:
        pipeline_model: Pipeline do scikit-learn
        features: Lista com as 4 features da flor
        config: Dicionário com as configurações
    
    Returns:
        dict: Resultado da predição
    """
    features_array = np.array(features).reshape(1, -1)
    prediction = pipeline_model.predict(features_array)
    prediction_proba = pipeline_model.predict_proba(features_array)
    
    class_index = int(prediction[0])
    class_name = config["target_names"][class_index]
    
    result = {
        "prediction_index": class_index,
        "prediction_name": class_name,
        "probabilities": {
            config["target_names"][i]: float(prob)
            for i, prob in enumerate(prediction_proba[0])
        },
        "features": {
            config["feature_names"][i]: float(features[i])
            for i in range(len(features))
        }
    }
    
    return result
