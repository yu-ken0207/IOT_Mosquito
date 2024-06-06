import cv2
import torch
from ultralytics import YOLO
import numpy as np

# 加载 YOLOv8 模型
model = YOLO('物件追蹤/runs/detect/train/weights/best.pt')  # 替换为您的模型路径

# 创建 CSRT 追踪器
tracker = cv2.TrackerCSRT_create()
tracking = False

# 打开摄像头
cap = cv2.VideoCapture(1)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Cannot receive frame")
        break
    
    # 调整帧的大小以加快处理速度
    #frame = cv2.resize(frame, (540, 300))
    frame = cv2.resize(frame, (1000, 800))
    
    if not tracking:
        # 使用 YOLOv8 模型进行物体检测
        results = model(frame)

        # 获取检测结果
        for result in results:
            boxes = result.boxes.xyxy.cpu().numpy()
            confidences = result.boxes.conf.cpu().numpy()
            class_ids = result.boxes.cls.cpu().numpy()

            for box, confidence, class_id in zip(boxes, confidences, class_ids):
                # 假设 '0' 是昆虫的类别索引，调整为您的实际类别索引
                if class_id == 0 and confidence > 0.5:
                    x1, y1, x2, y2 = map(int, box)
                    w, h = x2 - x1, y2 - y1
                    area = (x1, y1, w, h)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f'Insect {confidence:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    tracker.init(frame, area)  # 初始化追踪器
                    tracking = True
                    
                if class_id == 1 and confidence > 0.5:
                    x1, y1, x2, y2 = map(int, box)
                    w, h = x2 - x1, y2 - y1
                    area = (x1, y1, w, h)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f'Insect {confidence:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    tracker.init(frame, area)  # 初始化追踪器
                    tracking = True
                    
                if class_id == 2 and confidence > 0.5:
                    x1, y1, x2, y2 = map(int, box)
                    w, h = x2 - x1, y2 - y1
                    area = (x1, y1, w, h)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f'Insect {confidence:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    tracker.init(frame, area)  # 初始化追踪器
                    tracking = True
                    
                if class_id == 3 and confidence > 0.5:
                    x1, y1, x2, y2 = map(int, box)
                    w, h = x2 - x1, y2 - y1
                    area = (x1, y1, w, h)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f'Insect {confidence:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    tracker.init(frame, area)  # 初始化追踪器
                    tracking = True
                    
    
    if tracking:
        # 更新追踪器，获取新位置
        success, box = tracker.update(frame)
        if success:
            # 绘制追踪框
            p1 = (int(box[0]), int(box[1]))
            p2 = (int(box[0] + box[2]), int(box[1] + box[3]))
            cv2.rectangle(frame, p1, p2, (0, 0, 255), 3)
            
            # 计算并打印追踪框的中心位置
            center_x = int(box[0] + box[2] / 2)
            center_y = int(box[1] + box[3] / 2)
            print(f"Tracking center position: ({center_x}, {center_y})")
        else:
            tracking = False  # 如果追踪失败，重新检测

    # 显示视频帧
    cv2.imshow('Tracking', frame)
    
    # 等待按键事件
    keyName = cv2.waitKey(1)
    if keyName == ord('q'):
        break

# 释放资源
cap.release()
cv2.destroyAllWindows()
