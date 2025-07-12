from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
import os  # ✅ added for dynamic port access

app = Flask(__name__)
detector = HandDetector(detectionCon=0.8, maxHands=1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    file = request.files['image']
    npimg = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    hands, img = detector.findHands(img)
    if hands:
        return jsonify({'result': 'Hand Detected'})
    else:
        return jsonify({'result': 'No Hand'})

# ✅ this part is important for Render to detect the app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # get port from Render
    app.run(host='0.0.0.0', port=port, debug=True)
