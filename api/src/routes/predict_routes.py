from flask import Blueprint, request, jsonify
import hashlib
import json
from services.ml_service import predict
from services.mongo_service import save_prediction, get_predictions, get_prediction_by_id, get_stats
from services.redis_service import get_cached_prediction, cache_prediction, increment_prediction_count

predict_bp = Blueprint('predict', __name__)

def generate_features_key(features):
    features_str = json.dumps(features, sort_keys=True)
    return hashlib.md5(features_str.encode()).hexdigest()

@predict_bp.route('/api/predict', methods=['POST'])
def make_prediction():
    
    if not request.json or 'features' not in request.json:
        return jsonify({'error': 'Campo features é obrigatório'}), 400
    
    features = request.json['features']
    
    if not isinstance(features, list) or len(features) != 4:
        return jsonify({'error': 'Features deve ser uma lista com 4 valores numéricos'}), 400
    
    try:
        features = [float(f) for f in features]
    except (ValueError, TypeError):
        return jsonify({'error': 'Todas as features devem ser números'}), 400
    
    cache_key = generate_features_key(features)
    
    cached_result = get_cached_prediction(cache_key)
    if cached_result:
        increment_prediction_count()
        return jsonify({
            'result': cached_result,
            'source': 'cache'
        }), 200
    
    result, error = predict(features)
    
    if error:
        return jsonify({'error': f'Erro no modelo: {error}'}), 500
    
    pred_id = save_prediction(features, result)
    
    cache_prediction(cache_key, result)
    
    increment_prediction_count()
    
    return jsonify({
        'result': result,
        'prediction_id': pred_id,
        'source': 'model'
    }), 200

@predict_bp.route('/api/predictions', methods=['GET'])
def list_predictions():
    """Lista últimas predições"""
    limit = request.args.get('limit', 10, type=int)
    predictions = get_predictions(limit)
    
    return jsonify({
        'predictions': predictions,
        'count': len(predictions)
    }), 200

@predict_bp.route('/api/predictions/<pred_id>', methods=['GET'])
def get_prediction_detail(pred_id):
    """Retorna detalhes de uma predição"""
    prediction = get_prediction_by_id(pred_id)
    
    if not prediction:
        return jsonify({'error': 'Predição não encontrada'}), 404
    
    return jsonify(prediction), 200

@predict_bp.route('/api/stats', methods=['GET'])
def get_statistics():
    """Retorna estatísticas das predições"""
    stats = get_stats()
    
    if not stats:
        return jsonify({'error': 'Erro ao buscar estatísticas'}), 500
    
    return jsonify(stats), 200
