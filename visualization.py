import cv2
import numpy as np
import matplotlib.pyplot as plt

def visualize_region_analysis(left_rgb, right_rgb, regions, region_results):
    """可視化區域分析結果"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('區域性色差分析結果', fontsize=16, fontweight='bold')
    
    x_axis = range(len(left_rgb))
    colors = ['red', 'green', 'blue']
    
    # 左上：左邊線段 + 區域標記
    for i in range(3):
        axes[0, 0].plot(x_axis, left_rgb[:, i], color=colors[i], alpha=0.7, linewidth=1)
    
    # 標記各個檢測區域
    region_colors = ['yellow', 'orange', 'lightgreen', 'lightblue', 'pink']
    for idx, (name, (start, end)) in enumerate(regions.items()):
        color = region_colors[idx % len(region_colors)]
        axes[0, 0].axvspan(start, end, alpha=0.3, color=color, label=name)
    
    axes[0, 0].set_title('左邊線段 - 區域劃分')
    axes[0, 0].set_ylabel('RGB值')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # 右上：右邊線段 + 區域標記
    for i in range(3):
        axes[0, 1].plot(x_axis, right_rgb[:, i], color=colors[i], alpha=0.7, linewidth=1)
    
    for idx, (name, (start, end)) in enumerate(regions.items()):
        color = region_colors[idx % len(region_colors)]
        axes[0, 1].axvspan(start, end, alpha=0.3, color=color, label=name)
    
    axes[0, 1].set_title('右邊線段 - 區域劃分')
    axes[0, 1].set_ylabel('RGB值')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # 左下：各區域的平均顏色對比
    region_names = list(region_results.keys())
    delta_e_values = [region_results[name]['delta_e'] for name in region_names]
    rgb_distances = [region_results[name]['rgb_distance'] for name in region_names]
    
    x_pos = np.arange(len(region_names))
    width = 0.35
    
    axes[1, 0].bar(x_pos - width/2, delta_e_values, width, label='ΔE76', alpha=0.8)
    axes[1, 0].bar(x_pos + width/2, np.array(rgb_distances)/10, width, label='RGB距離/10', alpha=0.8)
    
    axes[1, 0].set_title('各區域色差對比')
    axes[1, 0].set_ylabel('色差值')
    axes[1, 0].set_xlabel('色帶區域')
    axes[1, 0].set_xticks(x_pos)
    axes[1, 0].set_xticklabels(region_names, rotation=45)
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # 右下：色差評估表
    axes[1, 1].axis('off')
    
    # 創建評估表格
    table_data = []
    headers = ['區域', 'ΔE76', 'RGB距離', '評估']
    
    for name in region_names:
        delta_e = region_results[name]['delta_e']
        rgb_dist = region_results[name]['rgb_distance']
        
        # 色差評估
        if delta_e < 1:
            assessment = "極小"
        elif delta_e < 3:
            assessment = "小"
        elif delta_e < 6:
            assessment = "中等"
        elif delta_e < 12:
            assessment = "大"
        else:
            assessment = "非常大"
            
        table_data.append([name, f'{delta_e:.3f}', f'{rgb_dist:.1f}', assessment])
    
    table = axes[1, 1].table(cellText=table_data, colLabels=headers,
                           cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)
    
    axes[1, 1].set_title('色差評估摘要', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('assets/region_color_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("✓ 區域色差分析圖已儲存到 assets/region_color_analysis.png")

def plot_color_delta_analysis(delta_rgb, delta_e_lab, delta_hsv):
    """可視化色差分析結果"""
    fig, axes = plt.subplots(3, 2, figsize=(16, 12))
    fig.suptitle('色差分析結果', fontsize=16, fontweight='bold')
    
    x_axis = range(len(delta_rgb['magnitude']))
    
    # RGB色差
    axes[0, 0].plot(x_axis, delta_rgb['delta_r'], 'r-', linewidth=2, label='ΔR')
    axes[0, 0].plot(x_axis, delta_rgb['delta_g'], 'g-', linewidth=2, label='ΔG')
    axes[0, 0].plot(x_axis, delta_rgb['delta_b'], 'b-', linewidth=2, label='ΔB')
    axes[0, 0].set_title('RGB通道色差', fontweight='bold')
    axes[0, 0].set_ylabel('色差值')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].axhline(y=0, color='black', linestyle='--', alpha=0.5)
    
    axes[0, 1].plot(x_axis, delta_rgb['magnitude'], 'purple', linewidth=2)
    axes[0, 1].set_title('RGB歐式距離色差', fontweight='bold')
    axes[0, 1].set_ylabel('色差大小')
    axes[0, 1].grid(True, alpha=0.3)
    
    # LAB色差
    axes[1, 0].plot(x_axis, delta_e_lab['delta_l'], 'gray', linewidth=2, label='ΔL*')
    axes[1, 0].plot(x_axis, delta_e_lab['delta_a'], 'red', linewidth=2, label='Δa*')
    axes[1, 0].plot(x_axis, delta_e_lab['delta_b_lab'], 'orange', linewidth=2, label='Δb*')
    axes[1, 0].set_title('LAB色彩空間色差', fontweight='bold')
    axes[1, 0].set_ylabel('色差值')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 0].axhline(y=0, color='black', linestyle='--', alpha=0.5)
    
    axes[1, 1].plot(x_axis, delta_e_lab['delta_e'], 'darkred', linewidth=2)
    axes[1, 1].set_title('ΔE76色差', fontweight='bold')
    axes[1, 1].set_ylabel('ΔE值')
    axes[1, 1].grid(True, alpha=0.3)
    
    # HSV色差
    axes[2, 0].plot(x_axis, delta_hsv['delta_h'], 'cyan', linewidth=2, label='ΔH')
    axes[2, 0].plot(x_axis, delta_hsv['delta_s'], 'magenta', linewidth=2, label='ΔS')
    axes[2, 0].plot(x_axis, delta_hsv['delta_v'], 'yellow', linewidth=2, label='ΔV')
    axes[2, 0].set_title('HSV色彩空間色差', fontweight='bold')
    axes[2, 0].set_ylabel('色差值')
    axes[2, 0].set_xlabel('採樣點位置')
    axes[2, 0].legend()
    axes[2, 0].grid(True, alpha=0.3)
    axes[2, 0].axhline(y=0, color='black', linestyle='--', alpha=0.5)
    
    # 綜合色差比較
    axes[2, 1].plot(x_axis, delta_rgb['magnitude']/np.max(delta_rgb['magnitude']), 
                   'purple', linewidth=2, label='RGB距離(歸一化)')
    axes[2, 1].plot(x_axis, delta_e_lab['delta_e']/np.max(delta_e_lab['delta_e']), 
                   'darkred', linewidth=2, label='ΔE76(歸一化)')
    axes[2, 1].set_title('歸一化色差比較', fontweight='bold')
    axes[2, 1].set_ylabel('歸一化色差值')
    axes[2, 1].set_xlabel('採樣點位置')
    axes[2, 1].legend()
    axes[2, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('assets/color_delta_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("✓ 色差分析圖已儲存到 assets/color_delta_analysis.png")

def print_color_delta_statistics(delta_rgb, delta_e_lab, delta_hsv):
    """輸出色差統計信息"""
    print("\n=== 色差統計摘要 ===")
    
    print(f"RGB色差統計:")
    print(f"  平均RGB距離: {np.mean(delta_rgb['magnitude']):.2f}")
    print(f"  最大RGB距離: {np.max(delta_rgb['magnitude']):.2f}")
    print(f"  最小RGB距離: {np.min(delta_rgb['magnitude']):.2f}")
    print(f"  RGB距離標準差: {np.std(delta_rgb['magnitude']):.2f}")
    
    print(f"\nLAB色差統計:")
    print(f"  平均ΔE76: {np.mean(delta_e_lab['delta_e']):.2f}")
    print(f"  最大ΔE76: {np.max(delta_e_lab['delta_e']):.2f}")
    print(f"  最小ΔE76: {np.min(delta_e_lab['delta_e']):.2f}")
    print(f"  ΔE76標準差: {np.std(delta_e_lab['delta_e']):.2f}")
    
    print(f"\nHSV色差統計:")
    print(f"  平均色相差: {np.mean(np.abs(delta_hsv['delta_h'])):.2f}°")
    print(f"  平均飽和度差: {np.mean(np.abs(delta_hsv['delta_s'])):.3f}")
    print(f"  平均明度差: {np.mean(np.abs(delta_hsv['delta_v'])):.3f}")
    
    # 色差評估
    avg_delta_e = np.mean(delta_e_lab['delta_e'])
    if avg_delta_e < 1:
        assessment = "極小，幾乎無法察覺"
    elif avg_delta_e < 3:
        assessment = "小，熟練觀察者可察覺"
    elif avg_delta_e < 6:
        assessment = "中等，一般觀察者可察覺"
    elif avg_delta_e < 12:
        assessment = "大，明顯色差"
    else:
        assessment = "非常大，顯著色差"
    
    print(f"\n色差評估: {assessment} (平均ΔE76: {avg_delta_e:.2f})")

def plot_rgb_analysis(left_rgb, left_pos, right_rgb, right_pos):
    """繪製RGB分析圖表"""
    
    # 設置中文字體（處理中文顯示問題）
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 創建3x2的子圖布局：3行（R、G、B），2列（左線、右線）
    fig, axes = plt.subplots(3, 2, figsize=(15, 12))
    fig.suptitle('RGB值分析 - 分通道顯示', fontsize=16, fontweight='bold')
    
    colors = ['red', 'green', 'blue']
    channel_names = ['Red', 'Green', 'Blue']
    channel_names_ch = ['紅色通道', '綠色通道', '藍色通道']
    
    # 繪製左邊線的RGB值（第一列）
    for i in range(3):
        axes[i, 0].plot(left_pos, left_rgb[:, i], color=colors[i], linewidth=2.5)
        axes[i, 0].set_title(f'左邊線段 - {channel_names_ch[i]}', fontsize=12, fontweight='bold')
        axes[i, 0].set_ylabel(f'{channel_names[i]} 值 (0-255)', fontsize=10)
        axes[i, 0].grid(True, alpha=0.3)
        axes[i, 0].set_ylim(0, 255)
        axes[i, 0].fill_between(left_pos, left_rgb[:, i], alpha=0.3, color=colors[i])
        
        # 只在最下面的圖加x軸標籤
        if i == 2:
            axes[i, 0].set_xlabel('距離起點的像素距離', fontsize=10)
    
    # 繪製右邊線的RGB值（第二列）
    for i in range(3):
        axes[i, 1].plot(right_pos, right_rgb[:, i], color=colors[i], linewidth=2.5)
        axes[i, 1].set_title(f'右邊線段 - {channel_names_ch[i]}', fontsize=12, fontweight='bold')
        axes[i, 1].set_ylabel(f'{channel_names[i]} 值 (0-255)', fontsize=10)
        axes[i, 1].grid(True, alpha=0.3)
        axes[i, 1].set_ylim(0, 255)
        axes[i, 1].fill_between(right_pos, right_rgb[:, i], alpha=0.3, color=colors[i])
        
        # 只在最下面的圖加x軸標籤
        if i == 2:
            axes[i, 1].set_xlabel('距離起點的像素距離', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('assets/rgb_analysis_separated.png', dpi=300, bbox_inches='tight')
    print("✓ 分離式RGB分析圖已儲存到 assets/rgb_analysis_separated.png")
    
    # 同時生成一個比較圖，方便對比左右兩線
    plot_rgb_comparison(left_rgb, left_pos, right_rgb, right_pos)

def visualize_sampling_lines(image, corners):
    """可視化採樣線段"""
    if len(corners) != 4:
        return
    
    # 創建結果圖像
    result_image = image.copy()
    if len(result_image.shape) == 2:
        result_image = cv2.cvtColor(result_image, cv2.COLOR_GRAY2BGR)
    
    # 確定四個點的位置
    sorted_corners = sorted(corners, key=lambda p: p[1])
    top_points = sorted(sorted_corners[:2], key=lambda p: p[0])
    bottom_points = sorted(sorted_corners[2:], key=lambda p: p[0])
    
    left_top = top_points[0]
    right_top = top_points[1]
    left_bottom = bottom_points[0]
    right_bottom = bottom_points[1]
    
    # 繪製兩條採樣線
    cv2.line(result_image, left_top, left_bottom, (255, 0, 0), 3)  # 藍色左線
    cv2.line(result_image, right_top, right_bottom, (0, 255, 0), 3)  # 綠色右線
    
    # 標記四個角點
    for i, point in enumerate([left_top, right_top, left_bottom, right_bottom]):
        cv2.circle(result_image, point, 8, (0, 0, 255), -1)
        labels = ['left_top', 'right_top', 'left_bottom', 'right_bottom']
        cv2.putText(result_image, labels[i], (point[0]+10, point[1]-10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    
    cv2.imwrite('assets/sampling_lines.png', result_image)
    print("✓ 採樣線段圖已儲存到 assets/sampling_lines.png")
    
    return result_image

def plot_rgb_comparison(left_rgb, left_pos, right_rgb, right_pos):
    """繪製左右兩線的RGB比較圖"""
    
    fig, axes = plt.subplots(3, 1, figsize=(15, 10))
    fig.suptitle('左右線段RGB值比較', fontsize=16, fontweight='bold')
    
    colors = ['red', 'green', 'blue']
    channel_names_ch = ['紅色通道比較', '綠色通道比較', '藍色通道比較']
    
    for i in range(3):
        # 繪製左線（實線）
        axes[i].plot(left_pos, left_rgb[:, i], color=colors[i], linewidth=2, 
                    label='左邊線段', linestyle='-')
        # 繪製右線（虛線）
        axes[i].plot(right_pos, right_rgb[:, i], color=colors[i], linewidth=2, 
                    label='右邊線段', linestyle='--', alpha=0.8)
        
        axes[i].set_title(channel_names_ch[i], fontsize=12, fontweight='bold')
        axes[i].set_ylabel(f'{colors[i].capitalize()} 值 (0-255)', fontsize=10)
        axes[i].grid(True, alpha=0.3)
        axes[i].set_ylim(0, 255)
        axes[i].legend()
        
        # 只在最下面的圖加x軸標籤
        if i == 2:
            axes[i].set_xlabel('距離起點的像素距離', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('assets/rgb_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("✓ RGB比較圖已儲存到 assets/rgb_comparison.png") 