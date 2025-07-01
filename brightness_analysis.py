import numpy as np
import matplotlib.pyplot as plt
from image_processing import sample_line_rgb
from visualization import plot_rgb_analysis

def brightness_analysis(image, corners):
    """分析校正點之間的線段RGB值變化，重點關注亮度分析"""
    if len(corners) != 4:
        print(f"⚠ 需要4個校正點，當前只有{len(corners)}個")
        return
    
    print("=== 亮度分析 ===")
    
    # 根據座標判斷四個點的位置關係
    # 按y座標排序，前兩個是上方的點，後兩個是下方的點
    sorted_corners = sorted(corners, key=lambda p: p[1])
    top_points = sorted(sorted_corners[:2], key=lambda p: p[0])  # 按x座標排序
    bottom_points = sorted(sorted_corners[2:], key=lambda p: p[0])
    
    left_top = top_points[0]      # 左上
    right_top = top_points[1]     # 右上
    left_bottom = bottom_points[0]  # 左下
    right_bottom = bottom_points[1] # 右下


    left_line_rgb, left_positions = sample_line_rgb(image, left_top, left_bottom)
    right_line_rgb, right_positions = sample_line_rgb(image, right_top, right_bottom)
    

    left_line_rgb[left_line_rgb > 250] = 255
    right_line_rgb[right_line_rgb > 250] = 255
    
    y = left_bottom[1] - left_top[1]

    left_line_rgb = left_line_rgb[int(0.65*y):int(y - 0.2 * y)]
    left_positions = left_positions[int(0.65*y):int(y - 0.2 * y)]

    right_line_rgb = right_line_rgb[int(0.75*y):int(y - 0.1 * y)]
    right_positions = right_positions[int(0.75*y):int(y - 0.1 * y)]

    plot_rgb_analysis(left_line_rgb, left_positions, right_line_rgb, right_positions)

    delta_e = calculate_brightness_delta(left_line_rgb, right_line_rgb)
    return left_line_rgb, right_line_rgb, delta_e

def calculate_brightness_delta(left_rgb, right_rgb):
    """
    Calculate the brightness difference between the left and right lines, focusing on the gray color band area
    
    Param:
    left_rgb (np.array): left line rgb data
    right_rgb (np.array): right line rgb data
    """
    print("\n=== brightness difference analysis ===")
    left_rgb_float = left_rgb.astype(np.float64)
    right_rgb_float = right_rgb.astype(np.float64)

    # 1. Calculate the brightness value (using the standard brightness formula: Y = 0.299*R + 0.587*G + 0.114*B)
    left_brightness = calculate_luminance(left_rgb_float)
    right_brightness = calculate_luminance(right_rgb_float)

    left_brightness_mean = 0
    left_brightness_cnt = 0
    for i in range(len(left_rgb_float)):
        if(left_rgb_float[i][0] == 255):
            continue
        else:
            left_brightness_mean += left_rgb_float[i][0]
            left_brightness_cnt += 1
    left_brightness_mean /= left_brightness_cnt
    print(f"left_brightness_mean: {left_brightness_mean}")

    right_brightness_mean = 0
    right_brightness_cnt = 0
    for i in range(len(right_rgb_float)):
        if(right_rgb_float[i][0] == 255):
            continue
        else:
            right_brightness_mean += right_rgb_float[i][0]
            right_brightness_cnt += 1
    right_brightness_mean /= right_brightness_cnt   
    print(f"right_brightness_mean: {right_brightness_mean}")
    delta_brightness = right_brightness_mean - left_brightness_mean
    print(f"delta_brightness: {delta_brightness}")
    return delta_brightness

def calculate_luminance(rgb_data):
    """
    Calculate the brightness value of the RGB data
    Using the standard brightness formula: Y = 0.299*R + 0.587*G + 0.114*B
    
    Param:
    rgb_data (np.array): RGB data (N x 3)
    
    Return:
    np.array: brightness value array
    """
    # standard brightness weights
    weights = np.array([0.299, 0.587, 0.114])
    luminance = np.dot(rgb_data, weights)
    return luminance
