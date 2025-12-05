# 報表驗證規則

## 共用

所有報表都會執行的檢查：

- **分類覆蓋率檢查 (step0)**:
  - 檢查上傳的表格是否包含所有分類（分類列表來自「上傳你的分類表」的檔案）
  - 根據報表類型自動檢查 `further_subcategory` 或 `subcategory` 層級的覆蓋率
  - 顯示每個分類的資料筆數，如果資料筆數為 0 則高亮顯示（紅色背景）
  - 如有缺失的分類，提供下載缺失分類清單的功能
  - 輸出：🔔 分類覆蓋率檢查結果（共 [分類總數] 個分類，缺失 [缺失分類數] 個）

- **欄位檢測 (step1)**: 
  - 依照輸入的報表種類與對應欄位規範，判斷是否缺少特定欄位
  - 若沒有缺失欄位，輸出：✅ 沒有缺失重要欄位
  - 若有缺失欄位，輸出所有缺失的欄位：⚠️ missing column: [缺失的欄位名稱]

- **空值分析 (step2)**: 
  - 印出各欄位的空值分佈狀況，以 dataframe 格式呈現
  - 顯示總列數：📊 總列數：[總數]
  - 第一列為空值數量，第二列為空值比例（百分比格式）

- **子品類標籤驗證 (step5)**:
  - 驗證產品分類組合（category, subcategory, further_subcategory）是否符合產品分類規範
  - 支援兩種驗證模式：
    - `mixed`: 同時檢查 subcategory 和 further_subcategory 層級（針對含 stats_type 欄位的報表）
    - `further_subcategory`: 僅檢查 further_subcategory 層級
    - `subcategory`: 僅檢查 subcategory 層級
  - 輸出：🔔 共有[錯誤資料數]筆資料的分類組合不存在於分類資料表中，佔總資料的[比例]%
  - 正常來講，錯誤筆數應該要為 0

## products

執行的檢查規則：
- 共用檢查：step0 (分類覆蓋率), step1 (欄位檢測), step2 (空值分析), step5 (子品類標籤驗證)
- **重複值檢測 (step3)**:
  - 使用 `source_product_id` 作為判定是否重複的欄位
  - 若沒有重複值，輸出：✅ 沒有重複的產品資料
  - 若有，輸出：🔔 Products 有重複值。(提供下載重複列 id 的按鈕)

## products_extend

執行的檢查規則：
- 共用檢查：step0 (分類覆蓋率), step1 (欄位檢測), step2 (空值分析), step5 (子品類標籤驗證)
- **重複值檢測 (step3)**:
  - 使用 `source_product_id`, `extend_class`, `extend_subclass`, `extend_detail` 作為判定是否重複的欄位
  - 若沒有重複值，輸出：✅ 沒有重複的產品擴增屬性資料
  - 若有，輸出：🔔 Products Extend 有重複值。(提供下載重複列 id 的按鈕)

- **擴充屬性檢測 (step4)**:
  - 針對所選報表的擴充屬性規範，判斷資料中是否缺少特定擴充屬性的統計資料
  - 以 dataframe 呈現。缺少的擴充屬性會有 ❌ 標記，存在的會有 ✅ 標記
  - 分析各個 `extend_class` 下，`extend_subclass` 和 `extend_unit` 出現空值的比率
  - 計算方式：
    1. 以 `extend_class` 分組
    2. 計算各組中 `extend_subclass` 和 `extend_unit` 的空值數量
    3. 將空值數量除以該組的總列數，得出空值比例（百分比格式）

## chart_brands

執行的檢查規則：
- 共用檢查：step0 (分類覆蓋率), step1 (欄位檢測), step2 (空值分析), step5 (子品類標籤驗證 - mixed 模式)
- **名次驗證 (step6)**:
  - 列印出品牌排名欄位 (`brand_rank`) 的值域 (unique value)
  - 驗證排名是否符合規範：應為 1-10 或 999
  - 輸出：
    - 🔔 品牌排名
    - - 資料中的名次：[資料中名次的值域]
    - - 規範名次：{1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 999}

## chart_brand (單數)

執行的檢查規則：
- 共用檢查：step0 (分類覆蓋率), step1 (欄位檢測), step2 (空值分析), step5 (子品類標籤驗證 - mixed 模式)
- **名次驗證 (step6)**: 同 chart_brands

## chart_brands_extend

