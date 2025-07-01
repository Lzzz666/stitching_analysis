import numpy as np

def calculate_color_delta(left_rgb, left_pos, right_rgb, right_pos):

    left_rgb_float = left_rgb.astype(np.float64)
    right_rgb_float = right_rgb.astype(np.float64)

    left_r_mean = 0
    left_r_cnt = 0
    for i in range(len(left_rgb_float)):
        if left_rgb_float[i][0] == 255:
            continue
        left_r_mean += left_rgb_float[i][0]
        left_r_cnt += 1
    left_r_mean /= left_r_cnt

 
    left_g_mean = 0
    left_g_cnt = 0
    for i in range(len(left_rgb_float)):
        if left_rgb_float[i][1] == 255:
            continue
        left_g_mean += left_rgb_float[i][1]
        left_g_cnt += 1
    left_g_mean /= left_g_cnt

    left_b_mean = 0
    left_b_cnt = 0
    for i in range(len(left_rgb_float)):
        if left_rgb_float[i][2] == 255:
            continue
        left_b_mean += left_rgb_float[i][2]
        left_b_cnt += 1
    left_b_mean /= left_b_cnt


    right_r_mean = 0
    right_r_cnt = 0
    for i in range(len(right_rgb_float)):
        if right_rgb_float[i][0] == 255:
            continue
        right_r_mean += right_rgb_float[i][0]
        right_r_cnt += 1    
    right_r_mean /= right_r_cnt

    right_g_mean = 0
    right_g_cnt = 0
    for i in range(len(right_rgb_float)):
        if right_rgb_float[i][1] == 255:
            continue
        right_g_mean += right_rgb_float[i][1]
        right_g_cnt += 1    
    right_g_mean /= right_g_cnt

    right_b_mean = 0
    right_b_cnt = 0
    for i in range(len(right_rgb_float)):
        if right_rgb_float[i][2] == 255:
            continue
        right_b_mean += right_rgb_float[i][2]
        right_b_cnt += 1    
    right_b_mean /= right_b_cnt

    # calculate delta_e
    delta_r = right_r_mean - left_r_mean
    delta_g = right_g_mean - left_g_mean
    delta_b = right_b_mean - left_b_mean
    delta_e = np.sqrt(delta_r**2 + delta_g**2 + delta_b**2)
    
    return delta_e