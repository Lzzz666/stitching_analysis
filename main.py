#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
色彩分析主程序 - 重構版本

這個程序用於分析左右兩條採樣線的色差，包含：
- 圖像讀取和處理
- 校正點檢測（模板匹配和手動標記）
- 色彩分析和色差計算
- 結果可視化

模組化結構：
- image_processing: 圖像處理相關
- calibration: 校正點檢測相關
- color_analysis: 色彩分析相關
- color_delta: 色差計算相關
- visualization: 可視化相關
- utils: 工具函式
"""

import cv2
from image_processing import load_image, convert_to_gray
from calibration import find_octagon_pattern_matching, find_octagon_manual
from color_analysis import analyze_color_lines
from visualization import visualize_sampling_lines
from utils import save_results

def main():
    """主程序入口"""
    try:
        print("=== 色彩分析程序 (重構版本) ===")
        print("開始處理...")
        
        # 1. 讀取主圖片
        image = load_image("assets/image_bias_test.png")
        if image is None:
            print("✗ 錯誤: 無法讀取圖片 assets/image_bias_test.png")
            return
            
        gray_image = convert_to_gray(image)
        print(f"✓ 成功讀取圖片，尺寸: {image.shape}")
        
        # 儲存灰度圖
        cv2.imwrite("assets/gray_image.png", gray_image)
        print("✓ 已儲存灰度圖到 assets/gray_image.png")
        
        main_corners = None
        
        # 2. 方法1: 模板匹配 (可選)
        use_template_matching = False  # 設置為True以啟用模板匹配
        
        if use_template_matching:
            try:
                target = load_image("assets/target.png")
                if target is not None:
                    gray_target = convert_to_gray(target)
                    all_corners = find_octagon_pattern_matching(gray_image, gray_target)
                    
                    if all_corners:
                        # 如果找到多個匹配，可以選擇前4個角點作為主要校正點
                        main_corners = all_corners[:4] if len(all_corners) >= 4 else all_corners
                        save_results(gray_image, main_corners, "pattern_matching")
                        print(f"✓ 模板匹配找到的所有角點數量: {len(all_corners)}")
                        print(f"✓ 主要校正點: {main_corners}")
                    else:
                        print("⚠ 模板匹配未找到任何匹配")
                else:
                    print("⚠ 未找到 target.png，跳過模板匹配")
            except Exception as e:
                print(f"⚠ 模板匹配失敗: {e}")
        
        # 3. 方法2: 手動標記 (如果模板匹配失敗或未啟用)
        if main_corners is None or len(main_corners) != 4:
            try:
                print("\n--- 使用手動標記方式 ---")
                corners_manual = find_octagon_manual(gray_image)
                
                if len(corners_manual) == 4:
                    main_corners = corners_manual
                    save_results(gray_image, corners_manual, "manual")
                    print(f"✓ 手動選擇的角點: {corners_manual}")
                else:
                    print("⚠ 手動標記未完成，使用預設角點")
                    # 使用預設角點進行演示
                    main_corners = [(100, 100), (400, 100), (400, 300), (100, 300)]
                    print(f"✓ 使用預設角點: {main_corners}")
                    
            except Exception as e:
                print(f"⚠ 手動標記失敗: {e}")
                # 使用預設角點
                main_corners = [(100, 100), (400, 100), (400, 300), (100, 300)]
                print(f"✓ 使用預設角點: {main_corners}")
        
        # 4. 如果成功獲得了4個校正點，進行顏色分析
        if main_corners and len(main_corners) == 4:
            print("\n" + "="*60)
            print("開始進行顏色分析...")
            
            # 可視化採樣線段
            visualize_sampling_lines(image, main_corners)
            
            # 執行完整的RGB分析和色差計算
            left_rgb, right_rgb = analyze_color_lines(image, main_corners)
            
            print("✓ 顏色分析完成")
            print("\n" + "="*60)
            print("程序執行完成！")
            print("生成的檔案:")
            print("- assets/gray_image.png - 灰度圖")
            print("- assets/sampling_lines.png - 採樣線段圖")
            print("- assets/rgb_analysis_separated.png - 分離式RGB分析圖")
            print("- assets/rgb_comparison.png - RGB比較圖")
            print("- assets/color_delta_analysis.png - 色差分析圖")
            print("- assets/region_color_analysis.png - 區域色差分析圖")
            
        else:
            print("⚠ 未能獲得有效的校正點，跳過顏色分析")
            print("提示:")
            print("1. 確保圖片 assets/image_bias_test.png 存在")
            print("2. 如果使用手動標記，確保有圖形界面環境")
            print("3. 或者修改代碼中的預設角點座標")
            
    except Exception as e:
        print(f"✗ 程序執行錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 