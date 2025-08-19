RULES = {
    "step1": """
🔆 欄位檢測：依照輸入的報表種類與對應欄位規範，判斷是否缺少特定欄位。
    • 若沒有缺失欄位，則輸出以下：
        ✅ 沒有缺失重要欄位
    • 若有缺失欄位，則輸出所有缺失的欄位：
        ⚠️ missing column: [缺失的欄位名稱]
""",
    "step2": """
🔆 空值分析：印出各欄位的空值分佈狀況，以 dataframe 格式呈現。第一列為空值數量，第二列為空值比例。
""",
    "step3": """
🔆 重複值檢測：針對 products 和 products_extend 表格，計算重複值出現的次數，並且回傳重複列的 id（並非 source_product_id）。
    - products 表使用 'source_product_id' 作為判定是否重複的欄位。
    - products_extend 表使用 'source_product_id', 'extend_class', 'extend_detail' 作為判定是否重複的欄位。
    • 若沒有重複值，則輸出以下：
        ✅ 沒有重複的[產品|產品擴增屬性]資料
    • 若有，則輸出以下：
        🔔 [Products|Products Extend] 有重複值。
        (最後面提供下載重複列 id 的按鈕)
""",
    "step4": """
🔆 擴充屬性檢測：
    • 針對所選報表的擴充屬性規範，判斷資料中是否缺少特定擴充屬性的統計資料。以 dataframe 呈現。缺少的擴充屬性會有 ❌ 標記。
    • 分析各個 extend_class 下，extend_subclass 出現空值的比率。若為 products_extend 報表，額外檢查 extend_unit 出現空值的比率。以 dataframe 呈現。
""",
    "step5": """
🔆 子品類標籤驗證：驗證產品分類組合（category, subcategory, further_subcategory）是否符合產品分類規範。產品分類規範的範例：設研院產品資料表.xlsx
    • 輸出以下：
        🔔 共有[錯誤資料數]筆資料的分類組合不存在於分類資料表中，佔總資料的[比例]%
    正常來講，錯誤筆數應該要為 0
""",
    "step6": """
🔆 名次驗證：列印出名次（品牌名次、因素名次）欄位的值域 (unique value)。
    • 輸出以下：
        🔔 標籤數量排名
        -資料中的名次：[資料中名次的值域]
        -規範名次：[該報表的名次規範]
""",
    "step7": """
🔆 小數點位數驗證：對有 extend_stats 欄位的報表，檢驗以下兩點：
    - ratio: 是否最多至小數三位
        • 若有列數之 ratio 超過三位小數，輸出以下：
            🔔 extend_stats -> ratio: [X] 列超過 3 位小數
    - avg_price: 是否最多至小數兩位
        • 若有列數之 avg_price 超過兩位小數，輸出以下：
            🔔 extend_stats -> avg_price: [X] 列超過 2 位小數

    • 若報表沒有 extend_stats，則輸出以下：
        ✅ 沒有 extend_stats 欄位
"""
}


charts = {
    "products": ["step1", "step2", "step3", "step5"],
    "products_extend": ["step1", "step2", "step3", "step4", "step5"],
    "chart_brand": ["step1", "step2", "step5", "step6"],
    "chart_brand_extend": ["step1", "step2", "step4", "step5", "step6", "step7"],
    "chart_brand_extend_cross": ["step1", "step2", "step4", "step5", "step6", "step7"],
    "chart_brand_extend_image": ["step1", "step2", "step4", "step5", "step6", "step7"],
    "chart_brand_comment_counts":["step1", "step2", "step4", "step5", "step6", "step7"],
    "chart_brand_comment_score":["step1", "step2", "step4", "step5"],
    "chart_others": ["step1", "step2", "step4", "step5", "step6", "step7"],
    "chart_trends": ["step1", "step2", "step5", "step6"],
    "reference": ["step1", "step2", "step5"],
    "keyword": ["step1", "step2", "step5"]
}


classification_columns = ["category", "subcategory", "further_subcategory"]


