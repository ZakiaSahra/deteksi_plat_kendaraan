import os
import cv2
import numpy as np
import base64
from flask import Flask, request, jsonify, render_template
from ultralytics import YOLO


# Import custom modules
from src.preprocessing import preprocess_plate
from src.ocr_and_classification import run_ocr_pipeline

app = Flask(__name__)

# Load YOLO model
MODEL_PATH = 'models/best.pt'
try:
    model = YOLO(MODEL_PATH)
    print("YOLO model loaded successfully.")
except Exception as e:
    print(f"Failed to load YOLO model from {MODEL_PATH}: {e}")
    model = None

def get_base64_image(img):
    """Convert numpy image to base64 string for HTML display"""
    _, buffer = cv2.imencode('.jpg', img)
    img_str = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/jpeg;base64,{img_str}"

@app.route('/')
def index():
    """Render the main UI page."""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """API endpoint to receive image and return predictions."""
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
        
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No image selected'}), 400

    import time
    start_time = time.time()
    
    try:
        # Read the image from bytes
        file_bytes = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'error': 'Invalid image format'}), 400

        if model is None:
            return jsonify({'error': 'Model not loaded on server'}), 500

        # Original image for frontend background
        orig_h, orig_w = img.shape[:2]
        full_img_b64 = get_base64_image(img)

        # 1. YOLO Detection - threshold diturunkan agar lebih sensitif deteksi plat variasi
        results = model(img, conf=0.15)
        
        detections = []
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                
                # Ekspansi bounding box: horizontal 5%, vertikal 5%
                # Diperluas sedikit saja agar huruf pertama tidak terpotong namun background tidak terlalu banyak masuk
                pad_x = int((x2 - x1) * 0.05)
                pad_y = int((y2 - y1) * 0.05)
                x1_exp = max(0, x1 - pad_x)
                y1_exp = max(0, y1 - pad_y)
                x2_exp = min(orig_w, x2 + pad_x)
                y2_exp = min(orig_h, y2 + pad_y)
                
                # Crop Plate dengan area yang sudah diperluas
                plate_img = img[y1_exp:y2_exp, x1_exp:x2_exp]
                
                # 2. Preprocessing
                preprocessed_plate = preprocess_plate(plate_img)
                
                # 3. OCR & Classification
                status, text = run_ocr_pipeline(preprocessed_plate)
                
                # Bounding box percentages for frontend drawing
                bbox_pct = {
                    'x': (x1 / orig_w) * 100,
                    'y': (y1 / orig_h) * 100,
                    'width': ((x2 - x1) / orig_w) * 100,
                    'height': ((y2 - y1) / orig_h) * 100
                }
                
                detections.append({
                    'text': text,
                    'status': status,
                    'conf': round(conf * 100, 1),
                    'bbox': bbox_pct
                })

        process_time_ms = int((time.time() - start_time) * 1000)

        if not detections:
            return jsonify({
                'message': 'Tidak ada plat nomor yang terdeteksi',
                'detections': [],
                'processing_time': process_time_ms,
                'full_image': full_img_b64
            })
            
        return jsonify({
            'message': 'Deteksi berhasil',
            'detections': detections,
            'processing_time': process_time_ms,
            'full_image': full_img_b64
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Run the app locally (Spaces will use `flask run`)
    app.run(host='0.0.0.0', port=7860, debug=True)
