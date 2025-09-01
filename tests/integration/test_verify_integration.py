"""
整合測試 - 驗證模組與配置檔案的互動
"""

import unittest
import pandas as pd
import os
import sys

# 將專案根目錄添加到 Python 路徑
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from verify import Verify
from constants import CATEGORY_COVERAGE_THRESHOLD

# 定義欄位名稱（根據實際情況調整）
PRODUCT_NAME_COLUMN = '產品名稱'
BRAND_COLUMN = '品牌'

class TestVerifyIntegration(unittest.TestCase):
    """測試驗證模組與配置的整合"""
    
    def setUp(self):
        """設置測試環境"""
        # 準備測試資料
        self.sample_data = pd.DataFrame({
            PRODUCT_NAME_COLUMN: ['產品A', '產品B', '產品C'],
            '大分類': ['類別1', '類別2', '類別3'],
            '中分類': ['子類1', '子類2', '子類3'],
            '小分類': ['細類1', '細類2', '細類3'],
            BRAND_COLUMN: ['品牌A', '品牌B', '品牌C']
        })
        
        # 創建驗證器實例 - Verify 只接受一個參數
        self.verifier = Verify(self.sample_data)
    
    def test_verify_uses_constants(self):
        """測試驗證器是否正確使用常數配置"""
        # 驗證品牌欄位可以正確被訪問
        result = self.verifier.classification[BRAND_COLUMN].tolist()
        self.assertEqual(result, ['品牌A', '品牌B', '品牌C'])
        
        # 驗證產品名稱欄位可以正確被訪問
        result = self.verifier.classification[PRODUCT_NAME_COLUMN].tolist()
        self.assertEqual(result, ['產品A', '產品B', '產品C'])
        
        # 驗證類別覆蓋閾值是否存在
        from constants import CATEGORY_COVERAGE_THRESHOLD
        self.assertIsInstance(CATEGORY_COVERAGE_THRESHOLD, float)
        self.assertTrue(0 <= CATEGORY_COVERAGE_THRESHOLD <= 1)
    
    def test_coverage_threshold_integration(self):
        """測試覆蓋率閾值與驗證邏輯的整合"""
        # 假設 CATEGORY_COVERAGE_THRESHOLD 是 0.7 (70%)
        
        # 測試數據包含完整分類，需要傳遞數據參數
        coverage_result = self.verifier.check_category_coverage_stats()
        
        # 確保結果中包含閾值信息
        self.assertIn('閾值', coverage_result)
        self.assertEqual(coverage_result['閾值'], CATEGORY_COVERAGE_THRESHOLD)
        
        # 確認覆蓋率計算和通過標準與閾值一致
        is_pass = all([
            coverage_result['大分類覆蓋率'] >= CATEGORY_COVERAGE_THRESHOLD,
            coverage_result['中分類覆蓋率'] >= CATEGORY_COVERAGE_THRESHOLD,
            coverage_result['小分類覆蓋率'] >= CATEGORY_COVERAGE_THRESHOLD
        ])
        
        self.assertEqual(coverage_result['通過'], is_pass)

if __name__ == '__main__':
    print("開始運行整合測試...")
    unittest.main(verbosity=2)
