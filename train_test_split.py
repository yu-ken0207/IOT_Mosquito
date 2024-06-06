import os
import shutil
import json
import random
from sklearn.model_selection import train_test_split
from PIL import Image

# 目標文件夾結構
train_img_dir = 'yoloV8/datasets/train/images'
val_img_dir = 'yoloV8/datasets/val/images'
test_img_dir = 'yoloV8/datasets/test/images'

train_label_dir = 'yoloV8/datasets/train/labels'
val_label_dir = 'yoloV8/datasets/val/labels'
test_label_dir = 'yoloV8/datasets/test/labels'



os.makedirs(train_img_dir, exist_ok=True)
os.makedirs(val_img_dir, exist_ok=True)
os.makedirs(test_img_dir, exist_ok=True)
os.makedirs(train_label_dir, exist_ok=True)
os.makedirs(val_label_dir, exist_ok=True)
os.makedirs(test_label_dir, exist_ok=True)

def convert_bbox_to_yolo(size, bbox):
    dw = 1. / size[0]
    dh = 1. / size[1]
    x = (bbox[0] + bbox[2] / 2.0) * dw
    y = (bbox[1] + bbox[3] / 2.0) * dh
    w = bbox[2] * dw
    h = bbox[3] * dh
    return (x, y, w, h)

def convert_annotations(json_file, image_dir, train_size=0.7, val_size=0.2):
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    image_names = list(data.keys())
    train_names, temp_names = train_test_split(image_names, train_size=train_size, random_state=42)
    val_names, test_names = train_test_split(temp_names, test_size=val_size/(1-train_size), random_state=42)
    
    for image_set, output_img_dir_set, output_label_dir_set in [(train_names, train_img_dir, train_label_dir), (val_names, val_img_dir, val_label_dir), (test_names, test_img_dir, test_label_dir)]:
        for image_name in image_set:
            annotation = data[image_name]
            bbox = annotation['bbox']
            img_path = os.path.join(image_dir, image_name)

            # 獲取圖片的尺寸
            with Image.open(img_path) as img:
                img_size = img.size  # (width, height)

            #img_size = (640, 640)  # 替換成實際圖片尺寸
            yolo_bbox = convert_bbox_to_yolo(img_size, bbox)
            
            label = categories[os.path.basename(json_file).split('.')[0]]
            label_file = os.path.join(output_label_dir_set, image_name.replace('.jpg', '.txt'))
            
            with open(label_file, 'w') as f:
                f.write(f"{label} " + " ".join([str(a) for a in yolo_bbox]) + '\n')
            
            shutil.copy(img_path, os.path.join(output_img_dir_set, image_name))

categories = {
    "Aedes Aegypti": 0,
    "Aedes albopictus": 1,
    "Anopheles Stephensi": 2,
    "Culex Quinquefasciatus": 3
}

# 使用範例
convert_annotations('mosquito/Aedes Aegypti.json', 'mosquito/Aedes Aegypti')
convert_annotations('mosquito/Aedes albopictus.json', 'mosquito/Aedes albopictus')
convert_annotations('mosquito/Anopheles Stephensi.json', 'mosquito/Anopheles Stephensi')
convert_annotations('mosquito/Culex Quinquefasciatus.json', 'mosquito/Culex Quinquefasciatus')
