from flask import Flask, jsonify
from routes.health_routes import health_bp
from routes.predict_routes import predict_bp
from services.mongo_service import init_mongo, close_mongo
from services.redis_service import init_redis, close_redis
import atexit
import sys

app = Flask(__name__)

app.config['JSON_SORT_KEYS'] = False

print('=' * 50)
print('Inicializando Kadupul API')
print('=' * 50)

mongo_ok = init_mongo()
redis_ok = init_redis()

if not mongo_ok or not redis_ok:
    print('⚠️Alguns serviços falharam ao inicializar⚠️')
    print('A API continuará funcionando em modo degradado')

print('\n' + '=' * 50)
print('Registrando rotas...')

app.register_blueprint(health_bp)
app.register_blueprint(predict_bp)

print('✓ Rotas registradas!')
print('=' * 50)

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint não encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/')
def index():
    return jsonify({
        'service': 'Kadupul API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health',
            'predict': '/api/predict',
            'predictions': '/api/predictions',
            'prediction_detail': '/api/predictions/<id>',
            'stats': '/api/stats'
        }
    }), 200

def cleanup():
    print('\nDesconectando serviços...')
    close_mongo()
    close_redis()
    print('Serviços desconectados. Até logo!')

atexit.register(cleanup)

if __name__ == '__main__':
    try:
        print('\nIniciando servidor na porta 8001...')
        app.run(host='0.0.0.0', port=8001, debug=False)
    except KeyboardInterrupt:
        print('\nServidor interrompido pelo usuário')
        sys.exit(0)
