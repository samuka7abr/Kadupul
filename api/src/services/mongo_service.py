from pymongo import MongoClient
from datetime import datetime
import os

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://mongodb:27017/')
MONGO_DB = os.getenv('MONGO_DB', 'kadupul_db')

mongo_client = None
db = None
predictions_collection = None

def init_mongo():
    global mongo_client, db, predictions_collection
    
    try:
        print(f'Conectando ao MongoDB: {MONGO_URI}')
        mongo_client = MongoClient(MONGO_URI)
        
        mongo_client.admin.command('ping')
        print('MongoDB conectado!')
        
        db = mongo_client[MONGO_DB]
        predictions_collection = db['predictions']
        
        predictions_collection.create_index('timestamp')
        predictions_collection.create_index('prediction_name')
        print('Índices criados!')
        
        return True
    except Exception as e:
        print(f'Erro ao conectar: {e}')
        return False

def save_prediction(features, result):
    try:
        doc = {
            'features': features,
            'prediction_index': result['prediction_index'],
            'prediction_name': result['prediction_name'],
            'probabilities': result['probabilities'],
            'timestamp': datetime.utcnow()
        }
        
        result = predictions_collection.insert_one(doc)
        return str(result.inserted_id)
    except Exception as e:
        print(f'Erro ao salvar predição: {e}')
        return None

def get_predictions(limit=10):
    try:
        predictions = list(predictions_collection.find()
                          .sort('timestamp', -1)
                          .limit(limit))
        
        for pred in predictions:
            pred['_id'] = str(pred['_id'])
            pred['timestamp'] = pred['timestamp'].isoformat()
        
        return predictions
    except Exception as e:
        print(f'Erro ao buscar predições: {e}')
        return []

def get_prediction_by_id(pred_id):
    try:
        from bson.objectid import ObjectId
        prediction = predictions_collection.find_one({'_id': ObjectId(pred_id)})
        
        if prediction:
            prediction['_id'] = str(prediction['_id'])
            prediction['timestamp'] = prediction['timestamp'].isoformat()
        
        return prediction
    except Exception as e:
        print(f'Erro ao buscar predição: {e}')
        return None

def get_stats():
    try:
        total = predictions_collection.count_documents({})
        
        pipeline = [
            {'$group': {
                '_id': '$prediction_name',
                'count': {'$sum': 1}
            }}
        ]
        
        by_class = list(predictions_collection.aggregate(pipeline))
        
        return {
            'total_predictions': total,
            'by_class': {item['_id']: item['count'] for item in by_class}
        }
    except Exception as e:
        print(f'Erro ao buscar estatísticas: {e}')
        return None

def close_mongo():
    global mongo_client
    if mongo_client:
        mongo_client.close()
        print('MongoDB desconectado')