執行的檢查規則：
- 共用檢查：step0 (分類覆蓋率), step1 (欄位檢測), step2 (空值分析), step5 (子品類標籤驗證 - mixed 模式)
- **名次驗證 (step6)**:
  - 驗證 `brand_rank`（品牌排名，範圍：1-5 或 999）
  - 驗證 `extend_detail_rank`（因素統計排名，範圍：1-10 或 999）
  - 驗證 `extend_detail_rank_ordinal`（因素名稱排名，範圍：1-10 或 999）
  - 輸出各排名欄位的資料值域與規範值域比較

- **擴充屬性檢測 (step4)**:
  - 檢查是否缺少特定的擴充屬性（extend_class）
  - 以 dataframe 呈現，缺少的擴充屬性會有 ❌ 標記
  - 分析各個 `extend_class` 下，`extend_subclass` 的空值比率

- **小數點位數驗證 (step7)**:
  - 檢查 `extend_stats` 欄位中的數值格式
  - 驗證 `ratio`：
    - 應最多至小數三位
    - 小數不應以 0 結尾（例如：0.500 應為 0.5）
    - 若有違反，輸出：🔔 extend_stats -> ratio: [X] 列超過 3 位小數 或 [Y] 列小數以 0 結尾
  - 驗證 `avg_price`：
    - 應最多至小數三位
    - 小數不應以 0 結尾
    - 若有違反，輸出：🔔 extend_stats -> avg_price: [X] 列超過 3 位小數 或 [Y] 列小數以 0 結尾
  - 若報表沒有 `extend_stats`，則輸出：✅ 沒有 extend_stats 欄位
  - 檢查完成後輸出：✅ 檢查完成

## chart_brands_extend_cross

執行的檢查規則：
- 共用檢查：step0 (分類覆蓋率), step1 (欄位檢測), step2 (空值分析), step5 (子品類標籤驗證 - mixed 模式)
- **名次驗證 (step6)**: 驗證 `brand_rank`（範圍：1-5 或 999）
- **擴充屬性檢測 (step4)**: 同 chart_brands_extend
- **小數點位數驗證 (step7)**: 同 chart_brands_extend

## chart_brands_extend_image

執行的檢查規則：
- 共用檢查：step0 (分類覆蓋率), step1 (欄位檢測), step2 (空值分析), step5 (子品類標籤驗證 - mixed 模式)
- **名次驗證 (step6)**: 驗證 `brand_rank`（範圍：1-5 或 999）
- **擴充屬性檢測 (step4)**: 同 chart_brands_extend
- **小數點位數驗證 (step7)**: 同 chart_brands_extend

## chart_brand_extend_image (單數)

執行的檢查規則：
- 共用檢查：step0 (分類覆蓋率), step1 (欄位檢測), step2 (空值分析), step5 (子品類標籤驗證 - mixed 模式)
- **名次驗證 (step6)**: 驗證 `brand_rank`（範圍：1-5 或 999）
- **擴充屬性檢測 (step4)**: 同 chart_brands_extend
- **小數點位數驗證 (step7)**: 同 chart_brands_extend

## chart_brands_comment_counts

執行的檢查規則：
- 共用檢查：step0 (分類覆蓋率), step1 (欄位檢測), step2 (空值分析), step5 (子品類標籤驗證 - mixed 模式)
- **名次驗證 (step6)**: 驗證 `brand_rank`（範圍：1-5 或 999）
- **擴充屬性檢測 (step4)**:
  - 檢查是否缺少特定的擴充屬性（正面留言因素、負面留言因素）
  - 注意：此報表的擴充屬性檢測不包含 `extend_subclass` 和 `extend_unit` 空值分析
- **小數點位數驗證 (step7)**: 同 chart_brands_extend

## chart_brand_comment_counts (單數)

執行的檢查規則：
- 共用檢查：step0 (分類覆蓋率), step1 (欄位檢測), step2 (空值分析), step5 (子品類標籤驗證 - mixed 模式)
- **名次驗證 (step6)**: 驗證 `brand_rank`（範圍：1-5 或 999）
- **擴充屬性檢測 (step4)**: 同 chart_brands_comment_counts
- **小數點位數驗證 (step7)**: 同 chart_brands_extend

## chart_brands_comment_score

執行的檢查規則：
- 共用檢查：step0 (分類覆蓋率), step1 (欄位檢測), step2 (空值分析), step5 (子品類標籤驗證 - mixed 模式)
- **名次驗證 (step6)**: 驗證 `brand_rank`（範圍：1-5 或 999）
- **擴充屬性檢測 (step4)**:
  - 檢查是否缺少特定的擴充屬性（正面留言因素、負面留言因素）
  - 以 dataframe 呈現

## chart_brand_comment_score (單數)

執行的檢查規則：
- 共用檢查：step0 (分類覆蓋率), step1 (欄位檢測), step2 (空值分析), step5 (子品類標籤驗證 - mixed 模式)
- **擴充屬性檢測 (step4)**: 同 chart_brands_comment_score

