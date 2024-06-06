# sudo pigpiod
# sudo pigpiod
# sudo pigpiod
# sudo pigpiod



import paho.mqtt.client as mqtt
import pigpio
import time
import json

# 初始化 pigpio
pi = pigpio.pi('localhost', 8888)

# 定義伺服機連接的GPIO引腳
servo_x_pin = 3  # X軸伺服機
servo_y_pin = 4  # Y軸伺服機

def set_servo_angle(pin, angle):
    """設定伺服機角度"""
    # 將角度轉換為PWM脈寬
    pulsewidth = int(angle * 1000 / 90 + 1500)
    pi.set_servo_pulsewidth(pin, pulsewidth)
    #time.sleep(1)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("TrackingCenter")

def on_message(client, userdata, msg):
    #payload = msg.payload.decode("utf-8")
    print(msg.topic + "  " + str(msg.payload))
    
    data = json.loads(msg.payload)

    # 提取XY軸的值和螢幕中心座標
    x, y, center_x, center_y = data
    
    
    # 計算伺服機應移動的角度
    x_angle = calculate_angle(x, center_x, 1000)
    y_angle = calculate_angle(y, center_y, 800)
    
    if (x_angle > 0):
        x_angle = x_angle / 5
    if (y_angle > 0):
        y_angle = y_angle / 5
    
    #print("X move = ", x_angle)
    #print("Y move = ", Y_angle)
    
    # 設定伺服機角度
    set_servo_angle(servo_x_pin, x_angle)
    set_servo_angle(servo_y_pin, y_angle)

def calculate_angle(current, target, frame_dimension):
    """根據當前位置和目標位置計算所需的角度"""
    # 這裡假設當前位置和目標位置的範圍是相同的，且最大範圍為180度
    # 根據需求調整此計算方法
    return 0+ (target - current) * 180 / frame_dimension


# 設定伺服機角度
set_servo_angle(servo_x_pin, 10)
set_servo_angle(servo_y_pin, 10)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_message = on_message
client.connect("test.mosquitto.org", 1883, 60)
client.loop_forever()