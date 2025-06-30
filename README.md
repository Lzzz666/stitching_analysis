# 色彩分析系統 - 重構版本

這個項目用於分析左右兩條採樣線的色差，支持圖像處理、校正點檢測、色彩分析和結果可視化。

## 項目結構

```
stitching_analysis/
├── main_new.py              # 主程序（重構版本）
├── main.py                  # 原始主程序（保留作為備份）
├── image_processing.py      # 圖像處理模組
├── calibration.py          # 校正點檢測模組
├── color_analysis.py       # 色彩分析模組
├── color_delta.py          # 色差計算模組
├── visualization.py        # 可視化模組
├── utils.py                # 工具函式模組
├── README.md               # 項目說明
└── assets/                 # 資源目錄
    ├── image_bias_test.png     # 測試圖片
    ├── target.png              # 模板圖片（可選）
    └── [生成的輸出圖片]
```

## 模組說明

### 1. image_processing.py
- `load_image()` - 讀取圖片
- `convert_to_gray()` - 轉換為灰度圖
- `sample_line_rgb()` - 沿線段採樣RGB值

### 2. calibration.py
- `find_octagon_pattern_matching()` - 模板匹配檢測校正點
- `find_octagon_manual()` - 手動標記校正點
- `find_octagon_manual_gui()` - GUI版本手動標記
- `correct_points_to_rectangle()` - 校正點為矩形

### 3. color_analysis.py
- `analyze_color_lines()` - 分析校正點間線段RGB值變化
- `detect_color_bars_automatically()` - 自動檢測色帶區域
- `align_color_samples()` - 對齊色彩採樣點

### 4. color_delta.py
- `calculate_color_delta()` - 主要色差計算函式
- `calculate_region_delta_e()` - 計算指定區域色差
- `calculate_rgb_delta()` - RGB色差計算
- `calculate_lab_delta_e()` - LAB色彩空間色差計算
- `calculate_hsv_delta()` - HSV色差計算
- 各種色彩空間轉換函式

### 5. visualization.py
- `plot_rgb_analysis()` - 繪製RGB分析圖
- `plot_color_delta_analysis()` - 可視化色差分析結果
- `visualize_region_analysis()` - 可視化區域分析結果
- `visualize_sampling_lines()` - 可視化採樣線段
- `plot_rgb_comparison()` - 繪製左右線段RGB比較圖
- `print_color_delta_statistics()` - 輸出色差統計信息

### 6. utils.py
- `save_results()` - 儲存標記結果

## 使用方法

### 基本使用
```bash
python main_new.py
```

### 啟用模板匹配
修改 `main_new.py` 中的 `use_template_matching = True`

### 自定義校正點
如果手動標記失敗，程序會使用預設校正點。可以在代碼中修改：
```python
main_corners = [(100, 100), (400, 100), (400, 300), (100, 300)]
```

## 輸出檔案

程序會在 `assets/` 目錄下生成以下檔案：

1. **gray_image.png** - 灰度圖
2. **sampling_lines.png** - 採樣線段圖
3. **rgb_analysis_separated.png** - 分離式RGB分析圖
4. **rgb_comparison.png** - RGB比較圖
5. **color_delta_analysis.png** - 色差分析圖
6. **region_color_analysis.png** - 區域色差分析圖

## 依賴項

```bash
pip install opencv-python numpy matplotlib scikit-image
```

注意：`scikit-image` 是可選的，如果沒有安裝會使用簡化版LAB轉換。

## 重構改進

相比原始版本，重構版本有以下改進：

1. **模組化設計** - 功能分離，代碼更清晰
2. **避免循環導入** - 使用動態導入解決依賴問題
3. **更好的錯誤處理** - 提供備用方案和詳細錯誤信息
4. **清晰的文檔** - 每個模組和函式都有詳細說明
5. **靈活配置** - 可以輕鬆啟用/禁用不同功能

## 主要功能

- **圖像處理** - 支持多種格式圖片讀取和處理
- **校正點檢測** - 支持模板匹配和手動標記兩種方式
- **色彩分析** - 精確的RGB線段採樣和分析
- **色差計算** - 支持RGB、LAB、HSV三種色彩空間的色差計算
- **區域性分析** - 自動檢測色帶區域並分別計算色差
- **結果可視化** - 生成多種分析圖表
- **統計報告** - 詳細的色差統計和評估

## 故障排除

1. **無法讀取圖片**
   - 確保 `assets/image_bias_test.png` 存在
   - 檢查圖片格式是否支持

2. **手動標記失敗**
   - 確保在有圖形界面的環境中運行
   - 檢查顯示環境變量設置

3. **模組導入錯誤**
   - 確保所有模組檔案在同一目錄
   - 檢查Python路徑設置

4. **色差計算錯誤**
   - 檢查校正點是否正確
   - 確保採樣線段在圖片範圍內 