"""
各表格 schema
"""
Config = {
    "products": 
        ["domain", 
         "category", 
         "subcategory", 
         "further_subcategory", 
         "brand", 
         "list_price", 
         "sale_price", 
         "sales_volume", 
         'best_sellers_rank', 
         'accessories', 
         'url', 
         'image_url_1', 
         'source'
    ],
    "products_extend": [
        'source_product_id', 
        'extend_class',
        'extend_subclass', 
        'extend_detail_raw', 
        'extend_detail', 
        'extend_unit', 
        'source',
        'domain', 
        'category', 
        'subcategory', 
        'further_subcategory'],
    "chart_brand": [
        "id",
        "category",
        "subcategory",
        "further_subcategory",
        "brand",
        "brand_rank",
        "amount",
        "product_sales",
        "sales_ratio",
        "sales_ranking",
        "ranking_ratio",
        "highest_price",
        "lowest_price",
        "average_price",
        "average_discounted_price",
        "amount_of_positive_comment",
        "amount_of_negative_comment",
        "score_of_positive_comment",
        "score_of_negative_comment",
        "stats_type",
        "source"
    ],
    "chart_brand_extend": [
        "id",
        "category",
        "subcategory",
        "further_subcategory",
        "brand",
        "brand_rank",
        "extend_class",
        "extend_subclass",
        "extend_detail",
        "extend_stats",
        "stats_type",
        "source",
        "extend_detail_rank",
        "extend_detail_rank_ordinal"
    ],
    "chart_brand_extend_cross": [
        "id",
        "category",
        "subcategory",
        "further_subcategory",
        "brand",
        "brand_rank",
        "extend_class",
        "extend_subclass",
        "extend_detail",
        "extend_stats",
        "stats_type",
        "source"
    ],
    "chart_brand_extend_image": [
        "id",
        "category",
        "subcategory",
        "further_subcategory",
        "brand",
        "brand_rank",
        "extend_class",
        "extend_subclass",
        "extend_detail",
        "stats_type",
        "source"
    ],
    "chart_brand_comment_counts": [
        "id",
        "category",
        "subcategory",
        "further_subcategory",
        "brand",
        "brand_rank",
        "extend_class",
        "extend_detail",
        "extend_detail_snippet",
        "extend_detail_snippet_source",
        "extend_stats",
        "stats_type",
        "source"
    ],
    "chart_brand_comment_score": [
        "id",
        "category",
        "subcategory",
        "further_subcategory",
        "brand",
        "extend_class",
        "extend_detail",
        "extend_stats",
        "stats_type",
        "source"
    ],
    "chart_others": [
        "id",
        "category",
        "subcategory",
        "further_subcategory",
        "extend_class",
        "extend_subclass",
        "extend_detail",
        "extend_detail_rank",
        "brand_rank_detail",
        "extend_stats",
        "stats_type",
        "source"
    ],
    "chart_trends": [
        "id",
        "category",
        "subcategory",
        "further_subcategory",
        "chart_name",
        "labels",
        "labels_rank",
        "element_name",
        "element_name_rank",
        "element_name_rank_ordinal",
        "features",
        "stats_type",
        "source"
    ],
    "reference": [
        "references_id",
        "domain",
        "category",
        "subcategory",
        "further_subcategory",
        "label",
        "type",
        "title",
        "url",
        "process",
        "is_domestic",
        "content",
        "source"
    ],
    "keyword": [
        "domain",
        "category",
        "subcategory",
        "further_subcategory",
        "keyword",
        "search_volume",
        "search_volume_max",
        "search_volume_min",
        "trends",
        "end_at",
        "is_brand",
        "predict_volume"
    ]
}

"""
各表格擴充屬性（若有）schema
"""
Extend_class_schema = {
    "products_extend": [
        "適用環境",
        "使用情境",
        "功能",
        "功能_相機規格",
        "訴求",
        "保固",
        "風格",
        "色彩",
        "材質",
        "材質_部件材質",
        "尺寸",
        "尺寸_部件尺寸",
        "尺寸_收納尺寸",
        "重量",
        "效能",
        "容量",
        "族群"
    ],
    "chart_brand_extend": [
        "使用情境",
        "適用環境",
        "功能",
        "效能",
        "色彩",
        "訴求",
        "材質",
        "尺寸",
        "風格",
        "重量",
        "容量",
        "族群"
    ],
    "chart_brand_extend_cross": [
        "使用情境 x 售價",
        "功能 x 售價",
        "效能 x 售價",
        "尺寸 x 售價",
        "重量 x 售價",
        "容量 x 售價",
        "風格 x 售價",
        "色彩 x 售價",
        "材質 x 售價",
        "尺寸二維分析",
        "尺寸 x 色彩",
        "尺寸 x 材質",
        "訴求 x 尺寸",
        "訴求 x 重量",
        "訴求 x 容量",
        "訴求 x 功能",
        "訴求 x 效能",
        "訴求 x 材質",
        "使用情境 x 風格",
        "使用情境 x 尺寸",
        "使用情境 x 重量",
        "使用情境 x 容量",
        "功能 x 風格",
        "功能 x 尺寸",
        "功能 x 重量",
        "功能 x 容量",
        "色彩 x 材質"
    ],
    "chart_brand_extend_image": [
        "使用情境 x 風格",
        "風格",
        "使用情境"
    ],
    "chart_brand_comment_counts": [
        "正面留言因素",
        "負面留言因素"
    ],
    "chart_brand_comment_score": [
        "正面留言因素",
        "負面留言因素"
    ],
    "chart_others": [
        "配件",
        "產品族群分析"
    ],
    "chart_trends": [

    ]
}

classification_columns = ["category", "subcategory", "further_subcategory"]

"""
各表格排名欄位與規範
"""
Rank_col_schema = {
    "chart_brand": {
        "brand": ("brand_rank", 10)
    },
    "chart_brand_extend": {
        "brand": ("brand_rank", 5),
        "factor_stats": ("extend_detail_rank", 10),
        "factor_alphabet": ("extend_detail_rank_ordinal", 10)
    },
    "chart_brand_extend_cross": {
        "brand": ("brand_rank", 5)
    },
    "chart_brand_extend_image": {
        "brand": ("brand_rank", 5)
    },
    "chart_brand_comment_counts": {
        "brand": ("brand_rank", 5)
    },
    "chart_brand_comment_score": {
        "brand": ("brand_rank", 5)
    },
    "chart_others": {
        "factor_stats": ("extend_detail_rank", 10)
    },
    "chart_trends": {
        "element_stats": ("element_name_rank", 5),
        "element_alphabet": ("element_name_rank_ordinal", 5),
        "labels_rank": ("labels_rank", 10)
    }
}

