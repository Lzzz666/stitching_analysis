import numpy as np
from image_processing import sample_line_rgb
from visualization import plot_rgb_analysis

def analyze_color_lines(image, corners):
    """分析校正點之間的線段RGB值變化"""
    if len(corners) != 4:
        print(f"⚠ 需要4個校正點，當前只有{len(corners)}個")
        return
    
    print("=== 顏色分析 ===")
    
    # 根據座標判斷四個點的位置關係
    # 按y座標排序，前兩個是上方的點，後兩個是下方的點
    sorted_corners = sorted(corners, key=lambda p: p[1])
    top_points = sorted(sorted_corners[:2], key=lambda p: p[0])  # 按x座標排序
    bottom_points = sorted(sorted_corners[2:], key=lambda p: p[0])
    
    left_top = top_points[0]      # 左上
    right_top = top_points[1]     # 右上
    left_bottom = bottom_points[0]  # 左下
    right_bottom = bottom_points[1] # 右下
    
    print(f"左上點: {left_top}")
    print(f"右上點: {right_top}")
    print(f"左下點: {left_bottom}")
    print(f"右下點: {right_bottom}")
    
    # 採樣兩條線的RGB值
    left_line_rgb, left_positions = sample_line_rgb(image, left_top, left_bottom)
    right_line_rgb, right_positions = sample_line_rgb(image, right_top, right_bottom)
    
    # 繪製RGB分析圖
    plot_rgb_analysis(left_line_rgb, left_positions, right_line_rgb, right_positions)

    # 導入並執行色差計算（避免循環導入）
    from color_delta import calculate_color_delta
    calculate_color_delta(left_line_rgb, left_positions, right_line_rgb, right_positions)
    
    return left_line_rgb, right_line_rgb

def detect_color_bars_automatically(left_rgb, right_rgb, method='gradient'):
    """
    自動檢測色帶區域
    
    參數:
    left_rgb, right_rgb: RGB數據
    method: 檢測方法 ('gradient', 'clustering', 'threshold')
    
    返回:
    dict: 檢測到的色帶區域
    """
    print(f"=== 自動檢測色帶區域 (方法: {method}) ===")
    
    # 使用左右兩邊的平均來檢測
    avg_rgb = (left_rgb + right_rgb) / 2
    gray_values = np.mean(avg_rgb, axis=1)
    
    if method == 'gradient':
        # 基於梯度變化檢測色帶邊界
        gradient = np.abs(np.gradient(gray_values))
        
        # 找到梯度峰值作為色帶邊界
        threshold = np.mean(gradient) + np.std(gradient)
        peaks = np.where(gradient > threshold)[0]
        
        # 將邊界點配對成區域
        regions = {}
        if len(peaks) >= 2:
            # 簡單的配對邏輯：相鄰峰值形成一個區域
            for i in range(0, len(peaks)-1, 2):
                start_idx = peaks[i]
                end_idx = peaks[i+1] if i+1 < len(peaks) else len(gray_values)-1
                
                # 根據區域位置給色帶命名
                region_name = f"color_bar_{i//2+1}"
                regions[region_name] = (start_idx, end_idx)
                
        print(f"檢測到 {len(regions)} 個色帶區域")
        for name, (start, end) in regions.items():
            print(f"  {name}: 索引 {start}-{end}")
            
        return regions
    
    return {}

def align_color_samples(left_rgb, left_pos, right_rgb, right_pos):
    """
    使用互相關 (Cross-Correlation) 自動計算並對齊兩條線段。
    這個函式會找出最佳的像素偏移量，並將其應用於右邊線段的 X 座標。
    
    參數:
    left_rgb (np.array): 左邊線段的 RGB 數據 (尺寸: N x 3)
    left_pos (np.array): 左邊線段的 X 座標 (像素距離)
    right_rgb (np.array): 右邊線段的 RGB 數據 (尺寸: M x 3)
    right_pos (np.array): 右邊線段的 X 座標 (像素距離)
    
    返回:
    tuple: 包含 (
        left_rgb,          # 左線RGB數據 (未變)
        left_pos,          # 左線X座標 (未變)
        right_rgb,         # 右線RGB數據 (未變)
        aligned_right_pos, # 對齊後的右線X座標
        pixel_offset       # 計算出的像素偏移量
    )
    """
    print("對齊採樣點...")
    left_signal = left_rgb[:, 1]
    right_signal = right_rgb[:, 1]

    left_signal_processed = left_signal - np.mean(left_signal)
    right_signal_processed = right_signal - np.mean(right_signal)
    
    # 計算互相關
    correlation = np.correlate(left_signal_processed, right_signal_processed, mode='full')
    
    lag_index = np.argmax(correlation)
    print(f"lag_index: {lag_index}")
    pixel_offset = lag_index - (len(right_signal) - 1)

    print(f"像素偏移量: {pixel_offset}")
    aligned_right_rgb = np.roll(right_rgb, shift=pixel_offset, axis=0)

    return left_rgb, left_pos, aligned_right_rgb, right_pos 