## chart_others

執行的檢查規則：
- 共用檢查：step0 (分類覆蓋率), step1 (欄位檢測), step2 (空值分析), step5 (子品類標籤驗證 - mixed 模式)
- **名次驗證 (step6)**: 驗證 `extend_detail_rank`（因素統計排名，範圍：1-10 或 999）
- **擴充屬性檢測 (step4)**: 同 chart_brands_extend
- **小數點位數驗證 (step7)**: 同 chart_brands_extend

## chart_trends

執行的檢查規則：
- 共用檢查：step0 (分類覆蓋率), step1 (欄位檢測), step2 (空值分析), step5 (子品類標籤驗證 - mixed 模式)
- **名次驗證 (step6)**:
  - 驗證 `element_name_rank`（因素數量排名，範圍：1-5 或 999）
  - 驗證 `element_name_rank_ordinal`（因素名稱排名，範圍：1-5 或 999）
  - 驗證 `labels_rank`（標籤數量排名，範圍：1-10 或 999）
  - 輸出各排名欄位的資料值域與規範值域比較

## reference

執行的檢查規則：
- 共用檢查：step0 (分類覆蓋率), step1 (欄位檢測), step2 (空值分析)
- **子品類標籤驗證 (step5)**: 僅檢查 `further_subcategory` 層級

## keyword

執行的檢查規則：
- 共用檢查：step0 (分類覆蓋率), step1 (欄位檢測), step2 (空值分析)
- **search_volume 檢查**:
  - 檢查是否有列的 `search_volume` 為 0 或空值
  - 若沒有，輸出：✅ 沒有 search_volume 為 0 或空值的資料
  - 若有，輸出：🔔 共有 [X] 列之 search_volume 為 0 或空值！
- **子品類標籤驗證 (step5)**:
  - 分別檢查 `is_brand = True` 和 `is_brand = False` 的資料
  - 兩組資料都進行 `further_subcategory` 層級的分類驗證
  - 分別顯示驗證結果和說明

## 附錄：規則與函數對照表

本附錄列出每條規則對應的函數名稱，方便開發者查找和修改規則的實現。

### 基礎驗證函數

| 規則 | 函數名稱 | 說明 |
|------|----------|------|
| 分類覆蓋率檢查 (step0) | `check_category_coverage` | 檢查上傳的表格是否包含所有分類，支援 `further_subcategory` 和 `subcategory` 層級 |
| 欄位檢測 (step1) | `column_assertion` | 檢查是否缺少特定欄位 |
| 空值分析 (step2) | `null_analysis` | 分析欄位空值分佈狀況 |
| 重複值檢測 (step3) | `duplicates_analysis` | 檢查資料是否有重複值，支援 `products` 和 `products_extend` 表 |
| 擴充屬性檢測 (step4) | `check_extend_class` | 檢查擴充屬性是否符合規範 |
| 子品類標籤驗證 (step5) | `classification_check` | 驗證產品分類組合是否符合規範，支援 `mixed`, `further_subcategory`, `subcategory` 模式 |
| 名次驗證 (step6) | `rank_verifier` | 驗證名次欄位的值域是否符合規範 |
| 小數點位數驗證 (step7) | `verify_decimal` | 檢查數值欄位的小數點位數和格式是否符合規範 |

### 報表專屬驗證函數

