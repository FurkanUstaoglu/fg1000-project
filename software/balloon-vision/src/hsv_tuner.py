import cv2
import numpy as np
import math
import pyrealsense2 as rs

# --- RealSense pipeline başlatma ---
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipeline.start(config)

# --- HSV aralıkları (sen trackbar ile bulduğun değerleri buraya yazacaksın) ---
lower_red1 = np.array([0, 120, 70])
upper_red1 = np.array([10, 255, 255])
lower_red2 = np.array([170, 120, 70])
upper_red2 = np.array([180, 255, 255])

lower_green = np.array([40, 60, 60])
upper_green = np.array([85, 255, 255])

MIN_AREA = 800
MAX_AREA = 5000
CIRCULARITY_THRESH = 0.5

def circularity(contour):
    area = cv2.contourArea(contour)
    peri = cv2.arcLength(contour, True)
    if peri == 0:
        return 0
    return 4 * math.pi * area / (peri * peri)

def process_mask(mask, frame, depth_frame, color_label):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < MIN_AREA or area > MAX_AREA:
            continue
        circ = circularity(cnt)
        if circ < CIRCULARITY_THRESH:
            continue
        x,y,w,h = cv2.boundingRect(cnt)
        cx,cy = x+w//2, y+h//2

        # --- Derinlik bilgisi ---
        depth_value = depth_frame.get_distance(cx, cy)  # metre cinsinden
        if depth_value == 0:  # ölçüm yoksa atla
            continue

        # --- Görsel işaretleme ---
        cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0) if color_label=='friend' else (0,0,255), 2)
        cv2.circle(frame, (cx,cy), 5, (255,0,0), -1)
        label = "FRIEND (Müttefik)" if color_label=='friend' else "ENEMY (Düşman)"
        cv2.putText(frame, f"{label} D:{depth_value:.2f}m", (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

while True:
    frames = pipeline.wait_for_frames()
    depth_frame = frames.get_depth_frame()
    color_frame = frames.get_color_frame()
    if not depth_frame or not color_frame:
        continue

    frame = np.asanyarray(color_frame.get_data())
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask_r = cv2.inRange(hsv, lower_red1, upper_red1) | cv2.inRange(hsv, lower_red2, upper_red2)
    mask_g = cv2.inRange(hsv, lower_green, upper_green)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7,7))
    mask_r = cv2.morphologyEx(mask_r, cv2.MORPH_CLOSE, kernel)
    mask_r = cv2.morphologyEx(mask_r, cv2.MORPH_OPEN, kernel)
    mask_g = cv2.morphologyEx(mask_g, cv2.MORPH_CLOSE, kernel)
    mask_g = cv2.morphologyEx(mask_g, cv2.MORPH_OPEN, kernel)

    process_mask(mask_r, frame, depth_frame, 'enemy')
    process_mask(mask_g, frame, depth_frame, 'friend')

    cv2.imshow("frame", frame)
    cv2.imshow("mask_red", mask_r)
    cv2.imshow("mask_green", mask_g)

    if cv2.waitKey(1) & 0xFF == 27:
        break

pipeline.stop()
cv2.destroyAllWindows()
