from flask import Flask, request, jsonify
from load_model import load_model_and_config
from predict import make_prediction

app = Flask(__name__)

print("\n" + "=" * 50)
print("ML Server Up")
print("=" * 50 + "\n")

pipeline_model, config = load_model_and_config()

print(f"Modelo: {config['model_name']}")
print(f"Algoritmo: KNN (k={config['n_neighbors']})")
print("\n" + "=" * 50)
print("✓ Serviço pronto!")
print("=" * 50 + "\n")


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'ML Inference Service',
        'model': config['model_name']
    }), 200


@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json(force=True, silent=True)

        if not data or 'features' not in data:
            return jsonify({'error': 'Formato inválido: esperado JSON com chave "features".'}), 400

        features = data['features']

        if not isinstance(features, list):
            return jsonify({'error': 'As features devem ser uma lista.'}), 400

        if len(features) != 4:
            return jsonify({'error': 'Esperado um vetor com exatamente 4 features.'}), 400

        result = make_prediction(pipeline_model, features, config)
        print(f"✓ Predição: {result.get('prediction_name')}")
        return jsonify(result), 200

    except Exception as e:
        print(f"❌ Erro na predição: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/model-info', methods=['GET'])
def model_info():
    return jsonify({
        'model_name': config['model_name'],
        'algorithm': 'KNN',
        'n_neighbors': config['n_neighbors'],
        'feature_names': config['feature_names'],
        'target_names': config['target_names']
    }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8002, debug=True)
