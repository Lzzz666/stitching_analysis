import cv2
import numpy as np
import os
from target_center import find_center_by_contours, find_center_by_hough_lines, find_center_by_corners

def extract_target_manually(image):
    print("=== select target region ===")
    print("Please drag to select a target region")
    
    # 創建圖像副本用於顯示
    display_image = cv2.cvtColor(image.copy(), cv2.COLOR_GRAY2BGR)

    try:
        # 使用cv2.selectROI來框選區域
        print("Info: drag to select target region → Space/Enter confirm → ESC cancel")
        roi = cv2.selectROI("select target region", display_image, False, False)
        cv2.destroyAllWindows()
        
        x, y, w, h = roi
        
        if w > 0 and h > 0:
            # 提取選擇的區域
            target_region = image[y:y+h, x:x+w]
            
            # 保存提取的target
            cv2.imwrite('assets/extracted_target.png', target_region)
            print(f"✓ extracted target: position({x},{y}), size({w}x{h})")
            print("✓ saved to assets/extracted_target.png")
            
            return target_region
        else:
            print("⚠ invalid region")
            return None
            
    except Exception as e:
        print(f"⚠ failed to select target region: {e}")
        return None

def find_octagon_pattern_matching(image):
    print("=== pattern matching ===")
    
    target = extract_target_manually(image)
    if target is None:
        print("⚠ failed to get target template, cannot perform matching")
        return []

    h, w = target.shape
    
    if h > image.shape[0] or w > image.shape[1]:
        print("⚠ template size is too large, cannot perform matching")
        return []

    result = cv2.matchTemplate(image, target, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    
    if max_val < 0.3:
        threshold = max_val * 0.8
        print(f"best matching score is too low, adjust threshold to: {threshold:.3f}")
    elif max_val < 0.6:
        threshold = 0.4
        print(f"use medium threshold: {threshold:.3f}")
    else:
        threshold = 0.6
        print(f"use standard threshold: {threshold:.3f}")
    
    locations = np.where(result >= threshold)

    print(f"found {len(locations[0])} matching positions")

    # for y_pos, x_pos in zip(locations[0], locations[1]):
    #     cv2.rectangle(image, (x_pos, y_pos), (x_pos + w, y_pos + h), (0, 255, 0), 2)

    # 5. 過濾重複匹配 - 改進版本：在相近的匹配中選擇最佳的
    all_matches = []
    min_distance = min(w, h) // 2
    
    # 先收集所有匹配
    for y_pos, x_pos in zip(locations[0], locations[1]):
        match_score = result[y_pos, x_pos]
        all_matches.append((x_pos, y_pos, match_score))
    
    # 按得分排序（從高到低）
    all_matches.sort(key=lambda x: x[2], reverse=True)
    
    filtered_matches = []
    
    for x_pos, y_pos, match_score in all_matches:
        # 檢查是否與已選中的匹配太接近
        is_duplicate = False
        for existing_x, existing_y, _ in filtered_matches:
            distance = np.sqrt((x_pos - existing_x)**2 + (y_pos - existing_y)**2)
            if distance < min_distance:
                is_duplicate = True
                break
        
        # 如果不重複，或者這是該區域得分最高的，就保留
        if not is_duplicate:
            filtered_matches.append((x_pos, y_pos, match_score))
    
    print(f"found {len(filtered_matches)} valid matches")
    
    result_image = cv2.cvtColor(image.copy(), cv2.COLOR_GRAY2BGR)
    all_corners = []
    center_of_octagon = []
    for i, (x, y, score) in enumerate(filtered_matches):
        print(f"match {i+1}: position({x},{y}), score: {score:.3f}")
        
        corners = [
            (x, y),           # top left
            (x + w, y),       # top right
            (x + w, y + h),   # bottom right
            (x, y + h)        # bottom left
        ]
        all_corners.extend(corners)
        
        cv2.rectangle(result_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(result_image, f'Match{i+1}: {score:.2f}', 
                   (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        for j, (cx, cy) in enumerate(corners):
            cv2.circle(result_image, (cx, cy), 5, (0, 0, 255), -1)
            cv2.putText(result_image, f'P{j+1}', 
                       (cx + 5, cy - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 0, 0), 1)

        roi = image[y:y+h, x:x+w]
        center, result = find_center_by_hough_lines(roi)
        print(f"center: {center}")

        center_of_octagon.append((x+center[0], y+center[1]))
        cv2.circle(result_image, (x+center[0], y+center[1]), 5, (0, 0, 255), -1)
        cv2.putText(result_image, f'O{i+1}', 
                   (x+center[0]+5, y+center[1]-5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 0, 0), 1)

    if len(filtered_matches) < 4:
        print("⚠ found less than 4 corners, cannot perform calibration")
        return []

    cv2.imwrite('assets/pattern_matching_result.png', result_image)
    print(f"✓ pattern matching completed, found {len(all_corners)} corners")
    print("✓ result saved to assets/pattern_matching_result.png")
    
    return center_of_octagon

def find_octagon_manual(image):
    """manual marking 4 correction points"""
    print("=== manual marking correction points ===")
    print(f"image size: {image.shape}")
    
    # check environment
    is_ssh = 'SSH_CONNECTION' in os.environ or 'SSH_CLIENT' in os.environ
    has_display = (
        'DISPLAY' in os.environ or 
        'WAYLAND_DISPLAY' in os.environ or 
        os.name == 'nt'
    ) and not is_ssh
    
    if has_display:
        return find_octagon_manual_gui(image)
    else:
        print("⚠ no graphical environment")
        print("tips:")
        print("1. make sure to run in a graphical environment")
        print("2. or use template matching function")
        return []

def find_octagon_manual_gui(image):
    """GUI version of manual marking"""
    print("start GUI, please click to select 4 correction points, press ESC to end")
    
    points = []
    
    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and len(points) < 4:
            points.append((x, y))
            print(f"selected point {len(points)}: ({x}, {y})")
            
            # 在圖像上標記點
            cv2.circle(param, (x, y), 5, (0, 255, 0), -1)
            cv2.putText(param, f'P{len(points)}', (x+10, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            cv2.imshow("Manual Selection", param)
            
            if len(points) == 4:
                print("✓ selected 4 points, press any key to continue")
    
    try:
        # 創建顯示圖像
        display_image = cv2.cvtColor(image.copy(), cv2.COLOR_GRAY2BGR)
        
        cv2.imshow("Manual Selection", display_image)
        cv2.setMouseCallback("Manual Selection", mouse_callback, display_image)
        
        print("instructions:")
        print("- left click to select correction points")
        print("- need to select 4 points")
        print("- press ESC to end")
        
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        if len(points) == 4:
            print(f"✓ manual selection completed: {points}")
            
            # 保存結果
            result_image = cv2.cvtColor(image.copy(), cv2.COLOR_GRAY2BGR)
            for i, (x, y) in enumerate(points):
                cv2.circle(result_image, (x, y), 8, (0, 255, 0), -1)
                cv2.putText(result_image, f'P{i+1}', (x+10, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            cv2.imwrite('assets/manual_selection_result.png', result_image)
            print("✓ result saved to assets/manual_selection_result.png")
            
        return points
        
    except Exception as e:
        print(f"⚠ GUI manual marking failed: {e}")
        return []

def correct_points_to_rectangle(points):
    """correct 4 points to a standard rectangle"""
    if len(points) != 4:
        print("⚠ need exactly 4 points to correct to rectangle")
        return points
    
    # 找到邊界
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    
    min_x, max_x = min(x_coords), max(x_coords)
    min_y, max_y = min(y_coords), max(y_coords)
    
    # 生成標準矩形的四個角點
    corrected_points = [
        (min_x, min_y),  # top left
        (max_x, min_y),  # top right
        (max_x, max_y),  # bottom right
        (min_x, max_y)   # bottom left
    ]
    
    print(f"original points: {points}")
    print(f"corrected points: {corrected_points}")
    
    return corrected_points 