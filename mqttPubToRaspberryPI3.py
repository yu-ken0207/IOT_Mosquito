# Publisher
import cv2
import torch
from ultralytics import YOLO
import numpy as np
import paho.mqtt.client as mqtt
import json


# 加載 YOLOv8 模型
model = YOLO('runs/detect/train/weights/best.pt')  # 替換為您的模型路徑

# 創建 CSRT 追蹤器
tracker = cv2.TrackerCSRT_create()
tracking = False

# 打開攝像頭
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

# MQTT 設置
TopicServerIP = "test.mosquitto.org"
TopicServerPort = 1883
TopicName = "TrackingCenter"

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1,"python_pub")
mqttc.connect(TopicServerIP, TopicServerPort)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Cannot receive frame")
        break
    
    # 調整幀的大小以加快處理速度
    frame = cv2.resize(frame, (1000, 800))

    # 計算畫面中心座標
    frame_center_x = frame.shape[1] // 2
    frame_center_y = frame.shape[0] // 2
    frame_center = [frame_center_x, frame_center_y]
    
    # 顯示畫面中心座標
    cv2.circle(frame, (frame_center_x, frame_center_y), 5, (255, 0, 0), -1)
    cv2.putText(frame, f'Center: {frame_center}', (frame_center_x - 50, frame_center_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    
    if not tracking:
        # 使用 YOLOv8 模型進行物體檢測
        results = model(frame)

        # 獲取檢測結果
        for result in results:
            boxes = result.boxes.xyxy.cpu().numpy()
            confidences = result.boxes.conf.cpu().numpy()
            class_ids = result.boxes.cls.cpu().numpy()

            for box, confidence, class_id in zip(boxes, confidences, class_ids):
                # 假設 '0' 是昆蟲的類別索引，調整為您的實際類別索引
                if class_id in [0, 1, 2, 3] and confidence > 0.5:
                    x1, y1, x2, y2 = map(int, box)
                    w, h = x2 - x1, y2 - y1
                    area = (x1, y1, w, h)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f'Insect {confidence:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    tracker.init(frame, area)  # 初始化追蹤器
                    tracking = True
                    
    if tracking:
        # 更新追蹤器，獲取新位置
        success, box = tracker.update(frame)
        if success:
            # 繪製追蹤框
            p1 = (int(box[0]), int(box[1]))
            p2 = (int(box[0] + box[2]), int(box[1] + box[3]))
            cv2.rectangle(frame, p1, p2, (0, 0, 255), 3)
            
            # 計算追蹤框的中心位置
            center_x = int(box[0] + box[2] / 2)
            center_y = int(box[1] + box[3] / 2)
            center_position = [center_x, center_y]
            
            print(f"Tracking center position: {center_position}")
            
            # 構造 JSON 數據
            data = json.dumps([center_position[0], center_position[1], frame_center[0], frame_center[1]])

            # 使用 MQTT 發佈中心位置
            #mqttc.publish(TopicName, str(center_position))
            mqttc.publish(TopicName, data)

        else:
            tracking = False  # 如果追蹤失敗，重新檢測

    # 顯示視頻幀
    cv2.imshow('Tracking', frame)
    
    # 等待按鍵事件
    keyName = cv2.waitKey(1)
    if keyName == ord('q'):
        break

# 釋放資源
cap.release()
cv2.destroyAllWindows()


