"""
Flask server with MLE inference
"""

import os
from flask import Flask, request, jsonify
import numpy as np
import mle_runtime

app = Flask(__name__)

# Initialize engine
engine = mle_runtime.MLEEngine(mle_runtime.Device.CPU)
model_loaded = False


def init_model():
    """Load model on startup"""
    global model_loaded
    
    try:
        model_path = os.environ.get('MODEL_PATH', 'model.mle')
        engine.load_model(model_path)
        model_loaded = True
        
        print('Model loaded successfully')
        metadata = engine.metadata
        if metadata:
            print(f'Model: {metadata.model_name}')
            print(f'Framework: {metadata.framework}')
    except Exception as e:
        print(f'Failed to load model: {e}')
        exit(1)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model_loaded,
        'memory': engine.peak_memory_usage()
    })


@app.route('/predict', methods=['POST'])
def predict():
    """Prediction endpoint"""
    if not model_loaded:
        return jsonify({'error': 'Model not loaded'}), 503
    
    try:
        data = request.get_json()
        features = data.get('features')
        
        if not isinstance(features, list):
            return jsonify({'error': 'features must be an array'}), 400
        
        input_data = np.array(features, dtype=np.float32).reshape(1, -1)
        outputs = engine.run([input_data])
        
        return jsonify({
            'prediction': outputs[0].tolist(),
            'memory': engine.peak_memory_usage()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    init_model()
    
    port = int(os.environ.get('PORT', 5000))
    print(f'Inference server running on port {port}')
    print(f'Try: curl -X POST http://localhost:{port}/predict -H "Content-Type: application/json" -d \'{{"features":[1,2,3,4]}}\'')
    
    app.run(host='0.0.0.0', port=port)
