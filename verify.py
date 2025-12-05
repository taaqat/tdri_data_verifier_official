import pandas as pd
import numpy as np
import json
import argparse
import streamlit as st
import time
import os
import sys
from constants import RULES, Config, classification_columns, Rank_col_schema, Extend_class_schema, CATEGORY_COVERAGE_THRESHOLD


def is_testing_environment():
    """判斷是否在測試環境中運行"""
    return 'PYTEST_CURRENT_TEST' in os.environ or any('test' in arg.lower() for arg in sys.argv)

def safe_st_call(func, *args, **kwargs):
    """安全地調用 Streamlit 函數，在測試環境中不會拋出異常"""
    if is_testing_environment():
        return None
    try:
        return func(*args, **kwargs)
    except Exception:
        # 在非 Streamlit 環境中運行時忽略錯誤
        return None

def stream_write(text, time_interval = 0.04):
    """帶有流式效果的文字輸出，在測試環境中不會使用延遲效果"""
    is_test = is_testing_environment()
    
    def gen_stream(text):
        for word in text:
            yield word
            # 在測試時不要延遲
            if not is_test:
                time.sleep(time_interval)
    
    try:
        # 在測試環境中，只輸出到控制台
        if is_test:
            print(text)
        else:
            st.write_stream(gen_stream(text))
    except Exception:
        # 在 streamlit 上下文外，回退到標準輸出
        print(text)

