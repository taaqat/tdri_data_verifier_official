"""
測試檔名自動匹配報表類型的功能
"""

import unittest
import sys
import os

# 將專案根目錄添加到 Python 路徑
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from constants import charts
from utils import match_chart_type_from_filename

class TestFilenameMatching(unittest.TestCase):
    
    def setUp(self):
        """設置測試環境"""
        self.chart_keys = list(charts.keys())
    
    def test_products_matching(self):
        """測試 products 相關檔名匹配"""
        # 標準 products 檔名
        result, detected = match_chart_type_from_filename("products_amazon_0822.csv", self.chart_keys)
        self.assertEqual(result, "products")
        self.assertTrue(detected)
        
        result, detected = match_chart_type_from_filename("products_momo_1201.xlsx", self.chart_keys)
        self.assertEqual(result, "products")
        self.assertTrue(detected)
    
    def test_products_extend_matching(self):
        """測試 products_extend 相關檔名匹配"""
        result, detected = match_chart_type_from_filename("products_extend_amazon_0822.csv", self.chart_keys)
        self.assertEqual(result, "products_extend")
        self.assertTrue(detected)
        
        result, detected = match_chart_type_from_filename("products_extend_momo_1128.xlsx", self.chart_keys)
        self.assertEqual(result, "products_extend")
        self.assertTrue(detected)
    
    def test_chart_brands_matching(self):
        """測試 chart_brands 基本匹配"""
        result, detected = match_chart_type_from_filename("chart_brands_amazon_1128.csv", self.chart_keys)
        self.assertEqual(result, "chart_brands")
        self.assertTrue(detected)
        
        result, detected = match_chart_type_from_filename("chart_brands.xlsx", self.chart_keys)
        self.assertEqual(result, "chart_brands")
        self.assertTrue(detected)
    
    def test_chart_brands_extend_matching(self):
        """測試 chart_brands_extend 匹配（不含 image/cross 等後綴）"""
        result, detected = match_chart_type_from_filename("chart_brands_extend_amazon_1128.csv", self.chart_keys)
        self.assertEqual(result, "chart_brands_extend")
        self.assertTrue(detected)
        
        result, detected = match_chart_type_from_filename("chart_brands_extend.xlsx", self.chart_keys)
        self.assertEqual(result, "chart_brands_extend")
        self.assertTrue(detected)
    
    def test_chart_brands_extend_image_matching(self):
        """測試 chart_brands_extend_image 匹配（這是關鍵測試）"""
        # 這是問題案例：應該匹配 chart_brands_extend_image 而不是 chart_brands_extend
        result, detected = match_chart_type_from_filename("chart_brands_extend_amazon_image_1128.csv", self.chart_keys)
        self.assertEqual(result, "chart_brands_extend_image", 
                        "應該匹配最具體的類型 chart_brands_extend_image")
        self.assertTrue(detected)
        
        result, detected = match_chart_type_from_filename("chart_brands_extend_momo_image_1128.csv", self.chart_keys)
        self.assertEqual(result, "chart_brands_extend_image",
                        "應該匹配最具體的類型 chart_brands_extend_image")
        self.assertTrue(detected)
        
        # 標準檔名
        result, detected = match_chart_type_from_filename("chart_brands_extend_image.csv", self.chart_keys)
        self.assertEqual(result, "chart_brands_extend_image")
        self.assertTrue(detected)
    
    def test_chart_brands_extend_cross_matching(self):
        """測試 chart_brands_extend_cross 匹配"""
        result, detected = match_chart_type_from_filename("chart_brands_extend_cross_amazon_1128.csv", self.chart_keys)
        self.assertEqual(result, "chart_brands_extend_cross")
        self.assertTrue(detected)
        
        result, detected = match_chart_type_from_filename("chart_brands_extend_cross.xlsx", self.chart_keys)
        self.assertEqual(result, "chart_brands_extend_cross")
        self.assertTrue(detected)
    
    def test_chart_brands_comment_counts_matching(self):
        """測試 chart_brands_comment_counts 匹配"""
        result, detected = match_chart_type_from_filename("chart_brands_comment_counts_momo_1128.csv", self.chart_keys)
        self.assertEqual(result, "chart_brands_comment_counts")
        self.assertTrue(detected)
    
    def test_chart_brands_comment_score_matching(self):
        """測試 chart_brands_comment_score 匹配"""
        result, detected = match_chart_type_from_filename("chart_brands_comment_score_amazon_1128.csv", self.chart_keys)
        self.assertEqual(result, "chart_brands_comment_score")
        self.assertTrue(detected)
    
    def test_chart_others_matching(self):
        """測試 chart_others 匹配"""
        result, detected = match_chart_type_from_filename("chart_others_1128.csv", self.chart_keys)
        self.assertEqual(result, "chart_others")
        self.assertTrue(detected)
    
    def test_chart_trends_matching(self):
        """測試 chart_trends 匹配"""
        result, detected = match_chart_type_from_filename("chart_trends_amazon_1201.csv", self.chart_keys)
        self.assertEqual(result, "chart_trends")
        self.assertTrue(detected)
    
    def test_reference_matching(self):
        """測試 reference 匹配"""
        result, detected = match_chart_type_from_filename("reference_data_1128.csv", self.chart_keys)
        self.assertEqual(result, "reference")
        self.assertTrue(detected)
    
    def test_keyword_matching(self):
        """測試 keyword 匹配"""
        result, detected = match_chart_type_from_filename("keyword_analysis_1201.csv", self.chart_keys)
        self.assertEqual(result, "keyword")
        self.assertTrue(detected)

    def test_keyword_matching2(self):
        """測試 keyword 匹配"""
        result, detected = match_chart_type_from_filename("keywords_1201.csv", self.chart_keys)
        self.assertEqual(result, "keyword")
        self.assertTrue(detected)
    
    def test_unmatched_filename(self):
        """測試無法匹配的檔名（應該返回預設值且 auto_detected=False）"""
        result, detected = match_chart_type_from_filename("categories_1001.csv", self.chart_keys)
        self.assertEqual(result, self.chart_keys[0])  # 預設值（products）
        self.assertFalse(detected, "無法匹配的檔名應該標記為未自動偵測")
        
        result, detected = match_chart_type_from_filename("random_file_name.xlsx", self.chart_keys)
        self.assertEqual(result, self.chart_keys[0])
        self.assertFalse(detected)
    
    def test_longest_match_priority(self):
        """測試優先選擇最長（最具體）的匹配"""
        # 當檔名可能匹配多個類型時，應該選擇最具體的
        test_cases = [
            ("chart_brands_extend_image_complete.csv", "chart_brands_extend_image"),
            ("chart_brands_extend_cross_complete.csv", "chart_brands_extend_cross"),
            ("products_extend_complete.csv", "products_extend"),
        ]
        
        for filename, expected in test_cases:
            result, detected = match_chart_type_from_filename(filename, self.chart_keys)
            self.assertEqual(result, expected, 
                           f"檔名 '{filename}' 應該匹配最具體的類型 '{expected}'")
            self.assertTrue(detected)
    
    def test_case_insensitive(self):
        """測試大小寫不敏感"""
        result1, _ = match_chart_type_from_filename("PRODUCTS_AMAZON.CSV", self.chart_keys)
        result2, _ = match_chart_type_from_filename("products_amazon.csv", self.chart_keys)
        result3, _ = match_chart_type_from_filename("Products_Amazon.csv", self.chart_keys)
        
        self.assertEqual(result1, result2)
        self.assertEqual(result2, result3)
        self.assertEqual(result1, "products")
    
    def test_plural_form_matching(self):
        """測試單複數形式匹配（新增功能）"""
        # 測試 keywords (複數) 匹配到 keyword (單數)
        result, detected = match_chart_type_from_filename("keywords_0829.xlsx", self.chart_keys)
        self.assertEqual(result, "keyword", "keywords (複數) 應該匹配 keyword (單數)")
        self.assertTrue(detected)
        
        result, detected = match_chart_type_from_filename("keywords.csv", self.chart_keys)
        self.assertEqual(result, "keyword")
        self.assertTrue(detected)
        
        # 測試 references (複數) 匹配到 reference (單數)
        result, detected = match_chart_type_from_filename("references_1201.csv", self.chart_keys)
        self.assertEqual(result, "reference", "references (複數) 應該匹配 reference (單數)")
        self.assertTrue(detected)
        
        result, detected = match_chart_type_from_filename("references.xlsx", self.chart_keys)
        self.assertEqual(result, "reference")
        self.assertTrue(detected)
        
        # 測試單數形式仍然正常工作
        result, detected = match_chart_type_from_filename("keyword_0829.xlsx", self.chart_keys)
        self.assertEqual(result, "keyword")
        self.assertTrue(detected)
        
        result, detected = match_chart_type_from_filename("reference.csv", self.chart_keys)
        self.assertEqual(result, "reference")
        self.assertTrue(detected)
    
    def test_plural_with_complex_filename(self):
        """測試複數形式與複雜檔名組合"""
        # keywords + 日期 + 來源
        result, detected = match_chart_type_from_filename("keywords_amazon_0829.xlsx", self.chart_keys)
        self.assertEqual(result, "keyword")
        self.assertTrue(detected)
        
        # references + 日期 + 來源
        result, detected = match_chart_type_from_filename("references_momo_1201.csv", self.chart_keys)
        self.assertEqual(result, "reference")
        self.assertTrue(detected)
        
        # 混合大小寫的複數形式
        result, detected = match_chart_type_from_filename("Keywords_Amazon_0829.XLSX", self.chart_keys)
        self.assertEqual(result, "keyword")
        self.assertTrue(detected)


if __name__ == '__main__':
    print("開始運行檔名匹配測試...")
    unittest.main(verbosity=2)
