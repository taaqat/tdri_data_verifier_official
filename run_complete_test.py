#!/usr/bin/env python
"""
完整測試腳本，直接保存結果到檔案
"""
import os
import sys
import pandas as pd
from datetime import datetime

# 將專案根目錄添加到 Python 路徑
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from verify import Verify

def run_test_with_output():
    # 創建輸出檔案
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file_path = os.path.join(os.path.dirname(__file__), f'test_output_{timestamp}.txt')
    
    with open(log_file_path, 'w', encoding='utf-8') as log_file:
        try:
            log_file.write("開始執行測試...\n\n")
            
            # 測試資料檔案路徑
            test_data_dir = os.path.join(os.path.dirname(__file__), 'tests', 'test_data')
            
            # 讀取分類資料
            classification_file = os.path.join(test_data_dir, 'classification.xlsx')
            classification_data = pd.read_excel(classification_file)
            log_file.write(f"分類資料讀取成功，檔案路徑: {classification_file}\n")
            log_file.write(f"分類資料行數: {len(classification_data)}\n")
            log_file.write(f"分類資料欄位: {', '.join(classification_data.columns)}\n\n")
            
            # 創建驗證器實例
            verifier = Verify(classification_data)
            log_file.write("驗證器實例創建成功\n\n")
            
            # 測試檢查空值方法
            log_file.write("測試 check_empty_cells 方法...\n")
            empty_cells = verifier.check_empty_cells()
            log_file.write(f"空值結果: {empty_cells}\n\n")
            
            # 測試檢查重複產品方法
            log_file.write("測試 check_duplicated_products 方法...\n")
            duplicates = verifier.check_duplicated_products()
            log_file.write(f"重複產品結果: {duplicates}\n\n")
            
            # 測試類別覆蓋率
            log_file.write("測試 check_category_coverage_stats 方法...\n")
            coverage = verifier.check_category_coverage_stats()
            log_file.write(f"覆蓋率結果: {coverage}\n\n")
            
            # 測試驗證報告生成
            log_file.write("測試 generate_verification_report 方法...\n")
            report = verifier.generate_verification_report()
            log_file.write(f"報告內容:\n")
            for key, value in report.items():
                log_file.write(f"  {key}: {value}\n")
            log_file.write("\n")
            
            # 讀取問題資料
            problem_file = os.path.join(test_data_dir, 'problem_data.xlsx')
            problem_data = pd.read_excel(problem_file)
            log_file.write(f"問題資料讀取成功，檔案路徑: {problem_file}\n")
            log_file.write(f"問題資料行數: {len(problem_data)}\n")
            log_file.write(f"問題資料欄位: {', '.join(problem_data.columns)}\n\n")
            
            # 創建問題驗證器實例
            problem_verifier = Verify(problem_data)
            problem_verifier.file_name = os.path.basename(problem_file)
            log_file.write("問題資料驗證器實例創建成功\n\n")
            
            # 測試問題資料檢查空值方法
            log_file.write("測試問題資料 check_empty_cells 方法...\n")
            problem_empty_cells = problem_verifier.check_empty_cells()
            log_file.write(f"問題資料空值結果: {problem_empty_cells}\n\n")
            
            # 測試問題資料檢查重複產品方法
            log_file.write("測試問題資料 check_duplicated_products 方法...\n")
            problem_duplicates = problem_verifier.check_duplicated_products()
            log_file.write(f"問題資料重複產品結果: {problem_duplicates}\n\n")
            
            # 測試問題資料驗證報告生成
            log_file.write("測試問題資料 generate_verification_report 方法...\n")
            problem_report = problem_verifier.generate_verification_report()
            log_file.write(f"問題資料報告內容:\n")
            for key, value in problem_report.items():
                log_file.write(f"  {key}: {value}\n")
            log_file.write("\n")
            
            log_file.write("測試完成!\n")
            print(f"測試完成，結果已保存到: {log_file_path}")
            return True
            
        except Exception as e:
            import traceback
            log_file.write(f"測試過程發生錯誤:\n{str(e)}\n\n")
            log_file.write(traceback.format_exc())
            print(f"測試出錯，詳情請查看: {log_file_path}")
            return False

if __name__ == "__main__":
    run_test_with_output()
