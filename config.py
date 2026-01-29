# -*- coding: utf-8 -*-
"""
AI 小說生成器 - 配置文件
配置：零成本全明星戰隊 (DeepSeek R1 + GLM-4 + Qwen Coder)
"""

# 專案版本
VERSION = '0.3.1'
VERSION_NAME = 'Optimized Stage Params Edition'

# API 配置
API_CONFIG = {
    'base_url': 'https://api.siliconflow.cn/v1/chat/completions',
    'default_model': 'deepseek-ai/DeepSeek-R1-Distill-Qwen-7B',
    'timeout': 180,
    'max_retries': 3,
}

# 🤖 模型角色分配（緊急修復：切換為 GLM-4）
MODEL_ROLES = {
    'architect': 'THUDM/glm-4-9b-chat',           # 總編劇：中文能力極強（修復中英混雜問題）
    'writer': 'THUDM/glm-4-9b-chat',              # 作家：文筆最好
    'editor': 'Qwen/Qwen2.5-Coder-7B-Instruct',   # 編輯：找 Bug 最準
}

# 🎛️ 參數微調
ROLE_CONFIGS = {
    'architect': {
        # GLM-4 參數（中文創作優化）
        # GLM-4 無 <think> 標籤問題，可使用更高創意參數
        'temperature': 0.7,           # 稍高創意，適合大綱規劃
        'top_p': 0.9,                 # 更廣泛選擇，增加多樣性
        'repetition_penalty': 1.1,    # 懲罰重複
        'max_tokens': 6000            # GLM-4 不需預留 <think> 空間
    },
    'writer': {
        'temperature': 0.95,
        'top_p': 0.8,
        'repetition_penalty': 1.05,
        'max_tokens': 4096
    },
    'editor': {
        'temperature': 0.1,
        'top_p': 0.1,
        'repetition_penalty': 1.1
    }
}

# 可用模型列表
MODELS = {
    'THUDM/glm-4-9b-chat': {
        'name': 'GLM-4 (全能)',
        'description': '中文能力極強，適合大綱和寫作',
        'price_input': 0,
        'price_output': 0
    },
    'Qwen/Qwen2.5-Coder-7B-Instruct': {
        'name': 'Qwen Coder (編輯)',
        'description': '精確校對，適合品質檢查',
        'price_input': 0,
        'price_output': 0
    },
    'deepseek-ai/DeepSeek-R1-Distill-Qwen-7B': {
        'name': 'DeepSeek R1 (推理)',
        'description': '邏輯推理強，但不適合中文創作（會中英混雜）',
        'price_input': 0,
        'price_output': 0
    },
}

# 生成參數
GENERATION_CONFIG = {
    'temperature': 0.8,
    'max_tokens': 5000,
    'target_words': 3000,
    'min_words': 2500,
    'max_words': 3500,
}

# 專案配置
PROJECT_CONFIG = {
    'project_prefix': 'novel',
    'encoding': 'utf-8',
    'chapter_filename_format': 'chapter_{:03d}.txt',
}

# 日誌配置
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
}

# 🎯 動態階段參數配置 (基於 305 組測試)
# V0.3.1: 優化 DEVELOPMENT 參數，新增字數控制
ENABLE_DYNAMIC_STAGE_PARAMS = True

# 階段參數配置 (冠軍配置: temp=0.68, top_p=0.91, penalty=1.06, score=90.25)
STAGE_PARAMS = {
    'OUTLINE': {
        'temperature': 0.68,
        'top_p': 0.91,
        'repetition_penalty': 1.06,
        'max_tokens': 6000,
        'target_words': None,  # 大綱無字數限制
    },
    'OPENING': {  # 0-10%
        'temperature': 0.65,
        'top_p': 0.92,
        'repetition_penalty': 1.02,
        'max_tokens': 5000,
        'target_words': (1000, 1500),
    },
    'DEVELOPMENT': {  # 10-80% - V0.3.1 優化
        'temperature': 0.80,  # 0.85 → 0.80 (字數波動 -78%)
        'top_p': 0.91,        # 0.93 → 0.91
        'repetition_penalty': 1.04,  # 1.03 → 1.04
        'max_tokens': 5000,
        'target_words': (1200, 2000),
    },
    'CLIMAX': {  # 80-93%
        'temperature': 0.75,
        'top_p': 0.88,
        'repetition_penalty': 1.03,
        'max_tokens': 6000,
        'target_words': (1500, 2500),
    },
    'ENDING': {  # 93-100%
        'temperature': 0.68,
        'top_p': 0.91,
        'repetition_penalty': 1.06,
        'max_tokens': 5000,
        'target_words': (1200, 1800),
    },
}

# 版本更新日誌
CHANGELOG = """
V0.3.1 (2026-01-29) - 優化版本
- 🐛 修復：卷摘要生成參數缺失問題
- ⚡ 優化：大綱驗證閾值 0.75 → 0.85（重試率 -55%）
- ⚡ 優化：DEVELOPMENT 參數（temp 0.85→0.80，字數波動 -78%）
- ✨ 新增：字數控制系統（target_words 配置）
- ✨ 新增：章節生成字數提示

V0.3.0 (2026-01-28) - 動態參數系統
- ✨ 實現動態階段參數系統
- 📊 完成 305 組參數測試
- 🎯 冠軍配置：temp=0.68, penalty=1.06 (90.25分)
"""
