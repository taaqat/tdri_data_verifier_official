"""
功能測試 - 測試完整的資料驗證流程，使用實際的 Excel 檔案
"""

import os
import sys
import unittest
import pandas as pd
import json

# 將專案根目錄添加到 Python 路徑
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from verify import Verify

# 測試資料檔案路徑
TEST_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../test_data'))

class TestCompleteVerificationFlow(unittest.TestCase):
    """測試完整的資料驗證流程"""
    
    def setUp(self):
        """設置測試環境"""
        # 讀取測試資料檔案
        self.complete_data_file = os.path.join(TEST_DATA_DIR, 'complete_data.xlsx')
        self.incomplete_data_file = os.path.join(TEST_DATA_DIR, 'incomplete_data.xlsx')
        self.classification_file = os.path.join(TEST_DATA_DIR, 'classification.xlsx')
        self.problem_data_file = os.path.join(TEST_DATA_DIR, 'problem_data.xlsx')
        
        # 讀取分類資料
        self.classification_data = pd.read_excel(self.classification_file)
        
        # 讀取完整資料
        self.complete_data = pd.read_excel(self.complete_data_file)
        
        # 創建驗證器實例
        self.verifier = Verify(self.classification_data)
    
    def test_complete_verification_flow(self):
        """測試完整的資料驗證流程，使用實際檔案"""
        # 讀取完整資料
        complete_data = pd.read_excel(self.complete_data_file)
        
        # 1. 執行資料檢查
        empty_cells = self.verifier.check_empty_cells()
        duplicates = self.verifier.check_duplicated_products()
        
        # 2. 執行類別覆蓋檢查
        coverage_result = self.verifier.check_category_coverage(complete_data)
        
        # 3. 執行品牌檢查
        brand_stats = self.verifier.check_brands()
        self.verifier.chart_brands_category()
        self.verifier.chart_brands_subcategory()
        
        # 4. 執行匯出報告功能
        report = self.verifier.generate_verification_report()
        
        # 檢查報告是否包含所有必要的部分
        self.assertIn('empty_cells', report)
        self.assertIn('duplicate_products', report)
        self.assertIn('category_coverage', report)
        self.assertIn('brands', report)
        
        # 驗證結果的正確性
        if empty_cells:
            # 應該沒有空值
            self.assertEqual(len(empty_cells), 0)
            
        if duplicates:
            # 應該沒有重複值
            self.assertEqual(len(duplicates), 0)
        
    def test_error_handling(self):
        """測試錯誤處理，使用實際的有問題資料檔案"""
        # 讀取問題數據
        problem_data = pd.read_excel(self.problem_data_file)
        
        # 創建驗證器實例
        problem_verifier = Verify(problem_data)
        problem_verifier.file_name = os.path.basename(self.problem_data_file)
        
        # 檢查空值檢測
        empty_cells = problem_verifier.check_empty_cells()
        self.assertGreater(len(empty_cells), 0, "應該檢測到空值")
        
        # 檢查重複檢測
        duplicates = problem_verifier.check_duplicated_products()
        self.assertGreater(len(duplicates), 0, "應該檢測到重複資料")
        
        # 確保報告生成不會因為問題資料而崩潰
        try:
            report = problem_verifier.generate_verification_report()
            self.assertIsNotNone(report, "報告不應為 None")
            
            # 檢查報告內容
            self.assertGreater(sum(report['empty_cells'].values()) if report['empty_cells'] else 0, 0, 
                             "報告應該包含空值信息")
            self.assertGreater(report['duplicate_products'].get('count', 0) if report['duplicate_products'] else 0, 0,
                             "報告應該包含重複產品信息")
        except Exception as e:
            self.fail(f"報告生成失敗，錯誤訊息：{str(e)}")


if __name__ == '__main__':
    unittest.main()
