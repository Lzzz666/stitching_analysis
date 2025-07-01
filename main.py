#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
色彩分析主程序 - 重構版本

功能：
- 圖像讀取和處理  
- 校正點檢測（模板匹配和手動標記）
- 色彩分析和色差計算
- 結果可視化

模組化結構：
- image_processing: 圖像處理
- calibration: 校正點檢測  
- color_analysis: 色彩分析
- color_delta: 色差計算
- visualization: 可視化
- utils: 工具函式
- brightness_analysis: 亮度分析
"""

import cv2
from image_processing import load_image, convert_to_gray
from calibration import find_octagon_pattern_matching, find_octagon_manual
from color_analysis import analyze_color_lines
from visualization import visualize_sampling_lines, print_center_line
from brightness_analysis import brightness_analysis

def main():
    """主程序入口"""
    try:
        print("=== 色彩分析程序 (重構版本) ===")
        print("開始處理...")
        
        # 1. 讀取和預處理圖像
        image = load_image("assets/image.png")
        if image is None:
            print("✗ 錯誤: 無法讀取圖片 assets/image.png")
            print("請確保該檔案存在於 assets/ 目錄下")
            return
            
        gray_image = convert_to_gray(image)
        print(f"✓ 成功讀取圖片，尺寸: {image.shape}")
        
        # 保存灰度圖
        cv2.imwrite("assets/gray_image.png", gray_image)
        print("✓ 已保存灰度圖到 assets/gray_image.png")
        
        # 2. 校正點檢測
        main_corners = detect_correction_points(gray_image)
        
        # 3. 色彩分析
        if main_corners and len(main_corners) == 4:
            perform_color_analysis(image, main_corners)
        else:
            print_usage_tips()
            
    except Exception as e:
        print(f"✗ 程序執行錯誤: {e}")
        import traceback
        traceback.print_exc()

def detect_correction_points(gray_image):
    """檢測校正點，依序嘗試模板匹配和手動標記"""
    print("\n" + "="*60)
    print("開始檢測校正點...")
    
    # 方法1: 模板匹配 (手動框選target)
    try:
        print("\n--- 方法1: 模板匹配 ---")
        corners = find_octagon_pattern_matching(gray_image)

        if corners and len(corners) >= 4:
            return corners
        else:
            print("⚠ 模板匹配未找到足夠的角點，嘗試手動標記...")
            
    except Exception as e:
        print(f"⚠ 模板匹配失敗: {e}")
        print("嘗試手動標記...")
    
    # 方法2: 手動標記
    try:
        print("\n--- 方法2: 手動標記 ---")
        corners = find_octagon_manual(gray_image)
        
        if len(corners) == 4:
            return corners
        else:
            print("⚠ 手動標記未完成，使用預設角點")
            
    except Exception as e:
        print(f"⚠ 手動標記失敗: {e}")
    
    return []

def perform_color_analysis(image, corners):
    """執行完整的色彩分析流程"""
    print("\n" + "="*60)
    print("開始色彩分析...")
    
    try:
        # 可視化採樣線段
        visualize_sampling_lines(image, corners)
        print("✓ 採樣線段可視化完成")

        # 印出中線
        print_center_line(image, corners)
        
        # RGB分析和色差計算
        left_rgb, right_rgb, delta_e = analyze_color_lines(image, corners)
        print("="*60)
        print(f"delta_e: {delta_e}")
        print("="*60)
        print("✓ RGB分析和色差計算完成")
        
        # 亮度分析
        left_rgb, right_rgb, delta_e_brightness = brightness_analysis(image, corners)
        print("="*60)
        print(f"delta_e_brightness: {delta_e_brightness}")
        print("="*60)
        print("✓ 亮度分析完成")
        
        # 顯示生成檔案清單
        print_generated_files()
        
    except Exception as e:
        print(f"✗ 色彩分析失敗: {e}")
        import traceback
        traceback.print_exc()

def print_generated_files():
    """顯示生成的檔案清單"""
    print("\n" + "="*60)
    print("✓ 程序執行完成！")
    print("\n生成的檔案:")
    print("📁 基礎檔案:")
    print("  - assets/gray_image.png - 灰度圖")
    print("  - assets/sampling_lines.png - 採樣線段圖")
    
    print("\n🎨 色彩分析:")
    print("  - assets/rgb_analysis_separated.png - 分離式RGB分析")
    print("  - assets/rgb_comparison.png - RGB比較圖")
    
    print("\n💡 亮度分析:")
    print("  - assets/brightness_analysis.png - 亮度分析圖")
    
    print("\n🎯 校正點檢測:")
    print("  - assets/pattern_matching_result.png - 模板匹配結果")
    print("  - assets/extracted_target.png - 提取的target模板")

def print_usage_tips():
    """顯示使用提示"""
    print("\n⚠ 未能獲得有效的校正點，跳過色彩分析")
    print("\n💡 使用提示:")
    print("1. 確保圖片 assets/image_bias_test.png 存在")
    print("2. 模板匹配時請準確框選一個target區域")
    print("3. 手動標記時確保有圖形界面環境")
    print("4. 可以修改程式碼中的預設角點座標進行測試")

if __name__ == "__main__":
    main() 