import pandas as pd 
import numpy as np
import json
import argparse
from constants import RULES, Config, classification_columns, Rank_col_schema, Extend_class_schema
import streamlit as st
import time


def stream_write(text, time_interval = 0.04):

    def gen_stream(text):
        for word in text:
            yield word
            time.sleep(time_interval)

    st.write_stream(gen_stream(text))

class Verify():

    def __init__(self, classification_data):
        self.classification = classification_data
        self.chart_brand_details = {"subcategory": {},
                                    "further_subcategory": {}}
        self.chart_brand_extend_details = {}
        self.chart_brand_extend_cross_details = {}
        self.chart_brand_extend_image_details = {}
        self.chart_brand_comment_counts_details = {}
        self.chart_others_details = {}
        self.chart_trends_details = {}

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

        stream_write("\n🔆 正在檢查重複列...")
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
        stream_write("\n🔆 正在檢查分類組合...")
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

        stream_write(f"🔔 共有 {count} 比資料的分類組合不存在於分類資料表中，佔總資料的 {count / len(data) * 100 :.2f}%")
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

    def check_chart_brand(self, data):


        # 檢查重要欄位是否存在
        self.column_assertion(data, "chart_brand")
        
        # 重要欄位空值分析
        self.null_analysis(data, "chart_brand")
    
        # 檢查產品分類組合
        self.classification_check(data, "mixed")

        # 驗證排名
        self.rank_verifier(data, "chart_brand")

    def check_chart_brands_extend_image(self, data):
        # 檢查重要欄位是否存在
        self.column_assertion(data, "chart_brands_extend_image")
        # 重要欄位空值分析
        self.null_analysis(data, "chart_brands_extend_image")
        # 檢查產品分類組合
        self.chart_brands_extend_image_details["incorrect_classified_ids"] = self.classification_check(data, "mixed")
        # 驗證排名
        self.rank_verifier(data, "chart_brands_extend_image")
        # 檢查擴充屬性
        self.check_extend_class(data, "chart_brands_extend_image")
        # 檢查小數點
        self.verify_decimal(data)
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
        data["search_volume_zero"] = data['search_volume'].apply(
            lambda x: pd.isna(x) or str(x).strip() in ['0', '0.0', ''] or (
                isinstance(x, (int, float)) and x == 0
            )
        )
        stream_write(f"🔔 共有 {data['search_volume_zero'].sum()} 列之 search_volume 為 0 或空值！")


        # 檢查產品分類組合
        self.classification_check(is_brand_t, "further_subcategory")
        st.caption("針對 is_brand = 1 之 keyword 資料")

        
        self.classification_check(is_brand_f, "further_subcategory")
        st.caption("針對 is_brand = 0 之 keyword 資料")
        

        

    



        

        


