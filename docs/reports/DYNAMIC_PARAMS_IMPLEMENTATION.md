# 動態階段參數配置系統 - 實現報告

**版本**: 0.2.2
**日期**: 2026-01-28
**狀態**: 生產就緒

---

## 1. 系統概述

### 1.1 背景

基於 305 組 GLM-4 參數測試，我們發現不同小說創作階段需要不同的參數配置：

- **大綱階段**: 需要結構性和創意平衡
- **開篇階段**: 需要穩定性和吸引力
- **發展階段**: 需要創意和多樣性
- **高潮階段**: 需要張力和情感強度
- **結局階段**: 需要收束和前後呼應

### 1.2 核心發現

| 配置類型 | Temperature | Top_P | Penalty | 測試分數 | 特點 |
|---------|-------------|-------|---------|---------|------|
| **冠軍配置** | 0.68 | 0.91 | 1.06 | 90.25 | 最佳綜合表現 |
| **穩定配置** | 0.65 | 0.92 | 1.02 | 87.5 | 最低變異係數 (CV 3.54%) |
| **創意配置** | 0.85 | 0.93 | 1.03 | 85.8 | 高多樣性 |
| **張力配置** | 0.75 | 0.88 | 1.03 | 88.3 | 適合衝突場景 |

---

## 2. 系統架構

### 2.1 組件結構

```
core/
├── stage_config.py      # 階段配置管理器 (新增)
├── api_client.py        # API 客戶端 (修改: 添加 update_params)
└── generator.py         # 生成器 (修改: 整合階段配置)

tests/
├── test_stage_config.py           # 單元測試 (新增)
└── analyze_param_interaction.py   # 參數交互分析 (已有)
```

### 2.2 類圖

```
┌─────────────────────────────────────────────────────────────┐
│                    StageConfigManager                        │
├─────────────────────────────────────────────────────────────┤
│ + enabled: bool                                              │
│ + _configs: Dict[NovelStage, StageConfig]                   │
├─────────────────────────────────────────────────────────────┤
│ + get_config(stage: NovelStage) -> StageConfig              │
│ + get_config_by_chapter(ch, total) -> (StageConfig, Stage)  │
│ + enable() / disable()                                       │
│ + get_params_dict(stage) -> Dict                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ uses
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       StageConfig                            │
├─────────────────────────────────────────────────────────────┤
│ + temperature: float                                         │
│ + top_p: float                                               │
│ + repetition_penalty: float                                  │
│ + max_tokens: int                                            │
│ + description: str                                           │
│ + score: float                                               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      NovelStage (Enum)                       │
├─────────────────────────────────────────────────────────────┤
│ OUTLINE    # 大綱生成                                         │
│ OPENING    # 開篇 (0-10%)                                     │
│ DEVELOPMENT # 發展 (10-80%)                                   │
│ CLIMAX     # 高潮 (80-93%)                                    │
│ ENDING     # 結局 (93-100%)                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 階段配置詳情

### 3.1 配置參數

| 階段 | 進度範圍 | temp | top_p | penalty | max_tokens | 來源 |
|------|---------|------|-------|---------|------------|------|
| **OUTLINE** | 大綱 | 0.68 | 0.91 | 1.06 | 6000 | 305組測試冠軍 |
| **OPENING** | 0-10% | 0.65 | 0.92 | 1.02 | 5000 | 最穩定配置 |
| **DEVELOPMENT** | 10-80% | 0.85 | 0.93 | 1.03 | 5000 | 高創意組 |
| **CLIMAX** | 80-93% | 0.75 | 0.88 | 1.03 | 6000 | 張力組 |
| **ENDING** | 93-100% | 0.68 | 0.91 | 1.06 | 5000 | 同大綱 |

### 3.2 30 章小說範例

```
章節   |  進度   |    階段      | temp | top_p | penalty
-------|---------|-------------|------|-------|--------
  1    |   3.3%  | OPENING     | 0.65 | 0.92  | 1.02
  3    |  10.0%  | OPENING     | 0.65 | 0.92  | 1.02
  4    |  13.3%  | DEVELOPMENT | 0.85 | 0.93  | 1.03
 15    |  50.0%  | DEVELOPMENT | 0.85 | 0.93  | 1.03
 24    |  80.0%  | DEVELOPMENT | 0.85 | 0.93  | 1.03
 25    |  83.3%  | CLIMAX      | 0.75 | 0.88  | 1.03
 27    |  90.0%  | CLIMAX      | 0.75 | 0.88  | 1.03
 28    |  93.3%  | ENDING      | 0.68 | 0.91  | 1.06
 30    | 100.0%  | ENDING      | 0.68 | 0.91  | 1.06
