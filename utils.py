"""
工具函數模組
"""

import re
import difflib


def match_chart_type_from_filename(filename, chart_keys):
    """
    根據檔名自動匹配報表類型
    
    使用 token-based 匹配：將檔名和關鍵字都拆分成 token 進行比對，
    支援中間有其他詞的檔名（如 chart_brands_extend_amazon_image_1128.csv）
    支援單複數變化（如 keywords 匹配 keyword）
    
    Parameters
    ----------
    filename : str
        上傳的檔案名稱
    chart_keys : list
        可用的報表類型列表
    
    Returns
    -------
    tuple
        (matched_type, auto_detected)
        - matched_type: 匹配到的報表類型，如果無法匹配則返回第一個類型（預設值）
        - auto_detected: 是否成功自動判斷（True/False）
    
    Examples
    --------
    >>> chart_keys = ['products', 'chart_brands', 'chart_brands_extend_image', 'keyword']
    >>> match_chart_type_from_filename('chart_brands_extend_amazon_image_1128.csv', chart_keys)
    ('chart_brands_extend_image', True)
    
    >>> match_chart_type_from_filename('products_momo_1128.xlsx', chart_keys)
    ('products', True)
    
    >>> match_chart_type_from_filename('keywords_0829.xlsx', chart_keys)
    ('keyword', True)
    
    >>> match_chart_type_from_filename('unknown_file.csv', chart_keys)
    ('products', False)
    """
    filename = filename.lower()
    best_match = []
    
    def normalize_token(token):
        """標準化 token，處理單複數變化"""
        # 移除常見的複數形式 's'
        if token.endswith('s') and len(token) > 1:
            return token[:-1]
        return token
    
    # 將檔名拆分成 token（以底線和數字分隔）
    filename_tokens = set(re.split(r'[_\d.]+', filename))
    filename_tokens.discard('')  # 移除空字串
    
    # 標準化檔名 tokens（用於模糊匹配）
    normalized_filename_tokens = {normalize_token(t) for t in filename_tokens}
    
    # 找出所有可能的匹配
    contain_matches = []
    for key in chart_keys:
        # 將關鍵字也拆分成 token
        key_tokens = set(key.split('_'))
        
        # 方法 1: 精確匹配 - 如果關鍵字的所有 token 都在檔名中
        if key_tokens.issubset(filename_tokens):
            contain_matches.append(key)
        # 方法 2: 標準化匹配 - 處理單複數變化
        else:
            normalized_key_tokens = {normalize_token(t) for t in key_tokens}
            if normalized_key_tokens.issubset(normalized_filename_tokens):
                contain_matches.append(key)
    
    # 如果有匹配，選擇最長的（最具體的）
    if contain_matches:
        best_match = [max(contain_matches, key=len)]
    # 如果沒有匹配，再用 difflib 模糊比對
    elif not best_match:
        best_match = difflib.get_close_matches(filename, chart_keys, n=1, cutoff=0.6)
    
    if best_match:
        return best_match[0], True
    else:
        return chart_keys[0] if chart_keys else None, False
