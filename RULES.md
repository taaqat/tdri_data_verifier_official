# 報表驗證規則

## 共用

所有報表都會執行的檢查：

- **欄位檢測 (step1)**: 
  - 依照輸入的報表種類與對應欄位規範，判斷是否缺少特定欄位
  - 若沒有缺失欄位，輸出：✅ 沒有缺失重要欄位
  - 若有缺失欄位，輸出所有缺失的欄位：⚠️ missing column: [缺失的欄位名稱]

- **空值分析 (step2)**: 
  - 印出各欄位的空值分佈狀況，以 dataframe 格式呈現
  - 第一列為空值數量，第二列為空值比例

- **子品類標籤驗證 (step5)**:
  - 驗證產品分類組合（category, subcategory, further_subcategory）是否符合產品分類規範
  - 輸出：🔔 共有[錯誤資料數]筆資料的分類組合不存在於分類資料表中，佔總資料的[比例]%
  - 正常來講，錯誤筆數應該要為 0

## products

- **重複值檢測 (step3)**:
  - 使用 'source_product_id' 作為判定是否重複的欄位
  - 若沒有重複值，輸出：✅ 沒有重複的產品資料
  - 若有，輸出：🔔 Products 有重複值。(提供下載重複列 id 的按鈕)

## products_extend

- **重複值檢測 (step3)**:
  - 使用 'source_product_id', 'extend_class', 'extend_detail' 作為判定是否重複的欄位
  - 若沒有重複值，輸出：✅ 沒有重複的產品擴增屬性資料
  - 若有，輸出：🔔 Products Extend 有重複值。(提供下載重複列 id 的按鈕)

- **擴充屬性檢測 (step4)**:
  - 針對所選報表的擴充屬性規範，判斷資料中是否缺少特定擴充屬性的統計資料
  - 以 dataframe 呈現。缺少的擴充屬性會有 ❌ 標記
  - 分析各個 extend_class 下，extend_subclass 出現空值的比率
  - 額外檢查 extend_unit 出現空值的比率。以 dataframe 呈現

## chart_brands

- **名次驗證 (step6)**:
  - 列印出名次（品牌名次）欄位的值域 (unique value)
  - 輸出：
    - 🔔 品牌排名
    - - 資料中的名次：[資料中名次的值域]
    - - 規範名次：[該報表的名次規範]

## chart_brands_extend

- **擴充屬性檢測 (step4)**
- **名次驗證 (step6)**
- **小數點位數驗證 (step7)**:
  - 對有 extend_stats 欄位的報表，檢驗以下兩點：
    - ratio: 是否最多至小數三位
      - 若有列數之 ratio 超過三位小數，輸出：🔔 extend_stats -> ratio: [X] 列超過 3 位小數
    - avg_price: 是否最多至小數兩位
      - 若有列數之 avg_price 超過兩位小數，輸出：🔔 extend_stats -> avg_price: [X] 列超過 2 位小數
    - 若報表沒有 extend_stats，則輸出：✅ 沒有 extend_stats 欄位

## chart_brands_extend_cross

- **擴充屬性檢測 (step4)**
- **名次驗證 (step6)**
- **小數點位數驗證 (step7)**

## chart_brands_extend_image

- **擴充屬性檢測 (step4)**
- **名次驗證 (step6)**
- **小數點位數驗證 (step7)**

## chart_brands_comment_counts

- **擴充屬性檢測 (step4)**
- **名次驗證 (step6)**
- **小數點位數驗證 (step7)**

## chart_brands_comment_score

- **擴充屬性檢測 (step4)**

## chart_others

- **擴充屬性檢測 (step4)**
- **名次驗證 (step6)**
- **小數點位數驗證 (step7)**

## chart_trends

- **名次驗證 (step6)**

## reference

僅執行共用規則檢查（欄位檢測、空值分析、子品類標籤驗證）。

## keyword

僅執行共用規則檢查（欄位檢測、空值分析、子品類標籤驗證）。

## 附錄：規則與函數對照表

本附錄列出每條規則對應的函數名稱，方便開發者查找和修改規則的實現。

### 基礎驗證函數

| 規則 | 函數名稱 | 說明 |
|------|----------|------|
| 欄位檢測 (step1) | `column_assertion` | 檢查是否缺少特定欄位 |
| 空值分析 (step2) | `null_analysis` | 分析欄位空值分佈狀況 |
| 重複值檢測 (step3) | `duplicates_analysis` | 檢查資料是否有重複值 |
| 擴充屬性檢測 (step4) | `check_extend_class` | 檢查擴充屬性是否符合規範 |
| 子品類標籤驗證 (step5) | `classification_check` | 驗證產品分類組合是否符合規範 |
| 名次驗證 (step6) | `rank_verifier` | 驗證名次欄位的值域是否符合規範 |
| 小數點位數驗證 (step7) | `verify_decimal` | 檢查數值欄位的小數點位數是否符合規範 |

### 報表專屬驗證函數

| 報表種類 | 主函數名稱 | 使用的基礎驗證函數 |
|---------|-----------|-------------------|
| products | `check_products` | `column_assertion`, `null_analysis`, `duplicates_analysis`, `classification_check` |
| products_extend | `check_products_extend` | `column_assertion`, `null_analysis`, `duplicates_analysis`, `classification_check`, `check_extend_class` |
| chart_brands | `check_chart_brands` | `column_assertion`, `null_analysis`, `classification_check`, `rank_verifier` |
| chart_brands_extend | `check_chart_brands_extend` | `column_assertion`, `null_analysis`, `classification_check`, `rank_verifier`, `check_extend_class`, `verify_decimal` |
| chart_brands_extend_cross | `check_chart_brands_extend_cross` | `column_assertion`, `null_analysis`, `classification_check`, `rank_verifier`, `check_extend_class`, `verify_decimal` |
| chart_brands_extend_image | `check_chart_brands_extend_image` | `column_assertion`, `null_analysis`, `classification_check`, `rank_verifier`, `check_extend_class`, `verify_decimal` |
| chart_brands_comment_counts | `check_chart_brands_comment_counts` | `column_assertion`, `null_analysis`, `classification_check`, `rank_verifier`, `check_extend_class`, `verify_decimal` |
| chart_brands_comment_score | `check_chart_brands_comment_score` | `column_assertion`, `null_analysis`, `classification_check`, `rank_verifier`, `check_extend_class` |
| chart_others | `check_chart_others` | `column_assertion`, `null_analysis`, `classification_check`, `rank_verifier`, `check_extend_class`, `verify_decimal` |
| chart_trends | `check_chart_trends` | `column_assertion`, `null_analysis`, `classification_check`, `rank_verifier` |
| reference | `check_reference` | `column_assertion`, `null_analysis`, `classification_check` |
| keyword | `check_keyword` | `column_assertion`, `null_analysis`, `classification_check` |