```

### 3.3 階段分佈

對於 30 章小說：
- **OPENING**: 3 章 (10%)
- **DEVELOPMENT**: 21 章 (70%)
- **CLIMAX**: 3 章 (10%)
- **ENDING**: 3 章 (10%)

---

## 4. 參數交互分析

### 4.1 二維交互效應

#### Temperature × Penalty Top 10
| 排名 | Temperature | Penalty | 平均分 |
|-----|-------------|---------|--------|
| 1 | 0.80 | 1.00 | 81.75 |
| 2 | 0.68 | 1.06 | 81.67 |
| 3 | 0.85 | 1.05 | 80.50 |
| 4 | 0.75 | 1.03 | 79.33 |
| 5 | 0.70 | 0.95 | 79.25 |

#### Temperature × Top_P Top 10
| 排名 | Temperature | Top_P | 平均分 |
|-----|-------------|-------|--------|
| 1 | 0.68 | 0.91 | 83.08 |
| 2 | 0.70 | 0.95 | 82.25 |
| 3 | 0.85 | 0.90 | 80.50 |
| 4 | 0.75 | 0.88 | 79.42 |
| 5 | 0.90 | 0.90 | 79.00 |

### 4.2 協同效應結論

1. **Temperature × Penalty**: 顯著協同效應
   - 「高溫低懲罰」(79.20) 比「低溫高懲罰」(72.25) **高 7.0 分**

2. **Temperature × Top_P**: 顯著協同效應
   - 「高溫低採樣」(79.12) 比「高溫高採樣」(70.75) **高 8.4 分**

### 4.3 三維交互 Top 10

| 排名 | Temp | Top_P | Penalty | 平均分 |
|-----|------|-------|---------|--------|
| 1 | 0.68 | 0.91 | 1.06 | **90.25** |
| 2 | 0.70 | 0.87 | 1.05 | 85.75 |
| 3 | 0.75 | 0.88 | 1.03 | 82.75 |
| 4 | 0.68 | 0.91 | 1.04 | 82.75 |
| 5 | 0.70 | 0.95 | 1.05 | 82.25 |

---

## 5. 使用指南

### 5.1 基本使用

```python
from core.generator import NovelGenerator

# 啟用動態階段參數（默認啟用）
generator = NovelGenerator(
    api_key="your_api_key",
    enable_stage_config=True  # 默認為 True
)

# 生成大綱（自動使用 OUTLINE 配置）
generator.create_project("測試小說", "科幻", "AI覺醒", 30)
generator.generate_outline()

# 生成章節（自動根據進度選擇配置）
for chapter in range(1, 31):
    generator.generate_chapter(chapter)
```

### 5.2 手動獲取配置

```python
from core.stage_config import StageConfigManager, NovelStage

manager = StageConfigManager()

# 按階段獲取
outline_config = manager.get_config(NovelStage.OUTLINE)
print(f"大綱配置: temp={outline_config.temperature}")

# 按章節獲取
config, stage = manager.get_config_by_chapter(15, 30)
print(f"第15章使用 {stage.name} 配置")
```

### 5.3 便捷函數

```python
from core.stage_config import get_stage_params, get_chapter_params

# 獲取階段參數字典
params = get_stage_params(NovelStage.OUTLINE)
# {'temperature': 0.68, 'top_p': 0.91, 'repetition_penalty': 1.06, 'max_tokens': 6000}

# 獲取章節參數字典
params = get_chapter_params(chapter_num=15, total_chapters=30)
# {'temperature': 0.85, 'top_p': 0.93, 'repetition_penalty': 1.03, 'max_tokens': 5000}
```

### 5.4 禁用動態參數

```python
# 方法 1: 初始化時禁用
generator = NovelGenerator(api_key, enable_stage_config=False)

# 方法 2: 運行時禁用
generator.stage_config_manager.disable()
```

---

## 6. 測試結果

### 6.1 單元測試 (7/7 通過)

| 測試項目 | 狀態 | 說明 |
|---------|------|------|
| 階段配置正確性 | ✅ 通過 | 5 個階段配置驗證 |
| 章節階段映射 | ✅ 通過 | 100 章邊界測試 |
| 30章小說模擬 | ✅ 通過 | 分佈合理性驗證 |
| API參數更新 | ✅ 通過 | update_params 功能 |
| 啟用/禁用開關 | ✅ 通過 | 開關狀態切換 |
| 便捷函數 | ✅ 通過 | 全局函數測試 |
| 自定義配置 | ✅ 通過 | 覆蓋默認配置 |

### 6.2 集成測試

```
✅ NovelGenerator 導入成功
✅ enable_stage_config 參數存在
✅ StageConfigManager 整合正常
✅ 章節配置自動切換正常
```

### 6.3 參數交互分析

- **總分析樣本**: 305 組
- **最佳組合**: temp=0.68, top_p=0.91, penalty=1.06
- **最高分數**: 90.25/120

---

## 7. 文件清單

| 文件 | 類型 | 行數 | 說明 |
|------|------|------|------|
| `core/stage_config.py` | 新建 | ~350 | 階段配置管理器核心 |
| `core/api_client.py` | 修改 | +80 | 添加 update_params 方法 |
| `core/generator.py` | 修改 | +30 | 整合 StageConfigManager |
| `tests/test_stage_config.py` | 新建 | ~400 | 完整測試腳本 |
| `tests/analyze_param_interaction.py` | 已有 | ~770 | 參數交互分析 |

---

## 8. 後續優化方向

1. **自適應參數調整**: 根據實時生成質量動態調整參數
2. **A/B 測試框架**: 在線比較不同配置效果
3. **用戶偏好學習**: 根據用戶反饋優化配置
4. **多模型支持**: 為不同模型提供最佳配置

---

## 9. 運行命令

```bash
# 單元測試
python tests/test_stage_config.py --full

# 快速查看配置
python tests/test_stage_config.py --quick

# 參數交互分析
python tests/analyze_param_interaction.py --top 30

# 查看分析報告
cat test_results/mega_test/interaction_report_*.md
```

---

**報告結束**
