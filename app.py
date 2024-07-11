import os
import numpy as np
import librosa
import tensorflow as tf
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Desactivar optimizaciones de TensorFlow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_DISABLE_MKL'] = '1'

app = Flask(__name__, static_folder='build')
CORS(app)  # Esto permite todas las solicitudes CORS

# Crear el directorio 'uploads' si no existe
if not os.path.exists('uploads'):
    os.makedirs('uploads')

# Cargar el modelo TensorFlow Lite
interpreter = tf.lite.Interpreter(model_path='model.tflite')
interpreter.allocate_tensors()

# Obtener detalles de entrada y salida
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

def process_audio(file_path):
    y, sr = librosa.load(file_path, sr=1000, duration=1.2)
    y = librosa.util.fix_length(y, size=1200)
    y = y / np.max(np.abs(y))
    return y.reshape(1, len(y), 1).astype(np.float32)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    file_path = os.path.join('uploads', file.filename)
    file.save(file_path)
    processed_audio = process_audio(file_path)
    try:
        interpreter.set_tensor(input_details[0]['index'], processed_audio)
        interpreter.invoke()
        prediction = interpreter.get_tensor(output_details[0]['index'])
        return jsonify(prediction.tolist()[0])
    except Exception as e:
        return str(e), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
