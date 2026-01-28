# Release v0.3.0 - 動態階段參數系統

**發布日期**: 2026-01-28
**版本代號**: Dynamic Stage Params Edition

---

## 概述

本版本引入基於 305 組 GLM-4 參數測試的動態階段參數配置系統，實現小說不同創作階段的自動參數優化。

## 主要特性

### 動態階段參數系統

根據小說創作階段自動調整 AI 生成參數：

| 階段 | 進度 | Temperature | Top_P | Penalty | 特點 |
|------|------|-------------|-------|---------|------|
| OUTLINE | 大綱 | 0.68 | 0.91 | 1.06 | 冠軍配置 |
| OPENING | 0-10% | 0.65 | 0.92 | 1.02 | 最穩定 |
| DEVELOPMENT | 10-80% | 0.85 | 0.93 | 1.03 | 高創意 |
| CLIMAX | 80-93% | 0.75 | 0.88 | 1.03 | 高張力 |
| ENDING | 93-100% | 0.68 | 0.91 | 1.06 | 前後呼應 |

### 參數交互分析

- 305 組參數組合完整測試
- 二維交互效應分析 (Temp×Penalty, Temp×TopP)
- 三維交互效應分析
- 協同效應發現：
  - Temperature × Penalty: 高溫低懲罰比低溫高懲罰高 **7.0 分**
  - Temperature × Top_P: 高溫低採樣比高溫高採樣高 **8.4 分**

### 冠軍配置

```python
params = {
    'temperature': 0.68,
    'top_p': 0.91,
    'repetition_penalty': 1.06,
    'max_tokens': 4000
}
# 測試分數: 90.25/120
```

## 新增文件

| 文件 | 說明 |
|------|------|
| `core/stage_config.py` | 階段配置管理器核心模組 |
| `tests/test_stage_config.py` | 完整測試套件 (7 個測試) |
| `tests/analyze_param_interaction.py` | 參數交互分析腳本 |
| `docs/DYNAMIC_PARAMS_SYSTEM.md` | 完整使用文檔 |
| `docs/PARAM_INTERACTION_ANALYSIS.txt` | 參數分析報告 |
| `docs/reports/DYNAMIC_PARAMS_IMPLEMENTATION.md` | 實現報告 |

## 修改文件

| 文件 | 修改內容 |
|------|---------|
| `core/api_client.py` | 新增 `update_params()` 動態參數更新方法 |
| `core/generator.py` | 整合 StageConfigManager |
| `config.py` | 新增 `ENABLE_DYNAMIC_STAGE_PARAMS` 開關和 `STAGE_PARAMS` 配置 |

## 使用方式

### 啟用動態參數（默認）

```python
from core.generator import NovelGenerator

generator = NovelGenerator(
    api_key="your_api_key",
    enable_stage_config=True  # 默認啟用
)

# 生成大綱（自動使用 OUTLINE 配置）
generator.generate_outline()

# 生成章節（自動根據進度選擇配置）
for chapter in range(1, 31):
    generator.generate_chapter(chapter)
```

### 禁用動態參數

```python
generator = NovelGenerator(api_key, enable_stage_config=False)
# 或
generator.stage_config_manager.disable()
```

## 性能提升

| 指標 | 固定參數 | 動態參數 | 提升 |
|------|---------|---------|------|
| 平均分數 | 72.5 | 87.8 | **+21.1%** |
| 最高分數 | 78.0 | 90.25 | **+15.7%** |
| 穩定性 (CV) | 8.2% | 4.3% | **-47.6%** |

## 測試結果

```
tests/test_stage_config.py::test_stage_configs PASSED
tests/test_stage_config.py::test_chapter_stage_mapping PASSED
tests/test_stage_config.py::test_30_chapter_simulation PASSED
tests/test_stage_config.py::test_api_client_update_params PASSED
tests/test_stage_config.py::test_enable_disable PASSED
tests/test_stage_config.py::test_convenience_functions PASSED
tests/test_stage_config.py::test_custom_configs PASSED

======================== 7 passed in 0.32s ========================
```

## 向後兼容性

- 通過 `enable_stage_config=False` 可完全禁用動態參數
- 原有 API 接口保持不變
- 默認配置使用測試驗證的最佳參數

## 升級指南

1. 更新代碼至 v0.3.0
2. 動態參數默認啟用，無需額外配置
3. 如需自定義配置，參考 `docs/DYNAMIC_PARAMS_SYSTEM.md`

---

**完整文檔**: `docs/DYNAMIC_PARAMS_SYSTEM.md`
**技術報告**: `docs/reports/DYNAMIC_PARAMS_IMPLEMENTATION.md`
