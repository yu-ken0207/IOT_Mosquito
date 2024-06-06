import cv2
import os
import json

# 设置输入图片文件夹和输出标注文件夹
image_folder = 'Culex Quinquefasciatus'  # 替换为您的图片文件夹路径
output_file = 'Culex Quinquefasciatus.json'  # 输出标注文件

# 初始化 CSRT 追踪器
tracker = cv2.TrackerCSRT_create()

# 获取文件夹中的图片文件名
image_files = [f for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]
image_files.sort()  # 按名称排序，以便依次处理

annotations = {}

# 设置图片最大尺寸
max_size = (800, 800)  # 最大宽高

for i, image_file in enumerate(image_files):
    image_path = os.path.join(image_folder, image_file)
    print(f"Loading image: {image_path}")
    
    try:
        image_path = image_path.encode('utf-8').decode('utf-8')
    except UnicodeDecodeError as e:
        print(f"Unicode decode error: {e}")
        continue
    
    image = cv2.imread(image_path)
    
    if image is None:
        print(f"Cannot load image {image_file}")
        continue
    
    # 调整图片大小
    height, width = image.shape[:2]
    if height > max_size[0] or width > max_size[1]:
        scaling_factor = min(max_size[0] / height, max_size[1] / width)
        new_size = (int(width * scaling_factor), int(height * scaling_factor))
        image = cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)
    
    if i == 0:
        # 在第一张图片中选择要跟踪的区域
        bbox = cv2.selectROI('Select ROI', image, showCrosshair=True, fromCenter=False)
        cv2.destroyWindow('Select ROI')
        tracker.init(image, bbox)
    else:
        # 在后续图片中更新追踪器
        success, bbox = tracker.update(image)
        if not success:
            print(f"Tracking failed for image {image_file}")
            break

    # 保存标注
    x, y, w, h = [int(v) for v in bbox]
    annotations[image_file] = {'bbox': [x, y, w, h]}

    # 在图片上绘制边界框以进行可视化（可选）
    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.imshow('Tracking', image)
    if cv2.waitKey(1) == ord('q'):
        break

# 保存标注到文件
with open(output_file, 'w') as f:
    json.dump(annotations, f, indent=4)

cv2.destroyAllWindows()
print(f"Annotations saved to {output_file}")
