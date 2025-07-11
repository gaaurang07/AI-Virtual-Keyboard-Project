#                           Libraries used
import cv2 # OpenCV library hai jo camera aur image processing ke liye use hoti hai.
import numpy as np # Math aur array handling ke liye, images ko matrix ke roop mein manage karta hai.
from cvzone.HandTrackingModule import HandDetector # Ek module jo haath detect karta hai aur unke landmarks (points) batata hai.
import time # Time delay ya timing ke liye use hoti hai.
import winsound # Sound play karne ke liye (Windows pe kaam karta hai).
from PIL import Image, ImageDraw, ImageFont # Images ko edit karne ke liye, yahan text draw karne mein use hoga.

#                           Web Cam
cap = cv2.VideoCapture(0) # Webcam ko on karta hai (0 matlab default camera).
if not cap.isOpened():
    print("Error: Webcam nahi khul rahi hai. Check karo!")
    exit()
cap.set(3, 1280) # Width ko 1280 pixels set karta hai.
cap.set(4, 720) # Height ko 720 pixels set karta hai (720p resolution).

cv2.namedWindow("Virtual keyboard", cv2.WND_PROP_FULLSCREEN) # Ek window banayi jati hai jiska naam "Virtual keyboard" hai aur yeh full-screen hogi.
cv2.setWindowProperty("Virtual keyboard", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

#                          Hand Detector
detector = HandDetector(detectionCon=0.8, maxHands=2)
# HandDetector: Haath detect karne ka object banaya.
# detectionCon=0.8: Confidence level 80% rakha, matlab haath tabhi detect hoga jab 80% sure ho.
# maxHands=2: Maximum 2 haath detect kar sakta hai (abhi code sirf 1st haath use karta hai).

#                           Keys Layout
keys = [
    (["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"], 0),
    (["A", "S", "D", "F", "G", "H", "J", "K", "L"], 0),
    (["Z", "X", "C", "V", "B", "N", "M", "<", "SPACE"], 0)
]
"""Ek list of tuples hai, har tuple mein ek row ke keys hain.
Pehli row: Q to P, doosri: A to L, teesri: Z to SPACE (SPACE bada button hai, < backspace ke liye).
0 ka matlab abhi koi state nahi (future mein shift ya caps ke liye use ho sakta hai)."""

#                           Appearance and Font
key_w, key_h = 70, 70
key_spacing = 15
space_key_width = key_w * 2 + key_spacing
font_path = "Orbitron/static/Orbitron-Bold.ttf"
font_size = 30
pil_font = ImageFont.truetype(font_path, font_size)
"""
key_w, key_h: Har key ka width aur height 70 pixels hai.
key_spacing: Keys ke beech 15 pixels ka gap.
space_key_width: SPACE key double size ka hai (140 + 15 = 155 pixels).
font_path: Font file ka path, yahan "Orbitron" font use ho raha hai (path adjust karna padega).
pil_font: Font ko PIL ke liye load kiya gaya taaki text draw ho sake.
"""

#                           Positioning
total_width = 10 * (key_w + key_spacing) - key_spacing
total_height = 3 * (key_h + key_spacing) + key_spacing
screen_width, screen_height = 1280, 720
x_start = (screen_width - total_width) // 2 + 100
y_start = (screen_height - total_height) // 2
"""
total_width: 10 keys + gaps ka total width (approx 835 pixels, note: 715 typo tha).
total_height: 3 rows + gaps ka total height (approx 255 pixels, note: 235 typo tha).
screen_width, screen_height: Screen ka size 1280x720.
x_start: Keyboard ko center mein shift kiya gaya + 100 pixels right.
y_start: Keyboard ko vertically center mein rakha gaya.
"""

#                           Colors
keyboard_box_color = (50, 50, 50) # Light Blue
key_fill_color = (50, 50, 50)    # White keys
text_color = (235, 206, 135)     # Black key text
border_color = (235, 206, 135)   # Black border
# RGB values mein colors define kiye (50, 50, 50 = dark gray, 235, 206, 135 = goldish).

#                           Text handling
final_text = ""
click_delay = 0.5 # Har click ke beech 0.5 seconds ka gap (tweakable).
last_click_time = 0 # Last click ka time track karta hai.

#                           Main Loop
while True:
    success, frame = cap.read()
    if not success: 
        print("Error: Frame nahi mil raha, webcam check karo!")
        break
    frame = cv2.flip(frame, 1)
    hands, frame = detector.findHands(frame, flipType=False)
    
    """while True: Ek infinite loop jo har frame ko process karta hai.
    cap.read(): Webcam se frame (image) leta hai, success batata hai ki frame mila ya nahi.
    break: Agar frame nahi mila toh loop band ho jata hai.
    cv2.flip(frame, 1): Image ko horizontally flip karta hai (mirror effect).
    detector.findHands(): Haath detect karta hai aur landmarks deta hai.
    """
    
    #                           Draw Keyboard Background Box
    box_padding = 40 
    cv2.rectangle(frame,
                  (x_start - box_padding, y_start - box_padding),
                  (x_start + total_width + box_padding, y_start + total_height + box_padding),
                  keyboard_box_color, cv2.FILLED)
    """box_padding: Keyboard ke aas-paas 40 pixels ka margin.
    cv2.rectangle: Ek rectangle banata hai jo keyboard ka background hai, keyboard_box_color se bhara hua.
    """
    
    #                           Hand Detection & Key Selection
    selected_key = None
    selected_coords = None
    distance = 999
    
    if hands:
        hand = hands[0]
        lmList = hand["lmList"]
        cx, cy = lmList[8][0], lmList[8][1] # Index finger tip
        thumb_tip = lmList[4][:2]
        index_tip = lmList[8][:2]
        distance = ((thumb_tip[0] - index_tip[0]) ** 2 + (thumb_tip[1] - index_tip[1]) ** 2) ** 0.5
        
        for row_idx, (row_key, _) in enumerate(keys):
            for col_idx, key in enumerate(row_key):
                x = x_start + col_idx * (key_w + key_spacing)
                y = y_start + row_idx * (key_h + key_spacing)
                key_box_w = space_key_width if key == "SPACE" else key_w
                if x < cx < x + key_box_w and y < cy < y + key_h:
                    selected_key = key
                    selected_coords = (x, y, key_box_w)   
    """selected_key, selected_coords, distance: Variables initialize kiye.
    if hands: Agar haath detect hua toh code chalega.
    hand = hands[0]: Pehla haath le liya (0 index).
    lmList: Haath ke 21 landmarks ki list, har landmark x, y coordinates deta hai.
    cx, cy: Index finger tip ka center (landmark 8).
    thumb_tip, index_tip: Thumb aur index finger ke tips.
    distance: Thumb aur index ke beech ki doori calculate ki gayi (Pythagoras theorem).
    for loops: Nested loops se har row aur har key check ki jati hai.
    x, y: Har key ka top-left corner calculate kiya.
    key_box_w: SPACE ke liye double width, warna normal.
    if condition: Agar finger tip key ke andar hai toh selected_key set ho jata hai.
    """
    
    #                           KEY PRESS LOGIC
    if selected_key and distance < 40 and time.time() - last_click_time > click_delay:
        if selected_key == "<":
            final_text = final_text[:-1]
        elif selected_key == "SPACE":
            final_text += " "
        else:
            final_text += selected_key
        # Add delay before playing sound
        time.sleep(0.2) # 0.2 seconds delay
        # Play typing sound for 0.5 second
        winsound.PlaySound("keyboard-typing-fast-371229.wav", winsound.SND_ASYNC | winsound.SND_LOOP)
        time.sleep(0.5) # Limit to 0.5 second
        winsound.PlaySound(None, winsound.SND_PURGE) # Stop sound
        last_click_time = time.time()
        
    """
    if condition: Agar key select hui, distance 40 se kam hai (gesture), aur last click se 0.5 seconds guzar chuke hain.
    Inner if-elif-else:
    "<": Backspace, text ka last character remove karta hai.
    "SPACE": Ek space add karta hai.
    Else: Selected key ka character text mein add hota hai.
    time.sleep(0.2): 0.2 seconds ki delay sound se pehle.
    winsound.PlaySound: Sound start karta hai, SND_ASYNC async play ke liye, SND_LOOP loop ke liye.
    time.sleep(0.5): 0.5 seconds ke liye sound chalega.
    winsound.PlaySound(None, SND_PURGE): Sound stop karta hai.
    last_click_time: Naya time update karta hai.
    """
    
    #                           Draw Keys
    for row_idx, (row_key, _) in enumerate(keys):
        for col_idx, key in enumerate(row_key):
            x = x_start + col_idx * (key_w + key_spacing)
            y = y_start + row_idx * (key_h + key_spacing)
            key_box_w = space_key_width if key == "SPACE" else key_w
            if selected_key == key and selected_coords and (x, y, key_box_w) == selected_coords:
                cv2.rectangle(frame, (x, y), (x + key_box_w, y + key_h), (0, 255, 0), cv2.FILLED)
            else:
                cv2.rectangle(frame, (x, y), (x + key_box_w, y + key_h), key_fill_color, cv2.FILLED)
            
            cv2.rectangle(frame, (x, y), (x + key_box_w, y + key_h), border_color, 2)

            # Use PIL for text
            key_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(key_pil)
            bbox = draw.textbbox((0, 0), key, font=pil_font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            text_x = x + (key_box_w - tw) // 2
            text_y = y + (key_h - th) // 2
            draw.text((text_x, text_y), key, fill=text_color, font=pil_font)
            frame = cv2.cvtColor(np.array(key_pil), cv2.COLOR_RGB2BGR)
    """Outer for: Har row ke liye.
    Inner for: Har key ke liye.
    x, y: Key ka position calculate kiya.
    if-else: Agar key selected hai toh green, warna normal color.
    cv2.rectangle: Key ka background aur border draw kiya.

    PIL Section:
    key_pil: Frame ko PIL image mein convert kiya.
    draw: Text draw karne ka object.
    bbox: Text ka size calculate kiya.
    text_x, text_y: Text ko center mein rakha.
    draw.text: Key ka text draw kiya.
    cv2.cvtColor: PIL image ko wapas OpenCV format mein convert kiya.
    """

    #                           TYPING BOX (just above keyboard)
    text_box_y = y_start - 60
    text_box_width = total_width + 80
    text_box_height = 60
    cv2.rectangle(frame, (x_start - 40, text_box_y),
                  (x_start + text_box_width - 40, text_box_y + text_box_height), (0, 0, 0), cv2.FILLED)
    """
    text_box_y: Typing area ko keyboard ke upar 60 pixels rakha.
    cv2.rectangle: Ek black box banaya typing ke liye.
    """

    #                           TYPING TEXT
    text_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(text_pil)
    display_text = final_text[-40:]
    if int(time.time() * 2) % 2 == 0:
        display_text += "|"
    bbox = draw.textbbox((0, 0), display_text, font=pil_font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    text_x = x_start - 20
    text_y = text_box_y + (text_box_height - th) // 2
    draw.text((text_x, text_y), display_text, fill=(255, 255, 255), font=pil_font)
    frame = cv2.cvtColor(np.array(text_pil), cv2.COLOR_RGB2BGR)
    """text_pil: Frame ko PIL ke liye ready kiya.
    display_text: Last 40 characters show karta hai.
    if condition: Har 0.5 second mein "|" (cursor) blink karta hai.
    bbox: Text ka size napa.
    text_x, text_y: Text ko center mein rakha.
    draw.text: White text draw kiya.
    cv2.cvtColor: Wapas OpenCV format mein convert kiya.                        
    """

    #                           Display & Exit
    cv2.imshow("Virtual keyboard", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break
    """cv2.imshow: Frame ko window mein dikhata hai.
    cv2.waitKey(1): 1 millisecond wait karta hai, ESC key (27) press hone pe loop break hota hai.
    """

#                           Cleanup
cap.release()
cv2.destroyAllWindows()
"""cap.release(): Webcam ko band karta hai.
cv2.destroyAllWindows(): Sab windows close karta hai.
"""
