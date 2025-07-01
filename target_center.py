import cv2
import numpy as np

def visualize_center(target, center):
    """mark the center point on the image"""
    result = target.copy()
    cv2.circle(result, center, 5, (0, 0, 255), -1)
    cv2.circle(result, center, 10, (0, 255, 0), 2)
    return result

def find_center_by_contours(target):
    """find the center by contours"""

    # find contours
    contours, _ = cv2.findContours(target, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        print("no contours found")
        return None, target
    
    # find the largest contour (assume it is the target)
    largest_contour = max(contours, key=cv2.contourArea)
    
    # calculate the centroid
    M = cv2.moments(largest_contour)
    if M['m00'] == 0:
        print("cannot calculate the centroid")
        return None, target
        
    cx = int(M['m10']/M['m00'])
    cy = int(M['m01']/M['m00'])
    center = (cx, cy)
    
    result = visualize_center(target, center)
    return center, result

def find_center_by_hough_lines(target):
    """find the center by hough lines (the intersection of the horizontal and vertical lines)"""
    # use Canny edge detection
    edges = cv2.Canny(target, 50, 150)
    
    # use hough lines
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength=30, maxLineGap=10)
    
    if lines is None:
        print("no lines found")
        return None, target
    
    horizontal_lines = []
    vertical_lines = []
    
    # classify horizontal and vertical lines
    for line in lines:
        x1, y1, x2, y2 = line[0]
        
        # calculate the angle
        angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
        
        # horizontal line (angle near 0 or 180)
        if abs(angle) < 10 or abs(angle) > 170:
            horizontal_lines.append(line[0])
        # vertical
        elif abs(abs(angle) - 90) < 10:
            vertical_lines.append(line[0])
    
    if not horizontal_lines or not vertical_lines:
        print("no enough horizontal or vertical lines")
        return None, target
    
    # find the horizontal and vertical lines closest to the image center
    img_center_x, img_center_y = target.shape[1] // 2, target.shape[0] // 2
    
    best_h_line = min(horizontal_lines, key=lambda line: abs((line[1] + line[3]) / 2 - img_center_y))
    best_v_line = min(vertical_lines, key=lambda line: abs((line[0] + line[2]) / 2 - img_center_x))
    
    # calculate the intersection
    h_y = (best_h_line[1] + best_h_line[3]) / 2
    v_x = (best_v_line[0] + best_v_line[2]) / 2
    
    center = (int(v_x), int(h_y))
    result = visualize_center(target, center)
    
    return center, result

def find_center_by_corners(target):
    """find the center by corners"""
    
    # use goodFeaturesToTrack to find corners
    corners = cv2.goodFeaturesToTrack(target, 25, 0.01, 10)
    
    if corners is None:
        print("no corners found")
        return None, target
    
    # calculate the average position of all corners as the center
    corners = corners.astype(np.int32)
    center_x = np.mean(corners[:, 0, 0])
    center_y = np.mean(corners[:, 0, 1])
    center = (int(center_x), int(center_y))
    
    result = visualize_center(target, center)
    
    # optional: mark all corners on the result image
    for corner in corners:
        x, y = corner.ravel()
        cv2.circle(result, (int(x), int(y)), 3, (255, 0, 0), -1)
    
    return center, result
