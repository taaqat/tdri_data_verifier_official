"""
測試配置文件，提供共用的測試工具和設置
"""

import pandas as pd
import numpy as np
import sys
from unittest import mock

# 模擬 streamlit 功能的類別
class MockStreamlit:
    """模擬 streamlit 功能的類別"""
    def __init__(self):
        self.container_calls = 0
        self.divider_calls = 0
        self.dataframe_calls = 0
        self.dataframe_data = None
        self.download_button_calls = 0
        self.download_button_data = None

    def divider(self):
        self.divider_calls += 1
        
    def dataframe(self, data):
        self.dataframe_calls += 1
        self.dataframe_data = data
        
    def download_button(self, label, data, file_name, mime):
        self.download_button_calls += 1
        self.download_button_data = data

# 模擬 streamlit 模組
class MockSt:
    def __init__(self):
        self.mock_container = MockStreamlit()
        
    def divider(self):
        self.mock_container.divider()
        
    def dataframe(self, data):
        self.mock_container.dataframe(data)
        
    def download_button(self, label, data, file_name, mime):
        self.mock_container.download_button(label, data, file_name, mime)
        
    def container(self, border=False):
        self.mock_container.container_calls += 1
        return self

    def write_stream(self, generator):
        # 消耗生成器但不做任何事
        for _ in generator:
            pass

def setup_streamlit_mock():
    """
    設置 streamlit 模擬並返回模擬對象
    """
    mock_st = MockSt()
    
    # 替換全局 st
    import verify
    sys.modules['streamlit'] = mock_st
    verify.st = mock_st
    
    return mock_st

def create_test_classification():
    """
    創建用於測試的分類表資料
    """
    classification = pd.DataFrame({
        'category': ['電子產品', '電子產品', '家具', '家具'],
        'subcategory': ['手機', '電腦', '桌子', '椅子'],
        'further_subcategory': ['智慧型手機', '筆記型電腦', '辦公桌', '辦公椅']
    })
    classification['classification_further_subcategory'] = classification.apply(
        lambda row: f"{row['category']}_{row['subcategory']}_{row['further_subcategory']}", 
        axis=1
    )
    classification['classification_subcategory'] = classification.apply(
        lambda row: f"{row['category']}_{row['subcategory']}", 
        axis=1
    )
    return classification

def create_complete_data():
    """
    創建包含所有分類的測試資料
    """
    return pd.DataFrame({
        'id': [1, 2, 3, 4],
        'category': ['電子產品', '電子產品', '家具', '家具'],
        'subcategory': ['手機', '電腦', '桌子', '椅子'],
        'further_subcategory': ['智慧型手機', '筆記型電腦', '辦公桌', '辦公椅'],
        'stats_type': ['further_subcategory'] * 4
    })

def create_incomplete_data():
    """
    創建缺少某些分類的測試資料
    """
    return pd.DataFrame({
        'id': [1, 2, 3],
        'category': ['電子產品', '電子產品', '家具'],
        'subcategory': ['手機', '電腦', '桌子'],
        'further_subcategory': ['智慧型手機', '筆記型電腦', '辦公桌'],
        'stats_type': ['further_subcategory'] * 3
    })
