"""
測試 category_coverage 功能的單元測試
"""

import unittest
import sys
import os

# 將專案根目錄添加到 Python 路徑
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pandas as pd
from verify import Verify
from tests.conftest import (
    setup_streamlit_mock,
    create_test_classification,
    create_complete_data,
    create_incomplete_data
)

class TestCategoryCoverage(unittest.TestCase):
    
    def setUp(self):
        """
        設置測試環境
        """
        # 準備測試資料
        self.classification = create_test_classification()
        self.complete_data = create_complete_data()
        self.incomplete_data = create_incomplete_data()
        
        # 模擬 streamlit
        self.mock_st = setup_streamlit_mock()
        
        # 創建驗證器實例
        self.verifier = Verify(self.classification)
        
    def test_check_category_coverage_complete(self):
        """測試完整資料的分類覆蓋檢查"""
        # 調用待測試的函數
        missing_categories = self.verifier.check_category_coverage(self.complete_data)
        
        # 驗證結果
        self.assertEqual(len(missing_categories), 0, "完整資料不應有缺失的分類")
        self.assertEqual(self.mock_st.mock_container.dataframe_calls, 1, "應該調用 dataframe 展示結果")
        
        # 檢查 dataframe 內容
        df = self.mock_st.mock_container.dataframe_data
        # 如果是 Styler 對象，獲取內部的 DataFrame
        if hasattr(df, 'data'):
            df_data = df.data
        else:
            df_data = df
        
        self.assertEqual(len(df_data), 4, "結果應該有 4 列")
        self.assertTrue('count' in df_data.columns, "結果應該有 count 列")
        self.assertTrue((df_data['count'] > 0).all(), "所有分類的數量應該大於 0")
        
        # 下載按鈕不應該出現
        self.assertEqual(self.mock_st.mock_container.download_button_calls, 0, "不應該顯示下載按鈕")
    
    def test_check_category_coverage_incomplete(self):
        """測試缺失分類的資料"""
        # 調用待測試的函數
        missing_categories = self.verifier.check_category_coverage(self.incomplete_data)
        
        # 驗證結果
        self.assertEqual(len(missing_categories), 1, "應該有一個缺失的分類")
        self.assertEqual(missing_categories[0], "家具_椅子_辦公椅", "缺失的分類應該是辦公椅")
        
        # 檢查 dataframe 內容
        df = self.mock_st.mock_container.dataframe_data
        # 如果是 Styler 對象，獲取內部的 DataFrame
        if hasattr(df, 'data'):
            df_data = df.data
        else:
            df_data = df
            
        self.assertEqual(len(df_data), 4, "結果應該有 4 列")
        
        # 檢查缺失的分類是否為 0
        zero_count_rows = df_data[df_data['count'] == 0]
        self.assertEqual(len(zero_count_rows), 1, "應該有一個分類的數量為 0")
        
        # 檢查下載按鈕
        self.assertEqual(self.mock_st.mock_container.download_button_calls, 1, "應該顯示下載按鈕")
        
    def test_styling_highlight_zero(self):
        """測試高亮顯示 0 筆數的功能"""
        # 製作一個簡單的 DataFrame 來測試樣式
        df = pd.DataFrame({
            'category': ['cat1', 'cat2'],
            'count': [5, 0]
        })
        
        # 調用高亮函數
        styled_df = self.verifier._style_category_coverage(df)
        
        # 檢查是否返回 Styler 對象 (styled_df 已經是 Styler 對象，不是 DataFrame)
        self.assertIsNotNone(styled_df, "應該返回一個非空對象")
        # 檢查 Styler 對象是否有正確的屬性
        self.assertTrue(hasattr(styled_df, 'data'), "Styler 對象應該有 data 屬性")
    
    def test_check_category_coverage_missing_columns(self):
        """測試資料缺少必要的分類欄位時的處理"""
        # 創建一個沒有分類欄位的資料
        data_without_columns = pd.DataFrame({
            'id': [1, 2, 3],
            'product_name': ['產品A', '產品B', '產品C'],
            'price': [100, 200, 300]
        })
        
        # 調用待測試的函數
        missing_categories = self.verifier.check_category_coverage(data_without_columns)
        
        # 驗證結果：應該返回空列表（因為無法進行檢查）
        self.assertEqual(len(missing_categories), 0, "缺少欄位時應該返回空列表")
        
        # 驗證不應該調用 dataframe（因為沒有結果可以顯示）
        self.assertEqual(self.mock_st.mock_container.dataframe_calls, 0, "缺少欄位時不應該調用 dataframe")
        
        # 驗證不應該顯示下載按鈕
        self.assertEqual(self.mock_st.mock_container.download_button_calls, 0, "缺少欄位時不應該顯示下載按鈕")


if __name__ == '__main__':
    print("開始運行單元測試...")
    unittest.main(verbosity=2)
