"""
創建測試用的 Excel 檔案
"""
import os
import pandas as pd
import numpy as np

def create_test_files():
    # 確保測試數據目錄存在
    test_data_dir = os.path.join(os.path.dirname(__file__), 'test_data')
    os.makedirs(test_data_dir, exist_ok=True)
    
    # 創建完整數據的 Excel 檔案
    complete_data = pd.DataFrame({
        'id': [1, 2, 3, 4],
        'category': ['電子產品', '電子產品', '家具', '家具'],
        'subcategory': ['手機', '電腦', '桌子', '椅子'],
        'further_subcategory': ['智慧型手機', '筆記型電腦', '辦公桌', '辦公椅'],
        '產品名稱': ['iPhone', 'MacBook', '辦公桌A', '辦公椅B'],
        '品牌': ['Apple', 'Apple', '品牌A', '品牌B'],
        'stats_type': ['further_subcategory'] * 4
    })
    complete_file_path = os.path.join(test_data_dir, 'complete_data.xlsx')
    complete_data.to_excel(complete_file_path, index=False)
    print(f"已創建完整數據檔案: {complete_file_path}")
    
    # 創建有缺失數據的 Excel 檔案
    incomplete_data = pd.DataFrame({
        'id': [1, 2, 3],
        'category': ['電子產品', '電子產品', '家具'],
        'subcategory': ['手機', '電腦', '桌子'],
        'further_subcategory': ['智慧型手機', '筆記型電腦', '辦公桌'],
        '產品名稱': ['iPhone', 'MacBook', '辦公桌A'],
        '品牌': ['Apple', 'Apple', '品牌A'],
        'stats_type': ['further_subcategory'] * 3
    })
    incomplete_file_path = os.path.join(test_data_dir, 'incomplete_data.xlsx')
    incomplete_data.to_excel(incomplete_file_path, index=False)
    print(f"已創建不完整數據檔案: {incomplete_file_path}")
    
    # 創建分類表的 Excel 檔案
    classification_data = pd.DataFrame({
        'category': ['電子產品', '電子產品', '家具', '家具'],
        'subcategory': ['手機', '電腦', '桌子', '椅子'],
        'further_subcategory': ['智慧型手機', '筆記型電腦', '辦公桌', '辦公椅']
    })
    classification_data['classification_further_subcategory'] = classification_data.apply(
        lambda row: f"{row['category']}_{row['subcategory']}_{row['further_subcategory']}", 
        axis=1
    )
    classification_data['classification_subcategory'] = classification_data.apply(
        lambda row: f"{row['category']}_{row['subcategory']}", 
        axis=1
    )
    classification_file_path = os.path.join(test_data_dir, 'classification.xlsx')
    classification_data.to_excel(classification_file_path, index=False)
    print(f"已創建分類表檔案: {classification_file_path}")
    
    # 創建問題數據的 Excel 檔案
    problem_data = pd.DataFrame({
        'id': [1, 2, 3],
        '產品名稱': ['產品A', '產品A', None],  # 重複和空值
        'category': ['電子產品', '電子產品', '家具'],
        'subcategory': ['手機', '手機', None],  # 空值
        'further_subcategory': ['智慧型手機', '智慧型手機', '辦公桌'],
        '品牌': ['品牌A', '品牌A', '品牌C'],
        '資料來源': ['來源A', '來源A', '來源C']
    })
    problem_file_path = os.path.join(test_data_dir, 'problem_data.xlsx')
    problem_data.to_excel(problem_file_path, index=False)
    print(f"已創建問題數據檔案: {problem_file_path}")
    
    return {
        'complete': complete_file_path,
        'incomplete': incomplete_file_path,
        'classification': classification_file_path,
        'problem': problem_file_path
    }

if __name__ == "__main__":
    create_test_files()
