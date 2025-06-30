import numpy as np

# 添加科學計算和色彩分析相關導入
try:
    from skimage import color
    from skimage.color import rgb2lab, deltaE_cie76
    SKIMAGE_AVAILABLE = True
except ImportError:
    print("⚠ 警告: skimage 未安裝，將使用簡化版 LAB 轉換")
    SKIMAGE_AVAILABLE = False

def calculate_color_delta(left_rgb, left_pos, right_rgb, right_pos):
    """計算左右線段的色差(Delta Color) - 包含區域性分析"""
    print("\n=== 色差分析 ===")

    # 動態導入，避免循環導入
    from color_analysis import detect_color_bars_automatically, align_color_samples
    from visualization import plot_color_delta_analysis, print_color_delta_statistics, visualize_region_analysis, plot_rgb_analysis

    # 1. 對齊兩條線段的採樣點
    left_rgb, left_pos, right_rgb_aligned, right_pos = align_color_samples(left_rgb, left_pos, right_rgb, right_pos)

    # 將對齊後的左右線RGB數據繪製出來
    plot_rgb_analysis(left_rgb, left_pos, right_rgb_aligned, right_pos)

    # 2. 自動檢測色帶區域
    auto_regions = detect_color_bars_automatically(left_rgb, right_rgb_aligned, method='gradient')
    
    # 3. 如果自動檢測失敗，使用手動定義的區域（你可以根據實際情況調整這些值）
    if not auto_regions:
        print("自動檢測失敗，使用預設區域...")
        manual_regions = {
            'region_1': (20, 60),   # 第一個色帶
            'region_2': (80, 120),  # 第二個色帶  
            'region_3': (140, 180), # 第三個色帶
        }
        regions = manual_regions
    else:
        regions = auto_regions
    
    # 4. 進行區域性色差分析
    region_results = calculate_region_delta_e(left_rgb, right_rgb_aligned, regions)
    
    # 5. 可視化區域分析結果
    if region_results:
        visualize_region_analysis(left_rgb, right_rgb_aligned, regions, region_results)
        
        # 打印區域分析摘要
        print("\n=== 區域色差分析摘要 ===")
        for region_name, result in region_results.items():
            print(f"{region_name}:")
            print(f"  ΔE76: {result['delta_e']:.4f}")
            print(f"  RGB距離: {result['rgb_distance']:.2f}")
            print(f"  區域大小: {result['region_size']} 個採樣點")
    
    # 6. 保留原有的全線段色差分析作為對比
    print("\n=== 全線段色差分析（對比用） ===")
    delta_rgb = calculate_rgb_delta(left_rgb, right_rgb_aligned)
    delta_e_lab = calculate_lab_delta_e(left_rgb, right_rgb_aligned)
    delta_hsv = calculate_hsv_delta(left_rgb, right_rgb_aligned)
    
    plot_color_delta_analysis(delta_rgb, delta_e_lab, delta_hsv)
    print_color_delta_statistics(delta_rgb, delta_e_lab, delta_hsv)
    
    return {
        'delta_rgb': delta_rgb,
        'delta_e_lab': delta_e_lab,
        'delta_hsv': delta_hsv,
        'region_analysis': region_results,
        'detected_regions': regions
    }

