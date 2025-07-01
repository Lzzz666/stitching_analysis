import numpy as np
from image_processing import sample_line_rgb
from visualization import plot_rgb_analysis
from color_delta import calculate_color_delta

def analyze_color_lines(image, corners):
    """analyze the RGB value change between the correction points"""
    if len(corners) != 4:
        print(f"⚠ need 4 correction points, currently only {len(corners)} points")
        return
    
    print("=== color analysis ===")
    

    sorted_corners = sorted(corners, key=lambda p: p[1])
    top_points = sorted(sorted_corners[:2], key=lambda p: p[0]) 
    bottom_points = sorted(sorted_corners[2:], key=lambda p: p[0])
    
    left_top = top_points[0]      
    right_top = top_points[1]     
    left_bottom = bottom_points[0]  
    right_bottom = bottom_points[1] 
    
    left_line_rgb, left_positions = sample_line_rgb(image, left_top, left_bottom)
    right_line_rgb, right_positions = sample_line_rgb(image, right_top, right_bottom)
    
    

    # filter out values greater than 250, and set values greater than 250 to 300 (because the maximum value of RGB is 255)
    left_line_rgb[left_line_rgb > 250] = 255
    right_line_rgb[right_line_rgb > 250] = 255
    # for the left line: cut off the first 10% and the last 35%
    y = left_bottom[1] - left_top[1]

    left_line_rgb = left_line_rgb[int(0.1*y):int(y - 0.35 * y)]
    left_positions = left_positions[int(0.1*y):int(y - 0.35 * y)]
    # for the right line: cut off the first 20% and the last 10%
    right_line_rgb = right_line_rgb[int(0.2*y):int(y - 0.25 * y)]
    right_positions = right_positions[int(0.2*y):int(y - 0.25 * y)]

    plot_rgb_analysis(left_line_rgb, left_positions, right_line_rgb, right_positions)

    delta_e = calculate_color_delta(left_line_rgb, left_positions, right_line_rgb, right_positions)
    return left_line_rgb, right_line_rgb, delta_e
