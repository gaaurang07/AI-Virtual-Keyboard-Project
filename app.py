from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
import os

app = Flask(__name__)
detector = HandDetector(detectionCon=0.8, maxHands=1, modelComplexity=0)  # 👈 fix added here

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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