def calculate_region_delta_e(left_rgb, right_rgb, regions):
    """
    計算指定區域內的平均顏色，並比較其色差
    
    參數:
    left_rgb (np.array): 左邊線段的 RGB 數據
    right_rgb (np.array): 右邊線段的 RGB 數據  
    regions (dict): 區域字典，例如 {'red_bar': (85, 120), 'green_bar': (150, 185)}
    
    返回:
    dict: 每個區域的色差結果
    """
    print("=== 區域性平均色差計算 ===")
    results = {}
    
    for color_name, (start_idx, end_idx) in regions.items():
        print(f"\n分析區域: {color_name} (索引 {start_idx}-{end_idx})")
        
        # 確保索引在有效範圍內
        start_idx = max(0, min(start_idx, len(left_rgb)-1))
        end_idx = max(start_idx+1, min(end_idx, len(left_rgb)))
        
        # 提取該區域的 RGB 數據
        left_region_rgb = left_rgb[start_idx:end_idx]
        right_region_rgb = right_rgb[start_idx:end_idx]
        
        if len(left_region_rgb) == 0 or len(right_region_rgb) == 0:
            print(f"⚠ 區域 {color_name} 無效，跳過")
            continue
            
        # 計算區域內的平均顏色
        avg_left_color = np.mean(left_region_rgb, axis=0)
        avg_right_color = np.mean(right_region_rgb, axis=0)
        
        print(f"左邊平均RGB: [{avg_left_color[0]:.1f}, {avg_left_color[1]:.1f}, {avg_left_color[2]:.1f}]")
        print(f"右邊平均RGB: [{avg_right_color[0]:.1f}, {avg_right_color[1]:.1f}, {avg_right_color[2]:.1f}]")
        
        # 計算色差
        if SKIMAGE_AVAILABLE:
            # 使用 skimage 進行精確的 LAB 轉換和 ΔE 計算
            # 將 RGB 值歸一化到 0-1 範圍並重塑為圖像格式
            left_rgb_norm = avg_left_color[np.newaxis, np.newaxis, :] / 255.0
            right_rgb_norm = avg_right_color[np.newaxis, np.newaxis, :] / 255.0
            
            # 轉換為 LAB 色彩空間
            avg_left_lab = rgb2lab(left_rgb_norm)
            avg_right_lab = rgb2lab(right_rgb_norm)
            
            # 計算 ΔE76 色差
            delta_e = deltaE_cie76(avg_left_lab, avg_right_lab)[0][0]
        else:
            # 使用簡化版色差計算
            delta_e = calculate_simple_delta_e(avg_left_color, avg_right_color)
        
        # 計算 RGB 歐式距離作為參考
        rgb_distance = np.sqrt(np.sum((avg_right_color - avg_left_color) ** 2))
        
        results[color_name] = {
            'delta_e': delta_e,
            'rgb_distance': rgb_distance,
            'left_avg_rgb': avg_left_color,
            'right_avg_rgb': avg_right_color,
            'region_size': end_idx - start_idx
        }
        
        print(f"ΔE76 色差: {delta_e:.4f}")
        print(f"RGB 距離: {rgb_distance:.2f}")
        
    return results

def calculate_simple_delta_e(rgb1, rgb2):
    """簡化版的色差計算（當 skimage 不可用時）"""
    # 轉換為簡化的 LAB 色彩空間
    lab1 = simple_rgb_to_lab(rgb1)
    lab2 = simple_rgb_to_lab(rgb2)
    
    # 計算 ΔE
    delta_l = lab2[0] - lab1[0]
    delta_a = lab2[1] - lab1[1] 
    delta_b = lab2[2] - lab1[2]
    
    delta_e = np.sqrt(delta_l**2 + delta_a**2 + delta_b**2)
    return delta_e

def simple_rgb_to_lab(rgb):
    """簡化的 RGB 到 LAB 轉換"""
    # 歸一化
    rgb_norm = rgb / 255.0
    
    # 簡化的轉換公式
    L = 0.299 * rgb_norm[0] + 0.587 * rgb_norm[1] + 0.114 * rgb_norm[2]
    a = (rgb_norm[0] - rgb_norm[1]) * 127
    b = (rgb_norm[1] - rgb_norm[2]) * 127
    
    return np.array([L * 100, a, b])  # L範圍0-100，a和b範圍約-127到127

