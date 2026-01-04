# -*- coding: utf-8 -*-
"""
AI 小說生成器 - 配置文件
"""

# 專案版本
VERSION = '0.1.0'
VERSION_NAME = 'MVP - 初始發布'
RELEASE_DATE = '2026-01-04'

# API 配置
API_CONFIG = {
    'base_url': 'https://api.siliconflow.cn/v1/chat/completions',
    'default_model': 'Qwen/Qwen2.5-7B-Instruct',
    'timeout': 120,  # 請求超時時間（秒）
    'max_retries': 3,  # 最大重試次數
}

# 可用模型列表與價格（每 1K tokens，人民幣）
MODELS = {
    'Qwen/Qwen2.5-7B-Instruct': {
        'name': 'Qwen2.5-7B',
        'price_input': 0.0007,
        'price_output': 0.0007,
        'description': '輕量快速，適合測試'
    },
    'Qwen/Qwen2.5-14B-Instruct': {
        'name': 'Qwen2.5-14B',
        'price_input': 0.0014,
        'price_output': 0.0014,
        'description': '平衡性能，適合正式創作'
    },
    'Qwen/Qwen2.5-32B-Instruct': {
        'name': 'Qwen2.5-32B',
        'price_input': 0.0035,
        'price_output': 0.0035,
        'description': '專業級別，高品質輸出'
    },
    'Qwen/Qwen2.5-72B-Instruct': {
        'name': 'Qwen2.5-72B',
        'price_input': 0.0070,
        'price_output': 0.0070,
        'description': '旗艦模型，出版級品質'
    },
}

# 生成參數
GENERATION_CONFIG = {
    'temperature': 0.8,      # 創造性（0-1，越高越隨機）
    'max_tokens': 5000,      # 每次請求最大 token 數
    'target_words': 3000,    # 目標章節字數
    'min_words': 2500,       # 最小章節字數
    'max_words': 3500,       # 最大章節字數
}

# 專案配置
PROJECT_CONFIG = {
    'project_prefix': 'novel',
    'encoding': 'utf-8',
    'chapter_filename_format': 'chapter_{:03d}.txt',  # chapter_001.txt
}

# 日誌配置
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
}
