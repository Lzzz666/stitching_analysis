import cv2
import numpy as np
import os

def find_octagon_pattern_matching(image, target):
    """使用模板匹配找到所有匹配的校正點"""
    print("=== 方法1: 模板匹配 ===")
    
    # 檢查圖片和模板尺寸
    print(f"主圖片尺寸: {image.shape}")
    print(f"目標模板尺寸: {target.shape}")
    
    # 獲取目標模板尺寸
    h, w = target.shape
    
    # 檢查模板是否小於圖片
    if h > image.shape[0] or w > image.shape[1]:
        print("⚠ 警告: 模板尺寸大於主圖片，這會導致匹配失敗")
        return []
    
    # 執行模板匹配
    result = cv2.matchTemplate(image, target, cv2.TM_CCOEFF_NORMED)
    
    # 查看匹配結果的統計信息
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    print(f"匹配結果統計: 最小值={min_val:.3f}, 最大值={max_val:.3f}")
    print(f"最佳匹配位置: {max_loc}, 分數: {max_val:.3f}")
    
    # 動態調整閾值
    if max_val < 0.3:
        threshold = max_val * 0.7  # 如果最佳匹配很低，降低閾值
        print(f"⚠ 最佳匹配分數較低，調整閾值為: {threshold:.3f}")
    elif max_val < 0.6:
        threshold = 0.3  # 中等匹配，使用較低閾值
        print(f"使用較低閾值: {threshold:.3f}")
    else:
        threshold = 0.6  # 高匹配，使用標準閾值
        print(f"使用標準閾值: {threshold:.3f}")
    
    print(f"threshold: {threshold}")
    locations = np.where(result >= threshold)
    
    # 創建結果圖像（不修改原圖）
    result_image = cv2.cvtColor(image.copy(), cv2.COLOR_GRAY2BGR)
    
    # 收集所有匹配的角點
    all_corners = []
    match_count = 0
    
    print(f"找到 {len(locations[0])} 個可能的匹配位置")
    
    # 如果沒有找到匹配，至少顯示最佳匹配
    if len(locations[0]) == 0:
        print("沒有找到符合閾值的匹配，顯示最佳匹配位置：")
        x, y = max_loc
        print(f"最佳匹配: 位置({x}, {y}), 分數: {max_val:.3f}")
        
        # 標記最佳匹配位置
        cv2.rectangle(result_image, (x, y), (x + w, y + h), (255, 0, 0), 2)  # 藍色框
        cv2.putText(result_image, f'Best: {max_val:.3f}', (x, y-10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        
        # 如果最佳匹配不是太差，就使用它
        if max_val > 0.2:
            corners = [
                (x, y),           # 左上
                (x + w, y),       # 右上
                (x + w, y + h),   # 右下
                (x, y + h)        # 左下
            ]
            all_corners.extend(corners)
            
            for i, (cx, cy) in enumerate(corners):
                cv2.circle(result_image, (cx, cy), 5, (255, 0, 0), -1)
                cv2.putText(result_image, f'P{i + 1}', 
                           (cx + 5, cy - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
    else:
        # 如果找到匹配，進行過濾和處理
        # 過濾重複匹配（移除距離太近的匹配點）
        filtered_matches = []
        min_distance = min(w, h) // 2  # 最小距離為模板尺寸的一半
        
        for y, x in zip(locations[0], locations[1]):
            match_score = result[y, x]
            
            # 檢查是否與已有匹配太近
            is_duplicate = False
            for existing_x, existing_y, _ in filtered_matches:
                distance = np.sqrt((x - existing_x)**2 + (y - existing_y)**2)
                if distance < min_distance:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                filtered_matches.append((x, y, match_score))
        
        print(f"過濾後剩餘 {len(filtered_matches)} 個有效匹配")
        
        # 處理每個有效匹配位置
        for x, y, match_score in filtered_matches:
            print(f"匹配 {match_count + 1}: 位置({x}, {y}), 分數: {match_score:.3f}")
            
            # 計算四個角點
            corners = [
                (x, y),           # 左上
                (x + w, y),       # 右上
                (x + w, y + h),   # 右下
                (x, y + h)        # 左下
            ]
            
            all_corners.extend(corners)
            
            # 在結果圖上標記匹配區域
            cv2.rectangle(result_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # 標記四個角點
            for i, (cx, cy) in enumerate(corners):
                cv2.circle(result_image, (cx, cy), 5, (0, 0, 255), -1)
                cv2.putText(result_image, f'M{match_count + 1}P{i + 1}', 
                           (cx + 5, cy - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
            
            match_count += 1
    
    # 儲存結果
    cv2.imwrite('assets/pattern_matching_result.png', result_image)
    print(f"✓ 找到 {match_count} 個匹配，共 {len(all_corners)} 個角點")
    print("✓ 已儲存模板匹配結果到 assets/pattern_matching_result.png")
    
    return all_corners

def find_octagon_manual(image):
    """手動輸入四個校正點座標"""
    print("=== 方法2: 手動標記 ===")
    print(f"圖片尺寸: {image.shape}")
    print("由於無顯示環境，請手動輸入四個校正點的座標")
    print("格式: x,y (例如: 100,50)")
    
    points = []
    
    # 檢查是否有顯示環境（檢查環境變量）
    # 檢查是否在 SSH 連接中
    is_ssh = 'SSH_CONNECTION' in os.environ or 'SSH_CLIENT' in os.environ
    
    has_display = (
        'DISPLAY' in os.environ or 
        'WAYLAND_DISPLAY' in os.environ or 
        os.name == 'nt'  # Windows
    ) and not is_ssh  # SSH 環境中即使有 DISPLAY 也不使用 GUI
    
    print(f"SSH 環境: {'是' if is_ssh else '否'}")
    print(f"顯示環境檢測: {'有' if has_display else '無'}")
    
    if has_display:
        # 有顯示環境，使用圖形界面
        print("檢測到顯示環境，啟用圖形界面...")
        return find_octagon_manual_gui(image)
    else:
        print("沒有顯示環境，無法使用手動標記功能")
        print("請確保:")
        print("1. 在有圖形界面的環境中運行")
        print("2. 或者取消註釋模板匹配功能")
        return []

def find_octagon_manual_gui(image):
    """GUI 版本的手動標記（需要顯示環境）"""
    print("啟動圖形界面，請點擊圖片選擇四個校正點，按 ESC 結束")
    
    points = []
    
    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and len(points) < 4:
            points.append((x, y))
            print(f"選擇點 {len(points)}: ({x}, {y})")
            
            # 在圖片上標記點
            cv2.circle(image_display, (x, y), 8, (0, 0, 255), -1)
            cv2.putText(image_display, f'P{len(points)}', (x+10, y-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            cv2.imshow("Manual Selection", image_display)
    
    # 準備顯示圖片
    image_display = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    
    try:
        # 設置鼠標回調
        cv2.namedWindow("Manual Selection", cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback("Manual Selection", mouse_callback)
        cv2.imshow("Manual Selection", image_display)
        
        # 等待用戶操作
        while len(points) < 4:
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC 鍵
                break
        
        cv2.destroyAllWindows()
        
        if len(points) == 4:
            print("✓ 成功選擇了4個校正點")
            # 校正 4 個點 ，必須為正方形
            # 左下點須對齊左上點 (對 x 值)
            # 右下點須對齊右上點 (對 x 值)
            # 左上點須對齊右上點 (對 y 值)
            
            # 自動校正四個點
            corrected_points = correct_points_to_rectangle(points)
            if corrected_points:
                points = corrected_points
                print(f"✓ 已自動校正為矩形: {points}")
                
                # 重新繪製校正後的點
                image_display = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
                for i, (x, y) in enumerate(points):
                    cv2.circle(image_display, (x, y), 8, (0, 255, 0), -1)  # 綠色表示校正後
                    cv2.putText(image_display, f'P{i+1}', (x+10, y-10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                
                # 繪製矩形邊框
                pts = np.array(points, np.int32)
                cv2.polylines(image_display, [pts], True, (0, 255, 0), 2)
                cv2.imshow("Manual Selection", image_display)
                cv2.waitKey(1000)  # 顯示1秒讓用戶看到校正結果
            
            result_image = image_display.copy()
            cv2.imwrite("assets/manual_selection_result.png", result_image)
            print("✓ 已儲存手動選擇結果到 assets/manual_selection_result.png")
        else:
            print("✗ 未完成選擇，需要4個點")
            
    except Exception as e:
        print(f"圖形界面啟動失敗: {e}")
        cv2.destroyAllWindows()
        return []
    
    return points

def correct_points_to_rectangle(points):
    """將4個點校正為標準矩形"""
    if len(points) != 4:
        print("⚠ 需要4個點才能進行校正")
        return None
    
    print("=== 開始校正四個點 ===")
    print(f"原始點: {points}")
    
    # 根據座標判斷四個點的大概位置
    # 按y座標排序，前兩個是上方的點，後兩個是下方的點
    sorted_by_y = sorted(points, key=lambda p: p[1])
    top_points = sorted(sorted_by_y[:2], key=lambda p: p[0])  # 上方兩點按x排序
    bottom_points = sorted(sorted_by_y[2:], key=lambda p: p[0])  # 下方兩點按x排序
    
    # 識別四個點
    left_top = top_points[0]      # 左上
    right_top = top_points[1]     # 右上
    left_bottom = bottom_points[0]  # 左下
    right_bottom = bottom_points[1] # 右下
    
    print(f"識別結果:")
    print(f"  左上: {left_top}")
    print(f"  右上: {right_top}")
    print(f"  左下: {left_bottom}")
    print(f"  右下: {right_bottom}")
    
    # 按照要求進行校正
    # 1. 左上點須對齊右上點 (對 y 值) - 取平均值
    top_y = (left_top[1] + right_top[1]) // 2
    
    # 2. 左下點須對齊左上點 (對 x 值)
    left_x = left_top[0]
    
    # 3. 右下點須對齊右上點 (對 x 值)  
    right_x = right_top[0]
    
    # 4. 左下點和右下點的y值取平均
    bottom_y = (left_bottom[1] + right_bottom[1]) // 2
    
    # 生成校正後的四個點
    corrected_points = [
        (left_x, top_y),      # 校正後的左上
        (right_x, top_y),     # 校正後的右上  
        (right_x, bottom_y),  # 校正後的右下
        (left_x, bottom_y)    # 校正後的左下
    ]
    
    print(f"校正後的點:")
    print(f"  左上: {corrected_points[0]}")
    print(f"  右上: {corrected_points[1]}")
    print(f"  右下: {corrected_points[2]}")
    print(f"  左下: {corrected_points[3]}")
    
    # 計算矩形的寬度和高度
    width = right_x - left_x
    height = bottom_y - top_y
    print(f"矩形尺寸: 寬度={width}, 高度={height}")
    
    return corrected_points 