class Verify():
    def __init__(self, classification_data, file_name=None):
        self.classification = classification_data
        self.file_name = file_name  # 新增檔案名稱參數，允許為 None
        self.chart_brand_details = {"subcategory": {},
                                    "further_subcategory": {}}
        self.chart_brand_extend_details = {}
        self.chart_brand_extend_cross_details = {}
        self.chart_brand_extend_image_details = {}
        self.chart_brand_comment_counts_details = {}
        self.chart_others_details = {}
        self.chart_trends_details = {}
        self.category_coverage_details = {}
        self.empty_cells_details = {}
        self.duplicated_products_details = {}
        
    def check_chart_brands_extend(self, data):
        # 檢查重要欄位是否存在
        self.column_assertion(data, "chart_brands_extend")
        # 重要欄位空值分析
        self.null_analysis(data, "chart_brands_extend")
        # 檢查產品分類組合
        self.classification_check(data, "mixed")
        # 驗證排名
        self.rank_verifier(data, "chart_brands_extend")
        # 檢查擴充屬性
        self.check_extend_class(data, "chart_brands_extend")
        # 檢查小數點
        self.verify_decimal(data)

    def column_assertion(self, data, chart_name):
        stream_write("🔆 檢查是否缺少特定欄位...")
        if_any = False
        for col in Config[chart_name]:
            if col not in data.columns:
                if_any = True
                stream_write(f"⚠️ missing column: {col}")

        if not if_any:
            stream_write("✅ 沒有缺失重要欄位")

    def null_analysis(self, data, chart_name):
        st.divider()
        stream_write(f"\n📊 總列數：{len(data)}")
        table = (pd.DataFrame(data[Config[chart_name]].isna().sum())
         .rename(columns = {0: "count"}))
        table['proportion'] = table['count'] / len(data)
        table = table.astype("object")
        table['count'] = table['count'].apply(lambda x: f"{int(x)}")
        table['proportion'] = table['proportion'].apply(lambda x: f"{x * 100:.2f} %")

        stream_write("🔆 各欄位空值分佈")
        st.dataframe(table.T)

    def duplicates_analysis(self, data, chart_name):
        st.divider()
        assert chart_name in ["products", "products_extend"], "duplicates analysis is only available for 'products' and 'products_extend' tables"

        stream_write("\n🔆 檢查重複列...")
        if chart_name == "products":
            data["dup"] = data.duplicated(subset = ["source_product_id"])
            dup_ids = data[data["dup"]]["id"].tolist()
            if dup_ids != []:
                stream_write("🔔 Products 有重複值。")
                return dup_ids
            else:
                stream_write("✅ 沒有重複的產品資料")
        
        if chart_name == "products_extend":
            data["dup"] = data.duplicated(subset = ["source_product_id", "extend_class", "extend_subclass", "extend_detail"])
            dup_ids = data[data["dup"]]["id"].tolist()
            if dup_ids != []:
                stream_write("🔔 Products Extend 有重複值。")
                return dup_ids
            else:
                stream_write("✅ 沒有重複的產品擴增屬性資料")
        
        

            


    def classification_check(self, data, statstype = "further_subcategory"):
        st.divider()
        stream_write("\n🔆 檢查分類組合...")
        assert statstype in ["subcategory", "further_subcategory", "mixed"] 
        incorrect_classified_ids = []

        if statstype == "mixed":
            """
            當表中同時有子類與品類層級的資料 -> 分開處理
            """
            # * 子類
            class_cols = ["category", "subcategory", "further_subcategory"]
            further_sub_data = data[data['stats_type'] == "further_subcategory"]
            for _, row in further_sub_data.dropna(subset = class_cols).iterrows():
                class_ = "_".join([row[col] for col in class_cols]) 
                if class_ not in self.classification['classification_further_subcategory'].tolist():
                    incorrect_classified_ids.append(row['id'])

            # * 品類
            class_cols = ["category", "subcategory"]
            sub_data = data[data['stats_type'] == "subcategory"]
            for _, row in sub_data.dropna(subset = class_cols).iterrows():
                class_ = "_".join([row[col] for col in class_cols]) 
                if class_ not in self.classification['classification_subcategory'].tolist():
                    incorrect_classified_ids.append(row['id'])

            count = len(incorrect_classified_ids)

        else:
            """
            當表中只有子類或品類其一層級的資料
            """
            if statstype == "further_subcategory":
                class_cols = classification_columns
            elif statstype == "subcategory":
                class_cols = ["category", "subcategory"]
            count = 0
            for _, row in data.dropna(subset = class_cols).iterrows():
                class_ = "_".join([row[col] for col in class_cols]) 
                if class_ not in self.classification['classification_' + statstype].tolist():
                    count += 1
                    try:
                        incorrect_classified_ids.append(row['id'])
                    except:
                        try:
                            # * 新增 reference 報表的例外處理
                            incorrect_classified_ids.append(row['reference_id'])
                        except:
                            pass

        stream_write(f"🔔 共有 {count} 筆資料的分類組合不存在於分類資料表中，佔總資料的 {count / len(data) * 100 :.2f}%")
        return incorrect_classified_ids
    
    def rank_verifier(self, data, chart_name):
        st.divider()
        schema = Rank_col_schema[chart_name]

        

        if "brand" in schema.keys():
            stream_write("\n🔆 驗證品牌排名欄位...")
            col_name = schema["brand"][0]
            range_   = schema["brand"][1]
            formatted_values = data[col_name].apply(
                lambda x: str(int(x)) if pd.notna(x) and isinstance(x, (int, float)) and x == int(x) 
                else str(x)
            ).unique().tolist()
            stream_write(f"🔔 品牌排名")
            stream_write(f"- 資料中的名次：{sorted(formatted_values)}", 0.002)
            stream_write(f"- 規範名次： {set([i + 1 for i in range(range_)] + [999])}", 0.002)

        if "factor_stats" in schema.keys():
            stream_write("\n🔆 驗證因素統計排名欄位...")
            col_name  = schema["factor_stats"][0]
            range_    = schema["factor_stats"][1]
            formatted_values = data[col_name].apply(
                lambda x: str(int(x)) if pd.notna(x) and isinstance(x, (int, float)) and x == int(x) 
                else str(x)
            ).unique().tolist()
            stream_write(f"🔔 因素統計排名")
            stream_write(f"- 資料中的名次：{sorted(formatted_values)}", 0.002)
            stream_write(f"- 規範名次： {set([i + 1 for i in range(range_)] + [999])}", 0.002)

        if "factor_alphabet" in schema.keys():
            stream_write("\n🔆 驗證因素名稱排名欄位...")
            col_name  = schema["factor_alphabet"][0]
            range_    = schema["factor_alphabet"][1]
            formatted_values = data[col_name].apply(
                lambda x: str(int(x)) if pd.notna(x) and isinstance(x, (int, float)) and x == int(x) 
                else str(x)
            ).unique().tolist()
            stream_write(f"🔔 因素名稱排名")
            stream_write(f"- 資料中的名次：{sorted(formatted_values)}", 0.002)
            stream_write(f"- 規範名次： {set([i + 1 for i in range(range_)] + [999])}", 0.002)

        if "element_stats" in schema.keys():
            stream_write("\n🔆 (chart_trends) 驗證因素數量排名欄位...")
            col_name  = schema["element_stats"][0]
            range_    = schema["element_stats"][1]
            formatted_values = data[col_name].apply(
                lambda x: str(int(x)) if pd.notna(x) and isinstance(x, (int, float)) and x == int(x) 
                else str(x)
            ).unique().tolist()
            stream_write(f"🔔 因素數量排名")
            stream_write(f"- 資料中的名次：{sorted(formatted_values)}", 0.002)
            stream_write(f"- 規範名次： {set([i + 1 for i in range(range_)] + [999])}", 0.002)
        
        if "element_alphabet" in schema.keys():
            stream_write("\n🔆 (chart_trends) 驗證因素名稱排名欄位...")
            col_name  = schema["element_alphabet"][0]
            range_    = schema["element_alphabet"][1]
            formatted_values = data[col_name].apply(
                lambda x: str(int(x)) if pd.notna(x) and isinstance(x, (int, float)) and x == int(x) 
                else str(x)
            ).unique().tolist()
            stream_write(f"🔔 因素名稱排名")
            stream_write(f"- 資料中的名次：{sorted(formatted_values)}", 0.002)
            stream_write(f"- 規範名次： {set([i + 1 for i in range(range_)] + [999])}", 0.002)

        if "labels_rank" in schema.keys():
            stream_write("\n🔆 (chart_trends) 驗證標籤數量排名欄位...")
            col_name  = schema["labels_rank"][0]
            range_    = schema["labels_rank"][1]
            formatted_values = data[col_name].apply(
                lambda x: str(int(x)) if pd.notna(x) and isinstance(x, (int, float)) and x == int(x) 
                else str(x)
            ).unique().tolist()
            stream_write(f"🔔 標籤數量排名")
            stream_write(f"- 資料中的名次：{sorted(formatted_values)}", 0.002)
            stream_write(f"- 規範名次： {set([i + 1 for i in range(range_)] + [999])}", 0.002)

    def check_extend_class(self, data, chart_name):
        st.divider()
        stream_write("\n🔆 檢查是否缺少擴充屬性...")
        extend_classes_status = pd.DataFrame(columns = Extend_class_schema[chart_name])
        for col in extend_classes_status.columns:
            if col not in data['extend_class'].unique():
                extend_classes_status.loc["是否出現在資料表中", col] = "❌"
            else:
                extend_classes_status.loc["是否出現在資料表中", col] = "✅"
        st.dataframe(extend_classes_status)


        
        if chart_name == "chart_brand_comment_counts":
            return 
        stream_write("\n🔆 子擴充屬性空值分析")
        subclass_decomp = (data
            .groupby(["extend_class"])
            .apply(lambda group: 
                    pd.DataFrame(
                            {
                                "extend_subclass為空之列數": pd.Series(group["extend_subclass"].isna().sum()),
                                "extend_subclass為空比例":  pd.Series(group["extend_subclass"].isna().sum() / len(group)),
                                "extend_unit為空之列數": pd.Series(group["extend_unit"].isna().sum()),
                                "extend_unit為空比例":  pd.Series(group["extend_unit"].isna().sum() / len(group))
                            }   
                                if chart_name == "products_extend" else
                            {
                                "extend_subclass為空之列數": pd.Series(group["extend_subclass"].isna().sum()),
                                "extend_subclass為空比例":  pd.Series(group["extend_subclass"].isna().sum() / len(group))
                            }
                         )
                    , include_groups =  False))
        subclass_decomp["extend_subclass為空比例"] = subclass_decomp["extend_subclass為空比例"].apply(lambda x: f"{x * 100:.2f}%")
        if chart_name == "products_extend":
            subclass_decomp["extend_unit為空比例"] = subclass_decomp["extend_unit為空比例"].apply(lambda x: f"{x * 100:.2f}%")

        st.dataframe(subclass_decomp)
        st.caption("""計算方式：
                   
1. groupby("extend_class")，計算 extend_subclass (extend_unit) 的空值數

2. 將上步驟算出的數量，除以每個 group (extend_class) 的列數，計算比例""")

    def verify_decimal(self, data):
        st.divider()
        stream_write("\n🔆 檢查小數點規範...")

        df = data.copy()

        if "extend_stats" in df.columns:
            
            # 讀取 json 字串
            df['extend_stats'] = df['extend_stats'].apply(json.loads)

            # json 標準化
            df = pd.concat([ 
                    df,
                    pd.json_normalize(df["extend_stats"])
                ], axis = 1
            )


            # * Check ratio
            if "ratio" in df.columns:
                df["ratio"] = df["ratio"].astype(str)
                df["ratio_decimal_test"] = df["ratio"].apply(lambda x: len(x.split(".")[1]) > 3 if len(x.split(".")) > 1 else False)
                df["ratio_ends_with_zero"] = df["ratio"].apply(lambda x: int(x.split(".")[1]) == 0 if len(x.split(".")) > 1 else False)
                sum_violating_1 = sum(df['ratio_decimal_test'])
                sum_violating_2 = sum(df['ratio_ends_with_zero'])
                if sum_violating_1 > 0:
                    stream_write(f"🔔 extend_stats -> ratio: {sum_violating_1} 列超過 3 位小數" )
                if sum_violating_2 > 0:
                    stream_write(f"🔔 extend_stats -> ratio: {sum_violating_2} 列小數以 0 結尾" )

            # * Check avg_price
            if "avg_price" in df.columns:
                df["avg_price"] = df["avg_price"].astype(str)
                df["avg_price_decimal_test"] = df["avg_price"].apply(lambda x: len(x.split(".")[1]) > 3 if len(x.split(".")) > 1 else False)
                df["avg_price_ends_with_zero"] = df["avg_price"].apply(lambda x: int(x.split(".")[1]) == 0 if len(x.split(".")) > 1 else False)
                sum_violating_1 = sum(df['avg_price_decimal_test'])
                sum_violating_2 = sum(df['avg_price_ends_with_zero'])
                if sum_violating_1 > 0:
                    stream_write(f"🔔 extend_stats -> avg_price: {sum_violating_1} 列超過 3 位小數" )
                if sum_violating_2 > 0:
                    stream_write(f"🔔 extend_stats -> avg_price: {sum_violating_2} 列小數以 0 結尾" )

            del df
            stream_write("✅ 檢查完成")
        else:
            stream_write("✅ 沒有 extend_stats 欄位")

    # ==========================================================================================================================
    # * * * 以下為各表的資料驗證函數。會用到上面的輔助函數 * * * 
    # ==========================================================================================================================

    def check_products(self, data):

        # 檢查重要欄位是否存在
        self.column_assertion(data, "products")
        
        # 重要欄位空值分析
        self.null_analysis(data, "products")

        # 重複值檢測
        dup_ids = self.duplicates_analysis(data, "products")
    
        # 檢查產品分類組合
        incorrect_classified_ids = self.classification_check(data)

        return dup_ids
        

    def check_products_extend(self, data):


        # 檢查重要欄位是否存在
        self.column_assertion(data, "products_extend")
        
        # 重要欄位空值分析
        self.null_analysis(data, "products_extend")

        # 重複值檢測
        dup_ids = self.duplicates_analysis(data, "products_extend")
    
        # 檢查產品分類組合
        self.classification_check(data)

        # 檢查擴充屬性
        self.check_extend_class(data, "products_extend")

        return dup_ids

    def check_chart_brands(self, data):
        # 檢查重要欄位是否存在
        self.column_assertion(data, "chart_brands")
        
        # 重要欄位空值分析
        self.null_analysis(data, "chart_brands")
    
        # 檢查產品分類組合
        self.classification_check(data, "mixed")

        # 驗證排名
        self.rank_verifier(data, "chart_brands")
        
    def check_chart_brand(self, data):
        # 檢查重要欄位是否存在
        self.column_assertion(data, "chart_brand")
        
        # 重要欄位空值分析
        self.null_analysis(data, "chart_brand")
    
        # 檢查產品分類組合
        self.classification_check(data, "mixed")

        # 驗證排名
        self.rank_verifier(data, "chart_brand")

    def check_chart_brands_extend_cross(self, data):
        # 檢查重要欄位是否存在
        self.column_assertion(data, "chart_brands_extend_cross")
        # 重要欄位空值分析
        self.null_analysis(data, "chart_brands_extend_cross")
        # 檢查產品分類組合
        self.classification_check(data, "mixed")
        # 驗證排名
        self.rank_verifier(data, "chart_brands_extend_cross")
        # 檢查擴充屬性
        self.check_extend_class(data, "chart_brands_extend_cross")
        # 檢查小數點
        self.verify_decimal(data)
        # 檢查擴充屬性
        self.check_extend_class(data, "chart_brands_extend")
        # 檢查小數點
        self.verify_decimal(data)
        self.verify_decimal(data)

    def check_chart_brands_extend_image(self, data):
        # 檢查重要欄位是否存在
        self.column_assertion(data, "chart_brands_extend_image")
        
        # 重要欄位空值分析
        self.null_analysis(data, "chart_brands_extend_image")
    
        # 檢查產品分類組合
        self.chart_brand_extend_image_details["incorrect_classified_ids"] = self.classification_check(data, "mixed")

        # 驗證排名
        self.rank_verifier(data, "chart_brands_extend_image")
        
        # 檢查擴充屬性
        self.check_extend_class(data, "chart_brands_extend_image")
        
        # 檢查小數點
        self.verify_decimal(data)
        
    def check_chart_brand_extend_image(self, data):

        # 檢查重要欄位是否存在
        self.column_assertion(data, "chart_brand_extend_image")
        
        # 重要欄位空值分析
        self.null_analysis(data, "chart_brand_extend_image")
    
        # 檢查產品分類組合
        self.chart_brand_extend_image_details["incorrect_classified_ids"] = self.classification_check(data, "mixed")

        # 驗證排名
        self.rank_verifier(data, "chart_brand_extend_image")
        
        # 檢查擴充屬性
        self.check_extend_class(data, "chart_brand_extend_image")

        # 檢查小數點
        self.verify_decimal(data)

    def check_chart_brands_comment_counts(self, data):
        # 檢查重要欄位是否存在
        self.column_assertion(data, "chart_brands_comment_counts")
        
        # 重要欄位空值分析
        self.null_analysis(data, "chart_brands_comment_counts")
    
        # 檢查產品分類組合
        self.classification_check(data, "mixed")

        # 驗證排名
        self.rank_verifier(data, "chart_brands_comment_counts")
        
    def check_chart_brand_comment_counts(self, data):

        # 檢查重要欄位是否存在
        self.column_assertion(data, "chart_brand_comment_counts")
        
        # 重要欄位空值分析
        self.null_analysis(data, "chart_brand_comment_counts")
    
        # 檢查產品分類組合
        self.classification_check(data, "mixed")

        # 驗證排名
        self.rank_verifier(data, "chart_brand_comment_counts")
        
        # 檢查擴充屬性
        self.check_extend_class(data, "chart_brand_comment_counts")

        # 檢查小數點
        self.verify_decimal(data)

    def check_chart_brands_comment_score(self, data):
        # 檢查重要欄位是否存在
        self.column_assertion(data, "chart_brands_comment_score")
        
        # 重要欄位空值分析
        self.null_analysis(data, "chart_brands_comment_score")
    
        # 檢查產品分類組合
        self.classification_check(data, "mixed")
        
        # 驗證排名
        self.rank_verifier(data, "chart_brands_comment_score")
        
        # 檢查擴充屬性
        stream_write("\n🔆 檢查是否缺少擴充屬性...")
        
    def check_chart_brand_comment_score(self, data):

        # 檢查重要欄位是否存在
        self.column_assertion(data, "chart_brand_comment_score")
        
        # 重要欄位空值分析
        self.null_analysis(data, "chart_brand_comment_score")
    
        # 檢查產品分類組合
        self.classification_check(data, "mixed")
        
        # 檢查擴充屬性
        stream_write("\n🔆 檢查是否缺少擴充屬性...")
        extend_classes_status = pd.DataFrame(columns = Extend_class_schema["chart_brand_comment_score"])
        for col in extend_classes_status.columns:
            if col not in data['extend_class'].unique():
                extend_classes_status.loc["是否出現在資料表中", col] = "❌"
            else:
                extend_classes_status.loc["是否出現在資料表中", col] = "✅"
        st.dataframe(extend_classes_status)
    
    def check_chart_others(self, data):

        # 檢查重要欄位是否存在
        self.column_assertion(data, "chart_others")
        
        # 重要欄位空值分析
        self.null_analysis(data, "chart_others")
    
        # 檢查產品分類組合
        self.classification_check(data, "mixed")

        # 驗證排名
        self.rank_verifier(data, "chart_others")
        
        # 檢查擴充屬性
        self.check_extend_class(data, "chart_others")

        # 檢查小數點
        self.verify_decimal(data)

    def check_chart_trends(self, data):

        # 檢查重要欄位是否存在
        self.column_assertion(data, "chart_trends")
        
        # 重要欄位空值分析
        self.null_analysis(data, "chart_trends")


        # 檢查產品分類組合
        self.classification_check(data, "mixed")

        # 驗證排名
        self.rank_verifier(data, "chart_trends")

    def check_reference(self, data):
        # 檢查重要欄位是否存在
        self.column_assertion(data, "reference")
        
        # 重要欄位空值分析
        self.null_analysis(data, "reference")

        # 檢查產品分類組合
        self.classification_check(data, "further_subcategory")

    def check_keyword(self, data):
        # 檢查重要欄位是否存在
        self.column_assertion(data, "keyword")
        
        # 重要欄位空值分析
        self.null_analysis(data, "keyword")

        for col in ["domain", "subcategory", "further_subcategory", "category"]:
            data[col] = data[col].astype(str)

        is_brand_t = data[data['is_brand'] == True]
        is_brand_f = data[data['is_brand'] == False]
        
        # 檢查是否有列的 search_volume 為 0
        stream_write("\n🔆 檢查 keyword 表中的 search_volume 欄位...")
        try:
            data["search_volume_zero"] = data['search_volume'].apply(
                lambda x: pd.isna(x) or str(x).strip() in ['0', '0.0', ''] or (
                    isinstance(x, (int, float)) and x == 0
                )
            )
            zero_count = int(data['search_volume_zero'].sum())
            if zero_count == 0:
                stream_write(f"✅ 沒有 search_volume 為 0 或空值的資料")
            else:
                stream_write(f"🔔 共有 {zero_count} 列之 search_volume 為 0 或空值！")
        except Exception as e:
            stream_write(f"⚠️ 檢查 search_volume 時發生錯誤: {str(e)}")

        # 檢查產品分類組合
        # stream_write("\n🔆 檢查 is_brand = True 的資料分類...")
        self.classification_check(is_brand_t, "further_subcategory")
        safe_st_call(st.caption, "針對 is_brand = 1 之 keyword 資料")

        # stream_write("\n🔆 檢查 is_brand = False 的資料分類...")
        self.classification_check(is_brand_f, "further_subcategory")
        safe_st_call(st.caption, "針對 is_brand = 0 之 keyword 資料")
        
    def check_category_coverage(self, data, level="further_subcategory"):
        """
        檢查上傳的表格是否包含所有分類
        
        Parameters:
        -----------
        data : pandas DataFrame
            要檢查的資料
        level : str
            檢查的分類層級，可以是 "subcategory" 或 "further_subcategory"
            
        Returns:
        --------
        list
            缺失的分類列表
        """
        safe_st_call(st.divider)
        stream_write("\n🔆 檢查分類覆蓋率...")
        
        # 確定檢查的分類層級
        if level == "further_subcategory":
            categories = self.classification['classification_further_subcategory'].tolist()
            class_cols = classification_columns
        else:
            categories = self.classification['classification_subcategory'].tolist()
            class_cols = ["category", "subcategory"]
        
        # 檢查必要的欄位是否存在
        missing_cols = [col for col in class_cols if col not in data.columns]
        if missing_cols:
            stream_write(f"⚠️ 資料缺少必要的分類欄位: {missing_cols}")
            stream_write("無法進行分類覆蓋率檢查")
            return []
        
        # 計算每個分類的數量
        result = []
        for category in categories:
            if level == "further_subcategory":
                # 拆分分類字串以便比對
                cat_parts = category.split('_')
                if len(cat_parts) != 3:
                    continue
                    
                # 篩選出符合該分類的資料
                mask = ((data['category'] == cat_parts[0]) & 
                       (data['subcategory'] == cat_parts[1]) & 
                       (data['further_subcategory'] == cat_parts[2]))
            else:
                cat_parts = category.split('_')
                if len(cat_parts) != 2:
                    continue
                    
                mask = ((data['category'] == cat_parts[0]) & 
                       (data['subcategory'] == cat_parts[1]))
            
            count = mask.sum()
            result.append({
                'category': category,
                'count': count
            })
        
        # 轉換為 DataFrame
        df_result = pd.DataFrame(result)
        
        # 找出缺失的分類 (count == 0)
        missing_categories = df_result[df_result['count'] == 0]['category'].tolist()
        
        # 儲存結果
        self.category_coverage_details['result'] = df_result
        self.category_coverage_details['missing'] = missing_categories
        
        # 顯示結果
        styled_df = self._style_category_coverage(df_result)
        stream_write(f"🔔 分類覆蓋率檢查結果（共 {len(categories)} 個分類，缺失 {len(missing_categories)} 個）：")
        st.dataframe(styled_df)
        
        # 如果有缺失的分類，提供下載按鈕
        if missing_categories:
            st.download_button(
                label = "下載缺失分類清單",
                data = "\n".join(missing_categories),
                file_name = "missing_categories.txt",
                mime = "text/plain"
            )
            
        return missing_categories
        
    def _style_category_coverage(self, df):
        """
        為分類覆蓋率結果添加樣式
        
        Parameters:
        -----------
        df : pandas DataFrame
            要添加樣式的資料
            
        Returns:
        --------
        pandas DataFrame
            帶有樣式的資料
        """
        # 使用 pandas styler API 來設置樣式
        def highlight_zero(val):
            return 'background-color: #FFCCCC' if val == 0 else ''
        
        # 將樣式應用到 'count' 列
        styled_df = df.style.map(highlight_zero, subset=['count'])
        
        return styled_df
    
    def check_category_coverage_stats(self):
        """
        檢查類別覆蓋率統計
        
        Returns:
        --------
        dict
            包含各分類層級覆蓋率和是否通過閾值檢查的結果
        """
        # 獲取當前資料的唯一分類值
        current_counts = {
            '大分類': len(self.classification['category'].unique()) if 'category' in self.classification.columns else 0,
            '中分類': len(self.classification['subcategory'].unique()) if 'subcategory' in self.classification.columns else 0,
            '小分類': len(self.classification['further_subcategory'].unique()) if 'further_subcategory' in self.classification.columns else 0
        }
        
        # 獲取總類別數量
        total_counts = self.get_total_category_counts()
        
        # 計算覆蓋率
        coverage = {
            '大分類覆蓋率': current_counts['大分類'] / total_counts['大分類'] if total_counts['大分類'] > 0 else 0,
            '中分類覆蓋率': current_counts['中分類'] / total_counts['中分類'] if total_counts['中分類'] > 0 else 0,
            '小分類覆蓋率': current_counts['小分類'] / total_counts['小分類'] if total_counts['小分類'] > 0 else 0
        }
        
        # 判斷是否通過
        passed = all(rate >= CATEGORY_COVERAGE_THRESHOLD for rate in coverage.values())
        
        # 返回結果
        return {
            **coverage,
            '閾值': CATEGORY_COVERAGE_THRESHOLD,
            '通過': passed
        }
    
    def get_total_category_counts(self):
        """
        獲取標準分類表中各層級的總類別數量
        
        Returns:
        --------
        dict
            各分類層級的總數量
        """
        if hasattr(self, 'classification') and isinstance(self.classification, pd.DataFrame):
            # 使用相同的欄位名稱來獲取計數
            return {
                '大分類': len(self.classification['category'].unique()) if 'category' in self.classification.columns else 0,
                '中分類': len(self.classification['subcategory'].unique()) if 'subcategory' in self.classification.columns else 0,
                '小分類': len(self.classification['further_subcategory'].unique()) if 'further_subcategory' in self.classification.columns else 0
            }
        else:
            # 如果沒有標準分類表，返回預設值
            return {'大分類': 1, '中分類': 1, '小分類': 1}

    def check_empty_cells(self):
        """
        檢查資料中的空值儲存格
        
        Returns:
        --------
        dict
            包含各欄位空值數量的字典
        """
        empty_cells = {}
        
        if hasattr(self, 'classification') and isinstance(self.classification, pd.DataFrame):
            # 計算每個欄位的空值數量
            for col in self.classification.columns:
                null_count = self.classification[col].isna().sum()
                if null_count > 0:
                    empty_cells[col] = null_count
                    
            # 保存詳細資訊
            self.empty_cells_details = empty_cells
            
            # 在 streamlit 環境中顯示結果（如果是在應用中運行）
            try:
                if empty_cells:
                    st.write("🔆 資料中存在空值儲存格：")
                    st.dataframe(pd.DataFrame(list(empty_cells.items()), columns=['欄位', '空值數量']))
                else:
                    st.write("✅ 資料中沒有空值儲存格")
            except (AttributeError, NameError):
                # 如果在測試環境，忽略 streamlit 顯示
                pass
                
        return empty_cells
    
    def check_duplicated_products(self):
        """
        檢查重複的產品資料
        
        Returns:
        --------
        list
            重複產品的索引列表
        """
        duplicates = []
        
        if hasattr(self, 'classification') and isinstance(self.classification, pd.DataFrame):
            # 根據產品名稱檢查重複
            if '產品名稱' in self.classification.columns:
                dup_mask = self.classification.duplicated(subset=['產品名稱'], keep=False)
                duplicates = self.classification[dup_mask].index.tolist()
                
                # 保存詳細資訊
                self.duplicated_products_details = {
                    'count': len(duplicates),
                    'indices': duplicates
                }
                
                # 在 streamlit 環境中顯示結果（如果是在應用中運行）
                try:
                    if duplicates:
                        st.write(f"🔔 發現 {len(duplicates)} 筆重複的產品資料")
                        st.dataframe(self.classification[dup_mask])
                    else:
                        st.write("✅ 沒有重複的產品資料")
                except (AttributeError, NameError):
                    # 如果在測試環境，忽略 streamlit 顯示
                    pass
                    
        return duplicates
    
    def check_brands(self):
        """
        檢查品牌資料
        
        Returns:
        --------
        dict
            品牌統計資訊
        """
        brand_stats = {}
        
        if hasattr(self, 'classification') and isinstance(self.classification, pd.DataFrame):
            # 檢查品牌欄位是否存在
            if '品牌' in self.classification.columns:
                # 統計每個品牌的數量
                brand_counts = self.classification['品牌'].value_counts()
                
                # 轉換為字典
                brand_stats = brand_counts.to_dict()
                
                # 在 streamlit 環境中顯示結果（如果是在應用中運行）
                try:
                    st.write("🔆 品牌統計資訊：")
                    st.dataframe(pd.DataFrame(list(brand_stats.items()), columns=['品牌', '數量']))
                except (AttributeError, NameError):
                    # 如果在測試環境，忽略 streamlit 顯示
                    pass
                
        return brand_stats
    
    def chart_brands_category(self):
        """
        生成品牌與大分類的交叉統計圖表
        """
        if hasattr(self, 'classification') and isinstance(self.classification, pd.DataFrame):
            # 檢查必要欄位是否存在
            if '品牌' in self.classification.columns and 'category' in self.classification.columns:
                # 生成交叉表
                cross_tab = pd.crosstab(
                    self.classification['品牌'], 
                    self.classification['category']
                )
                
                # 在 streamlit 環境中顯示結果（如果是在應用中運行）
                try:
                    st.write("🔆 品牌與大分類交叉統計：")
                    st.dataframe(cross_tab)
                except (AttributeError, NameError):
                    # 如果在測試環境，忽略 streamlit 顯示
                    pass
                
                # 保存詳細資訊
                self.chart_brand_details["category"] = cross_tab.to_dict()
                
    def chart_brands_subcategory(self):
        """
        生成品牌與中分類的交叉統計圖表
        """
        if hasattr(self, 'classification') and isinstance(self.classification, pd.DataFrame):
            # 檢查必要欄位是否存在
            if '品牌' in self.classification.columns and 'subcategory' in self.classification.columns:
                # 生成交叉表
                cross_tab = pd.crosstab(
                    self.classification['品牌'], 
                    self.classification['subcategory']
                )
                
                # 在 streamlit 環境中顯示結果（如果是在應用中運行）
                try:
                    st.write("🔆 品牌與中分類交叉統計：")
                    st.dataframe(cross_tab)
                except (AttributeError, NameError):
                    # 如果在測試環境，忽略 streamlit 顯示
                    pass
                
                # 保存詳細資訊
                self.chart_brand_details["subcategory"] = cross_tab.to_dict()
    
    def generate_verification_report(self):
        """
        生成驗證報告
        
        Returns:
        --------
        dict
            包含所有驗證結果的報告
        """
        # 處理 numpy 類型的問題，轉為 Python 原生類型
        def convert_numpy_to_native(obj):
            if hasattr(obj, 'items'):
                return {k: convert_numpy_to_native(v) for k, v in obj.items()}
            elif hasattr(obj, '__iter__') and not isinstance(obj, str):
                return [convert_numpy_to_native(v) for v in obj]
            elif hasattr(obj, 'item'):
                return obj.item()  # 將 numpy 類型轉為 Python 原生類型
            else:
                return obj
            
        # 轉換 empty_cells_details
        if self.empty_cells_details:
            self.empty_cells_details = convert_numpy_to_native(self.empty_cells_details)
            
        report = {
            'empty_cells': self.empty_cells_details,
            'duplicate_products': self.duplicated_products_details,
            'category_coverage': self.category_coverage_details,
            'brands': self.chart_brand_details
        }
        
        # 添加檔案名稱（如果有）
        if self.file_name:
            report['file_name'] = self.file_name
        
        # 計算問題總數
        empty_cell_count = sum(self.empty_cells_details.values()) if self.empty_cells_details else 0
        duplicate_count = self.duplicated_products_details.get('count', 0) if self.duplicated_products_details else 0
        
        summary = pd.DataFrame({
            '項目': ['空值儲存格數量', '重複產品數量'],
            '數量': [empty_cell_count, duplicate_count]
        })
        
        # 在 streamlit 環境中顯示報告摘要（如果是在應用中運行）
        try:
            st.write("📋 驗證報告摘要：")
            st.dataframe(summary)
            
            # 提供下載報告的按鈕
            if self.file_name:
                # 轉換報告中的所有 numpy 類型為 Python 原生類型
                json_safe_report = convert_numpy_to_native(report)
                
                st.download_button(
                    label="下載驗證報告",
                    data=json.dumps(json_safe_report, ensure_ascii=False, indent=2),
                    file_name=f"{self.file_name.split('.')[0]}_verification_report.json",
                    mime="application/json"
                )
        except (AttributeError, NameError):
            # 如果在測試環境，忽略 streamlit 顯示
            pass
            
        return report


