import cv2
import numpy as np

def save_results(image, corners, method_name):
    """儲存標記結果的通用函數"""
    result_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    
    # 標記所有角點
    for i, (x, y) in enumerate(corners):
        cv2.circle(result_image, (x, y), 10, (0, 0, 255), 3)
        cv2.putText(result_image, f'P{i+1}', (x+15, y-5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
    
    # 連接四個點形成四邊形
    if len(corners) == 4:
        pts = np.array(corners, np.int32)
        cv2.polylines(result_image, [pts], True, (0, 255, 0), 2)
    
    filename = f"assets/{method_name}_labeled.png"
    cv2.imwrite(filename, result_image)
    return filename 