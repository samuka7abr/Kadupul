from flask import Blueprint, jsonify
from services.mongo_service import mongo_client
from services.redis_service import redis_client
from services.ml_service import check_ml_health

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    
    status = {
        'api': 'healthy',
        'mongodb': 'disconnected',
        'redis': 'disconnected',
        'ml_service': 'disconnected'
    }
    
    try:
        if mongo_client:
            mongo_client.admin.command('ping')
            status['mongodb'] = 'healthy'
    except:
        pass
    
    try:
        if redis_client:
            redis_client.ping()
            status['redis'] = 'healthy'
    except:
        pass
    
    if check_ml_health():
        status['ml_service'] = 'healthy'
    
    all_healthy = all(v == 'healthy' for v in status.values())
    
    return jsonify({
        'status': 'healthy' if all_healthy else 'degraded',
        'services': status
    }), 200 if all_healthy else 503
