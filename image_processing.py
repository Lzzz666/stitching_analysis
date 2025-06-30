import cv2
import numpy as np

def load_image(image_path):
    """讀取圖片"""
    image = cv2.imread(image_path)
    return image

def convert_to_gray(image):
    """將圖片轉換為灰度圖"""
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def sample_line_rgb(image, start_point, end_point, num_samples=100):
    """沿著線段採樣RGB值"""
    x1, y1 = start_point
    x2, y2 = end_point
    
    # 生成線段上的採樣點
    positions = []
    rgb_values = []
    
    for i in range(num_samples):
        # 線性插值計算採樣點座標
        t = i / (num_samples - 1)  # 參數從0到1
        x = int(x1 + t * (x2 - x1))
        y = int(y1 + t * (y2 - y1))
        
        # 確保座標在圖片範圍內
        x = max(0, min(x, image.shape[1] - 1))
        y = max(0, min(y, image.shape[0] - 1))
        
        # 提取RGB值（注意OpenCV使用BGR格式）
        if len(image.shape) == 3:
            b, g, r = image[y, x]
            rgb_values.append([r, g, b])  # 轉換為RGB順序
        else:
            # 灰度圖
            gray_val = image[y, x]
            rgb_values.append([gray_val, gray_val, gray_val])
        
        # 記錄在線段上的位置（距離起點的距離）
        distance = ((x - x1) ** 2 + (y - y1) ** 2) ** 0.5
        positions.append(distance)
    
    return np.array(rgb_values), np.array(positions) 