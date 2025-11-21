from flask import Blueprint, jsonify
from services.mongo_service import mongo_client
from services.redis_service import redis_client
from services.ml_service import check_ml_health

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Verifica saúde de todos os serviços"""
    
    status = {
        'api': 'healthy',
        'mongodb': 'disconnected',
        'redis': 'disconnected',
        'ml_service': 'disconnected'
    }
    
    # Verifica MongoDB
    try:
        if mongo_client:
            mongo_client.admin.command('ping')
            status['mongodb'] = 'healthy'
    except:
        pass
    
    # Verifica Redis
    try:
        if redis_client:
            redis_client.ping()
            status['redis'] = 'healthy'
    except:
        pass
    
    # Verifica ML Service
    if check_ml_health():
        status['ml_service'] = 'healthy'
    
    # Define status geral
    all_healthy = all(v == 'healthy' for v in status.values())
    
    return jsonify({
        'status': 'healthy' if all_healthy else 'degraded',
        'services': status
    }), 200 if all_healthy else 503
