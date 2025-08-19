import streamlit as st 
st.set_page_config(layout="wide")


import pandas as pd
from verify import Verify
from constants import charts, classification_columns, RULES

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

CL, CR = st.columns(2)
with CL:
    classification = st.file_uploader("上傳你的分類表", type = ["csv", "xlsx"])
    chart_name = st.selectbox("選擇欲驗證的報表種類", charts.keys())
with CR:
    data =  st.file_uploader("上傳欲驗證的報表", type = ["csv", "xlsx"])
    submit = st.button("開始驗證")

help = "".join([RULES[x] for x in charts[chart_name]])
instruction = st.empty()
with instruction.container():
    st.code(help , wrap_lines = False)

if submit:
    instruction.empty()
    try:
        classification = pd.read_csv(classification)
    except:
        try:
            classification = pd.read_excel(classification)
        except:
            raise TypeError("input only 'csv' or 'xlsx' file!")
        
    with st.spinner("讀取報表資料..."):  
        try:
            data = pd.read_csv(data)
        except:
            try:
                data = pd.read_excel(data)
            except:
                raise TypeError("input only 'csv' or 'xlsx' file!")
    
    classification['classification_further_subcategory'] = classification.apply(lambda row: "_".join([row[col] for col in classification_columns]), axis = 1)
    classification['classification_subcategory'] = classification.apply(lambda row: "_".join([row[col] for col in classification_columns if col != "further_subcategory"]), axis = 1)
    verifier = Verify(classification)

    with st.container(border = True):
        if chart_name == "products":
            dup_ids = verifier.check_products(data)
            if dup_ids:
                st.download_button(
                    label = "下載 products 重複列 id",
                    data = "\n".join(dup_ids),
                    file_name = "products_duplicated_id.txt",
                    mime = "text/plain"
                )

        if chart_name == "products_extend":
            dup_ids = verifier.check_products_extend(data)
            if dup_ids:
                st.download_button(
                    label = "下載 products extend 重複列 id",
                    data = "\n".join(dup_ids),
                    file_name = "products_extend_duplicated_id.txt",
                    mime = "text/plain"
                )

        if chart_name == "chart_brand":
            verifier.check_chart_brand(data)

        if chart_name == "chart_brand_extend":
            verifier.check_chart_brand_extend(data)

        if chart_name == "chart_brand_extend_cross":
            verifier.check_chart_brand_extend_cross(data)

        if chart_name == "chart_brand_extend_image":
            verifier.check_chart_brand_extend_image(data)

        if chart_name == "chart_brand_comment_counts":
            verifier.check_chart_brand_comment_counts(data)

        if chart_name == "chart_brand_comment_score":
            verifier.check_chart_brand_comment_score(data)

        if chart_name == "chart_others":
            verifier.check_chart_others(data)

        if chart_name == "chart_trends":
            verifier.check_chart_trends(data)

        if chart_name == "reference":
            verifier.check_reference(data)

        if chart_name == "keyword":
            verifier.check_keyword(data)