def calculate_rgb_delta(left_rgb, right_rgb):
    """計算RGB色差"""
    # 計算各通道的差值
    delta_r = right_rgb[:, 0] - left_rgb[:, 0]
    delta_g = right_rgb[:, 1] - left_rgb[:, 1]
    delta_b = right_rgb[:, 2] - left_rgb[:, 2]
    
    # 計算歐式距離
    delta_rgb_magnitude = np.sqrt(delta_r**2 + delta_g**2 + delta_b**2)
    
    return {
        'delta_r': delta_r,
        'delta_g': delta_g,
        'delta_b': delta_b,
        'magnitude': delta_rgb_magnitude
    }

def rgb_to_lab(rgb):
    """將RGB轉換為LAB色彩空間"""
    # 歸一化RGB值到0-1
    rgb_normalized = rgb / 255.0
    
    # 簡化的RGB到LAB轉換（更精確的轉換需要考慮白點等因素）
    # 這裡使用近似公式
    lab = np.zeros_like(rgb_normalized)
    
    # L通道（亮度）
    lab[:, 0] = 0.299 * rgb_normalized[:, 0] + 0.587 * rgb_normalized[:, 1] + 0.114 * rgb_normalized[:, 2]
    
    # a通道（紅綠軸）
    lab[:, 1] = (rgb_normalized[:, 0] - rgb_normalized[:, 1]) * 127
    
    # b通道（藍黃軸）
    lab[:, 2] = (rgb_normalized[:, 1] - rgb_normalized[:, 2]) * 127
    
    return lab

def calculate_lab_delta_e(left_rgb, right_rgb):
    """計算LAB色彩空間中的ΔE色差"""
    # 轉換到LAB空間
    left_lab = rgb_to_lab(left_rgb)
    right_lab = rgb_to_lab(right_rgb)
    
    # 計算ΔE76 (CIE76色差公式)
    delta_l = right_lab[:, 0] - left_lab[:, 0]
    delta_a = right_lab[:, 1] - left_lab[:, 1]
    delta_b = right_lab[:, 2] - left_lab[:, 2]
    
    delta_e = np.sqrt(delta_l**2 + delta_a**2 + delta_b**2)
    
    return {
        'delta_l': delta_l,
        'delta_a': delta_a,
        'delta_b_lab': delta_b,
        'delta_e': delta_e
    }

def rgb_to_hsv(rgb):
    """將RGB轉換為HSV"""
    rgb_normalized = rgb / 255.0
    hsv = np.zeros_like(rgb_normalized)
    
    for i in range(len(rgb_normalized)):
        r, g, b = rgb_normalized[i]
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        diff = max_val - min_val
        
        # Value
        hsv[i, 2] = max_val
        
        # Saturation
        if max_val == 0:
            hsv[i, 1] = 0
        else:
            hsv[i, 1] = diff / max_val
        
        # Hue
        if diff == 0:
            hsv[i, 0] = 0
        elif max_val == r:
            hsv[i, 0] = (60 * ((g - b) / diff) + 360) % 360
        elif max_val == g:
            hsv[i, 0] = (60 * ((b - r) / diff) + 120) % 360
        elif max_val == b:
            hsv[i, 0] = (60 * ((r - g) / diff) + 240) % 360
    
    return hsv

def calculate_hsv_delta(left_rgb, right_rgb):
    """計算HSV色差"""
    left_hsv = rgb_to_hsv(left_rgb)
    right_hsv = rgb_to_hsv(right_rgb)
    
    # 色相差值需要考慮環形特性
    delta_h = right_hsv[:, 0] - left_hsv[:, 0]
    delta_h = np.where(delta_h > 180, delta_h - 360, delta_h)
    delta_h = np.where(delta_h < -180, delta_h + 360, delta_h)
    
    delta_s = right_hsv[:, 1] - left_hsv[:, 1]
    delta_v = right_hsv[:, 2] - left_hsv[:, 2]
    
    return {
        'delta_h': delta_h,
        'delta_s': delta_s,
        'delta_v': delta_v
    } 