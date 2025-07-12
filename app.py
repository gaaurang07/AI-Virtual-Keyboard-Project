from flask import Flask, render_template, Response
import cv2
import numpy as np

app = Flask(__name__)

# Keys Layout
keys = [
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
    ["Z", "X", "C", "V", "B", "N", "M", "<", "SPACE"]
]
key_w, key_h = 70, 70
key_spacing = 15
space_key_width = key_w * 2 + key_spacing
x_start = 200
y_start = 200

# Colors
keyboard_box_color = (50, 50, 50)
key_color = (150, 150, 150)
selected_color = (0, 255, 0)
text_color = (0, 0, 0)
border_color = (200, 200, 200)
final_text = ""

def gen_frames():
    global final_text
    # Placeholder: Browser se video stream ayega, abhi static frame banate hain
    while True:
        # Create a blank frame (1280x720)
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        
        # Draw Keyboard Background Box
        box_padding = 40
        cv2.rectangle(frame, (x_start - box_padding, y_start - box_padding),
                      (x_start + (10 * key_w + 9 * key_spacing) + box_padding, y_start + (3 * key_h + 2 * key_spacing) + box_padding),
                      keyboard_box_color, cv2.FILLED)
        
        # Draw Keys
        for row_idx, row in enumerate(keys):
            for col_idx, key in enumerate(row):
                x = x_start + col_idx * (key_w + key_spacing)
                y = y_start + row_idx * (key_h + key_spacing)
                key_box_w = space_key_width if key == "SPACE" else key_w
                cv2.rectangle(frame, (x, y), (x + key_box_w, y + key_h), key_color, cv2.FILLED)
                cv2.rectangle(frame, (x, y), (x + key_box_w, y + key_h), border_color, 2)
                cv2.putText(frame, key, (x + key_box_w // 2 - 10, y + key_h // 2 + 10), cv2.FONT_HERSHEY_SIMPLEX, 1, text_color, 2)
        
        # Typing Box
        text_box_y = y_start - 60
        text_box_width = 10 * key_w + 9 * key_spacing + 80
        text_box_height = 60
        cv2.rectangle(frame, (x_start - 40, text_box_y),
                      (x_start + text_box_width - 40, text_box_y + text_box_height), (0, 0, 0), cv2.FILLED)
        cv2.putText(frame, final_text + ("|" if int(time.time() * 2) % 2 == 0 else ""),
                    (x_start - 30, text_box_y + text_box_height // 2 + 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)