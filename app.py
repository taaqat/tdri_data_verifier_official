
import streamlit as st 
st.set_page_config(layout="wide")


import pandas as pd
from verify import Verify
from constants import charts, classification_columns, RULES
from utils import match_chart_type_from_filename

st.title("設研院資料驗證平台")
st.markdown("""<style>
div[data-baseweb="select"]:hover {
    border-color: #baad8d;
}
div.stButton > button {
    width: 100%;  /* 設置按鈕寬度為頁面寬度的 50% */
    height: 50px;
    margin-left: 0;
    margin-right: auto;
}
div.stButton > button:hover {
    transform: scale(1.02);
    transition: transform 0.05s;
}
</style>
""", unsafe_allow_html=True)


# 新增：根據檔名自動選擇報表種類

CL, CR = st.columns(2)

# chart_name 預設值自動判斷
chart_keys = list(charts.keys())
auto_detected = False

# 初始化 session state
if 'last_uploaded_file' not in st.session_state:
    st.session_state.last_uploaded_file = None
if 'chart_name' not in st.session_state:
    st.session_state.chart_name = chart_keys[0]

with CR:
    data = st.file_uploader("上傳欲驗證的報表", type = ["csv", "xlsx"], key="data_file")
    if data is not None:
        # 檢查是否是新上傳的檔案
        file_changed = (st.session_state.last_uploaded_file != data.name)
        
        # 使用工具函數進行檔名匹配
        matched_type, auto_detected = match_chart_type_from_filename(data.name, chart_keys)
        
        # 如果是新檔案且成功自動判斷，更新 session state
        if file_changed and auto_detected:
            st.session_state.chart_name = matched_type
        
        # 更新記錄的檔案名稱
        st.session_state.last_uploaded_file = data.name
    submit = st.button("開始驗證")
with CL:
    classification = st.file_uploader("上傳你的分類表", type = ["csv", "xlsx"])
    # selectbox 使用 session_state 的值，不設定 index 參數
    chart_name = st.selectbox("選擇欲驗證的報表種類", chart_keys, key="chart_name")
    
    # 只在無法自動判斷時顯示警告
    if data is not None and not auto_detected:
        st.warning(f"⚠️ 無法自動判斷報表類型，請手動選擇正確的類型")

help = "".join([RULES[x] for x in charts[chart_name]])
instruction = st.empty()
with instruction.container():
    st.code(help , wrap_lines = False)

if submit:
    instruction.empty()
    
    # 檢查是否上傳了分類表
    if classification is None:
        st.error("❌ 請上傳分類表！")
        st.stop()
    
    # 檢查是否上傳了報表資料
    if data is None:
        st.error("❌ 請上傳欲驗證的報表！")
        st.stop()
    
    # 讀取分類表
    try:
        classification = pd.read_csv(classification)
    except:
        try:
            classification = pd.read_excel(classification)
        except:
            st.error("❌ 分類表格式錯誤，請上傳 csv 或 xlsx 檔案！")
            st.stop()
        
    # 讀取報表資料
    with st.spinner("讀取報表資料..."):  
        try:
            data = pd.read_csv(data)
        except:
            try:
                data = pd.read_excel(data)
            except:
                st.error("❌ 報表格式錯誤，請上傳 csv 或 xlsx 檔案！")
                st.stop()
    
    classification['classification_further_subcategory'] = classification.apply(lambda row: "_".join([row[col] for col in classification_columns]), axis = 1)
    classification['classification_subcategory'] = classification.apply(lambda row: "_".join([row[col] for col in classification_columns if col != "further_subcategory"]), axis = 1)
    verifier = Verify(classification)

    with st.container(border = True):
        # 先檢查分類覆蓋率
        verifier.check_category_coverage(data)
        if chart_name == "products":
            dup_ids = verifier.check_products(data)
            if dup_ids:
                st.download_button(
                    label = "下載 products 重複列 id",
                    data = "\n".join(map(str, dup_ids)),
                    file_name = "products_duplicated_id.txt",
                    mime = "text/plain"
                )

        if chart_name == "products_extend":
            dup_ids = verifier.check_products_extend(data)
            if dup_ids:
                st.download_button(
                    label = "下載 products extend 重複列 id",
                    data = "\n".join(map(str, dup_ids)),
                    file_name = "products_extend_duplicated_id.txt",
                    mime = "text/plain"
                )

        if chart_name == "chart_brands":
            verifier.check_chart_brands(data)

        if chart_name == "chart_brands_extend":
            verifier.check_chart_brands_extend(data)

        if chart_name == "chart_brands_extend_cross":
            verifier.check_chart_brands_extend_cross(data)

        if chart_name == "chart_brands_extend_image":
            verifier.check_chart_brands_extend_image(data)

        if chart_name == "chart_brands_comment_counts":
            verifier.check_chart_brands_comment_counts(data)

        #if chart_name == "chart_brands_comment_score":
        #    verifier.check_chart_brands_comment_score(data)

        if chart_name == "chart_others":
            verifier.check_chart_others(data)

        if chart_name == "chart_trends":
            verifier.check_chart_trends(data)

        if chart_name == "reference":
            verifier.check_reference(data)

        if chart_name == "keyword":
            verifier.check_keyword(data)