| 報表種類 | 主函數名稱 | 使用的基礎驗證函數 |
|---------|-----------|-------------------|
| products | `check_products` | `column_assertion`, `null_analysis`, `duplicates_analysis`, `classification_check` |
| products_extend | `check_products_extend` | `column_assertion`, `null_analysis`, `duplicates_analysis`, `classification_check`, `check_extend_class` |
| chart_brands | `check_chart_brands` | `column_assertion`, `null_analysis`, `classification_check` (mixed), `rank_verifier` |
| chart_brand (單數) | `check_chart_brand` | `column_assertion`, `null_analysis`, `classification_check` (mixed), `rank_verifier` |
| chart_brands_extend | `check_chart_brands_extend` | `column_assertion`, `null_analysis`, `classification_check` (mixed), `rank_verifier`, `check_extend_class`, `verify_decimal` |
| chart_brands_extend_cross | `check_chart_brands_extend_cross` | `column_assertion`, `null_analysis`, `classification_check` (mixed), `rank_verifier`, `check_extend_class`, `verify_decimal` |
| chart_brands_extend_image | `check_chart_brands_extend_image` | `column_assertion`, `null_analysis`, `classification_check` (mixed), `rank_verifier`, `check_extend_class`, `verify_decimal` |
| chart_brand_extend_image (單數) | `check_chart_brand_extend_image` | `column_assertion`, `null_analysis`, `classification_check` (mixed), `rank_verifier`, `check_extend_class`, `verify_decimal` |
| chart_brands_comment_counts | `check_chart_brands_comment_counts` | `column_assertion`, `null_analysis`, `classification_check` (mixed), `rank_verifier`, `check_extend_class`, `verify_decimal` |
| chart_brand_comment_counts (單數) | `check_chart_brand_comment_counts` | `column_assertion`, `null_analysis`, `classification_check` (mixed), `rank_verifier`, `check_extend_class`, `verify_decimal` |
| chart_brands_comment_score | `check_chart_brands_comment_score` | `column_assertion`, `null_analysis`, `classification_check` (mixed), `rank_verifier`, `check_extend_class` |
| chart_brand_comment_score (單數) | `check_chart_brand_comment_score` | `column_assertion`, `null_analysis`, `classification_check` (mixed), `check_extend_class` |
| chart_others | `check_chart_others` | `column_assertion`, `null_analysis`, `classification_check` (mixed), `rank_verifier`, `check_extend_class`, `verify_decimal` |
| chart_trends | `check_chart_trends` | `column_assertion`, `null_analysis`, `classification_check` (mixed), `rank_verifier` |
| reference | `check_reference` | `column_assertion`, `null_analysis`, `classification_check` (further_subcategory) |
| keyword | `check_keyword` | `column_assertion`, `null_analysis`, 自訂 search_volume 檢查, `classification_check` (further_subcategory, 分別檢查 is_brand=True/False) |

### 輔助函數

| 函數名稱 | 說明 |
|---------|------|
| `is_testing_environment` | 判斷是否在測試環境中運行 |
| `safe_st_call` | 安全地調用 Streamlit 函數，在測試環境中不會拋出異常 |
| `stream_write` | 帶有流式效果的文字輸出，在測試環境中不會使用延遲效果 |
| `match_chart_type_from_filename` | 根據檔名自動匹配報表類型（在 utils.py 中） |

### 各報表欄位規範

各報表的必要欄位定義在 `constants.py` 的 `Config` 字典中：

```python
Config = {
    "products": [...],
    "products_extend": [...],
    "chart_brands": [...],
    # ... 其他報表類型
}
```

### 擴充屬性規範

各報表的擴充屬性（extend_class）定義在 `constants.py` 的 `Extend_class_schema` 字典中：

```python
Extend_class_schema = {
    "products_extend": ["適用環境", "使用情境", "功能", ...],
    "chart_brands_extend": ["使用情境", "適用環境", "功能", ...],
    # ... 其他報表類型
}
```

### 排名欄位規範

各報表的排名欄位及其值域定義在 `constants.py` 的 `Rank_col_schema` 字典中：

```python
Rank_col_schema = {
    "chart_brands": {
        "brand": ("brand_rank", 10)  # 欄位名稱, 最大名次
    },
    "chart_brands_extend": {
        "brand": ("brand_rank", 5),
        "factor_stats": ("extend_detail_rank", 10),
        "factor_alphabet": ("extend_detail_rank_ordinal", 10)
    },
    # ... 其他報表類型
}
```

### 分類覆蓋率閾值

分類覆蓋率的最低要求定義在 `constants.py` 中：

```python
CATEGORY_COVERAGE_THRESHOLD = 0.7  # 70%
```

---

## 設定檔說明

### constants.py

此檔案包含所有驗證規則的設定：

1. **RULES**: 定義各個驗證步驟的說明文字
2. **charts**: 定義每個報表類型需要執行哪些驗證步驟
3. **Config**: 定義每個報表類型的必要欄位
4. **Extend_class_schema**: 定義每個報表類型的擴充屬性規範
5. **Rank_col_schema**: 定義每個報表類型的排名欄位規範
6. **CATEGORY_COVERAGE_THRESHOLD**: 定義分類覆蓋率的最低要求（預設 70%）

### 使用流程

1. 使用者上傳分類表和待驗證報表
2. 系統自動偵測報表類型（透過 `match_chart_type_from_filename`）
3. 根據報表類型執行對應的驗證函數
4. 顯示驗證結果和下載選項

### 測試環境支援

所有驗證函數都支援在測試環境中運行，透過以下機制：
- `is_testing_environment()`: 檢測是否在 pytest 環境
- `safe_st_call()`: 在測試環境中安全地調用 Streamlit 函數
- `stream_write()`: 在測試環境中輸出到 console 而非 Streamlit
