import redis
import json
import os

REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_EXPIRE_TIME = int(os.getenv('REDIS_EXPIRE_TIME', 3600))  # 1 hora

redis_client = None

def init_redis():
    global redis_client
    
    try:
        print(f'Conectando ao Redis: {REDIS_HOST}:{REDIS_PORT}')
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True
        )
        
        # Testa a conexão
        redis_client.ping()
        print('Redis conectado!')
        
        return True
    except Exception as e:
        print(f'Erro ao conectar: {e}')
        return False

def get_cached_prediction(features_key):
    """Busca predição no cache"""
    try:
        cached = redis_client.get(f'prediction:{features_key}')
        if cached:
            return json.loads(cached)
        return None
    except Exception as e:
        print(f'Erro ao buscar cache: {e}')
        return None

def cache_prediction(features_key, result):
    try:
        redis_client.setex(
            f'prediction:{features_key}',
            REDIS_EXPIRE_TIME,
            json.dumps(result)
        )
        return True
    except Exception as e:
        print(f'Erro ao salvar cache: {e}')
        return False

def increment_prediction_count():
    try:
        return redis_client.incr('prediction_count')
    except Exception as e:
        print(f'Erro ao incrementar contador: {e}')
        return None

def get_prediction_count():
    try:
        count = redis_client.get('prediction_count')
        return int(count) if count else 0
    except Exception as e:
        print(f'Erro ao buscar contador: {e}')
        return 0

def clear_cache():
    try:
        redis_client.flushdb()
        print('Cache limpo!')
        return True
    except Exception as e:
        print(f'Erro ao limpar cache: {e}')
        return False

def close_redis():
    global redis_client
    if redis_client:
        redis_client.close()
        print('Redis desconectado')
