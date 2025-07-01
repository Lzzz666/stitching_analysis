import cv2
import numpy as np
import matplotlib.pyplot as plt

def plot_rgb_analysis(left_rgb, left_pos, right_rgb, right_pos):
    """plot the RGB analysis chart"""
    
    # set the Chinese font (to handle Chinese display issues)
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    # create a 3x2 subplot layout: 3 rows (R, G, B), 2 columns (left line, right line)
    fig, axes = plt.subplots(3, 2, figsize=(15, 12))
    fig.suptitle('RGB value analysis - display by channel', fontsize=16, fontweight='bold')
    
    colors = ['red', 'green', 'blue']
    channel_names = ['Red', 'Green', 'Blue']
    channel_names_ch = ['red channel', 'green channel', 'blue channel']
    
    # plot the RGB value of the left line (first column)
    for i in range(3):
        axes[i, 0].plot(left_pos, left_rgb[:, i], color=colors[i], linewidth=2.5)
        axes[i, 0].set_title(f'left line - {channel_names_ch[i]}', fontsize=12, fontweight='bold')
        axes[i, 0].set_ylabel(f'{channel_names[i]} value (0-255)', fontsize=10)
        axes[i, 0].grid(True, alpha=0.3)
        axes[i, 0].set_ylim(0, 255)
        axes[i, 0].fill_between(left_pos, left_rgb[:, i], alpha=0.3, color=colors[i])
        
        # only add the x-axis label on the bottommost figure
        if i == 2:
            axes[i, 0].set_xlabel('distance from the starting point', fontsize=10)
    
    # plot the RGB value of the right line (second column)
    for i in range(3):
        axes[i, 1].plot(right_pos, right_rgb[:, i], color=colors[i], linewidth=2.5)
        axes[i, 1].set_title(f'right line - {channel_names_ch[i]}', fontsize=12, fontweight='bold')
        axes[i, 1].set_ylabel(f'{channel_names[i]} value (0-255)', fontsize=10)
        axes[i, 1].grid(True, alpha=0.3)
        axes[i, 1].set_ylim(0, 255)
        axes[i, 1].fill_between(right_pos, right_rgb[:, i], alpha=0.3, color=colors[i])
        
        # only add the x-axis label on the bottommost figure
        if i == 2:
            axes[i, 1].set_xlabel('distance from the starting point', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('assets/rgb_analysis_separated.png', dpi=300, bbox_inches='tight')
    print("✓ separated RGB analysis chart saved to assets/rgb_analysis_separated.png")
    
    # generate a comparison chart for easy comparison of the left and right lines
    plot_rgb_comparison(left_rgb, left_pos, right_rgb, right_pos)

def visualize_sampling_lines(image, corners):
    """visualize the sampling lines"""
    if len(corners) != 4:
        return
    
    # create the result image
    result_image = image.copy()
    if len(result_image.shape) == 2:
        result_image = cv2.cvtColor(result_image, cv2.COLOR_GRAY2BGR)
    
    # determine the position of the four points
    sorted_corners = sorted(corners, key=lambda p: p[1])
    top_points = sorted(sorted_corners[:2], key=lambda p: p[0])
    bottom_points = sorted(sorted_corners[2:], key=lambda p: p[0])
    
    left_top = top_points[0]
    right_top = top_points[1]
    left_bottom = bottom_points[0]
    right_bottom = bottom_points[1]
    
    # draw the two sampling lines
    cv2.line(result_image, left_top, left_bottom, (255, 0, 0), 3)  # blue left line
    cv2.line(result_image, right_top, right_bottom, (0, 255, 0), 3)  # green right line
    
    # mark the four corners
    for i, point in enumerate([left_top, right_top, left_bottom, right_bottom]):
        cv2.circle(result_image, point, 8, (0, 0, 255), -1)
        labels = ['left_top', 'right_top', 'left_bottom', 'right_bottom']
        cv2.putText(result_image, labels[i], (point[0]+10, point[1]-10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    
    cv2.imwrite('assets/sampling_lines.png', result_image)
    print("✓ sampling lines chart saved to assets/sampling_lines.png")
    
    return result_image

def plot_rgb_comparison(left_rgb, left_pos, right_rgb, right_pos):
    """plot the RGB comparison chart of the left and right lines"""
    
    fig, axes = plt.subplots(3, 1, figsize=(15, 10))
    fig.suptitle('RGB value comparison of the left and right lines', fontsize=16, fontweight='bold')
    
    colors = ['red', 'green', 'blue']
    channel_names_ch = ['red channel comparison', 'green channel comparison', 'blue channel comparison']
    
    for i in range(3):
        # plot the left line (solid line)
        axes[i].plot(left_pos, left_rgb[:, i], color=colors[i], linewidth=2, 
                    label='left line', linestyle='-')
        # plot the right line (dashed line)
        axes[i].plot(right_pos, right_rgb[:, i], color=colors[i], linewidth=2, 
                    label='right line', linestyle='--', alpha=0.8)
        
        axes[i].set_title(channel_names_ch[i], fontsize=12, fontweight='bold')
        axes[i].set_ylabel(f'{colors[i].capitalize()} 值 (0-255)', fontsize=10)
        axes[i].grid(True, alpha=0.3)
        axes[i].set_ylim(0, 255)
        axes[i].legend()
        
        # only add the x-axis label on the bottommost figure
        if i == 2:
            axes[i].set_xlabel('distance from the starting point', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('assets/rgb_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("✓ RGB comparison chart saved to assets/rgb_comparison.png") 

def print_center_line(image, corners):
    """print the center line"""
    if len(corners) != 4:
        return
    
    # determine the position of the four points
    sorted_corners = sorted(corners, key=lambda p: p[1])
    top_points = sorted(sorted_corners[:2], key=lambda p: p[0])
    bottom_points = sorted(sorted_corners[2:], key=lambda p: p[0])
    
    left_top = top_points[0]
    right_top = top_points[1]
    mid_top = (left_top[0] + right_top[0]) // 2, (left_top[1] + right_top[1]) // 2

    left_bottom = bottom_points[0]
    right_bottom = bottom_points[1]
    mid_bottom = (left_bottom[0] + right_bottom[0]) // 2, (left_bottom[1] + right_bottom[1]) // 2
    
    # draw the center line
    cv2.line(image, mid_top, mid_bottom, (0, 0, 255), 3)
    cv2.imwrite('assets/center_line.png', image)
    print("✓ center line chart saved to assets/center_line.png")