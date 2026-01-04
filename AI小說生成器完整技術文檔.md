# AI 小說自動生成器 - 完整技術文檔

> **版本**: v1.0  
> **日期**: 2025-01-03  
> **作者**: Cody  
> **技術棧**: Python 3.9+ | 矽基流動 API | Qwen2.5

---

## 📚 目錄

- [1. 專案概述](#1-專案概述)
- [2. 技術選型分析](#2-技術選型分析)
- [3. 核心架構設計](#3-核心架構設計)
- [4. 分卷管理系統](#4-分卷管理系統)
- [5. 上下文管理方案](#5-上下文管理方案)
- [6. JSON 解析容錯](#6-json-解析容錯)
- [7. 提示詞管理](#7-提示詞管理)
- [8. 生成監控統計](#8-生成監控統計)
- [9. 緩存優化系統](#9-緩存優化系統)
- [10. 一致性檢查](#10-一致性檢查)
- [11. 完整程式碼](#11-完整程式碼)
- [12. 使用指南](#12-使用指南)
- [13. 常見問題](#13-常見問題)

---

## 1. 專案概述

### 1.1 專案背景

在 AI 技術快速發展的今天，大型語言模型 (LLM) 已經具備了相當的文學創作能力。本專案旨在開發一個基於千問 (Qwen) 模型的 **CLI 小說生成工具**，讓使用者能透過簡單的指令介面，自動生成結構完整、情節連貫的小說作品。

### 1.2 核心目標

- **主要目標**: 建立一個易用的命令列小說生成工具
- **技術目標**: 整合矽基流動 API，實現穩定的 AI 內容生成
- **品質目標**: 確保生成內容的連貫性、文學性和可讀性
- **使用目標**: 降低小說創作門檻，輔助創作者構思情節

### 1.3 目標用戶

- 業餘小說創作者（尋找靈感）
- 網路文學作家（快速產出初稿）
- 遊戲開發者（需要劇本/世界觀文本）
- 文學愛好者（體驗 AI 創作）

### 1.4 核心特性

✨ **智能分卷系統**
- 根據劇情重點自動分卷
- 非固定章節數，靈活調整
- 語義化的卷結構設計

🧠 **雙層上下文管理**
- 跨卷：卷摘要壓縮（支援 100+ 章）
- 卷內：RAG 語義檢索 + 金字塔分層

🔒 **強大的一致性保證**
- 角色性格追蹤
- 時間線檢查
- 設定一致性驗證
- 劇情邏輯檢查

📊 **全面監控統計**
- 即時進度顯示
- 成本追蹤
- 品質評估
- 詳細報告生成

---

## 2. 技術選型分析

### 2.1 為何選擇 CLI 而非 GUI？

#### 優勢

1. **開發效率高**: 專注核心邏輯，無需處理 UI 框架
2. **資源消耗低**: 適合在各種環境運行（包括伺服器）
3. **自動化友善**: 易於整合到其他工作流程
4. **適合技術用戶**: 目標用戶群體熟悉命令列操作

#### 後續擴展性

```
CLI 作為核心引擎
    ↓
未來可包裝成 Web 介面
    ↓
或提供 Python 模組供其他程式呼叫
```

### 2.2 API vs 本地模型對比

| 考量因素 | 矽基流動 API | 本地 Ollama |
|---------|------------|-----------|
| **部署難度** | ⭐ (僅需 API Key) | ⭐⭐⭐ (需下載模型) |
| **運行速度** | ⭐⭐⭐⭐ (雲端 GPU) | ⭐⭐ (視硬體而定) |
| **成本** | 按量計費 (極低) | 免費但需硬體 |
| **品質** | ⭐⭐⭐⭐ (可選大模型) | ⭐⭐⭐ (受限本地資源) |
| **隱私性** | ⭐⭐ (數據上傳) | ⭐⭐⭐⭐⭐ (完全本地) |
| **網路依賴** | 必須連網 | 無需網路 |

#### 決策

採用 **矽基流動 API**，原因：
1. 開發階段快速迭代
2. 成本極低（測試階段 <¥1）
3. 可隨時切換不同規模模型
4. 未來可增加本地模型作為備選方案

### 2.3 千問模型選擇

#### 可用模型梯度

```
Qwen2.5-7B-Instruct   ← 起步選擇 (平衡速度/品質)
    ↓ 
Qwen2.5-14B-Instruct  ← 品質提升
    ↓
Qwen2.5-32B-Instruct  ← 專業創作
    ↓
Qwen2.5-72B-Instruct  ← 旗艦級 (出版級)
```

#### 推薦策略

- **開發測試**: 7B 模型（省錢）
- **正式創作**: 14B-32B（性價比最佳）
- **精品產出**: 72B（重要作品）

#### 為何選通用版而非 Coder 版？

| 項目 | Instruct (通用版) | Coder (程式版) |
|------|----------|-------|
| 小說生成 | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| 程式開發 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 文學性 | 更豐富細膩 | 偏功能性 |
| 對話自然度 | 更流暢 | 較生硬 |
| 創意發想 | 更好 | 邏輯導向 |

**結論**: 小說創作必須使用 **Instruct 通用版**

---

## 3. 核心架構設計

### 3.1 整體架構圖

```
┌─────────────────────────────────────────┐
│           使用者命令列介面               │
│   (輸入需求、查看進度、控制流程)        │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         NovelGenerator 核心類別          │
│  ┌────────────────────────────────────┐ │
│  │ API 通訊層                         │ │
│  │ - 請求管理                         │ │
│  │ - 錯誤處理                         │ │
│  │ - 重試機制                         │ │
│  └────────────────────────────────────┘ │
│  ┌────────────────────────────────────┐ │
│  │ 內容生成層                         │ │
│  │ - 大綱生成                         │ │
│  │ - 章節生成                         │ │
│  │ - 上下文管理                       │ │
│  └────────────────────────────────────┘ │
│  ┌────────────────────────────────────┐ │
│  │ 專案管理層                         │ │
│  │ - 檔案組織                         │ │
│  │ - 元數據管理                       │ │
│  │ - 版本控制                         │ │
│  └────────────────────────────────────┘ │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│          矽基流動 API 服務               │
│      (Qwen2.5 模型推理)                  │
└─────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│           本地檔案系統                   │
│  novel_project_YYYYMMDD_HHMMSS/         │
│  ├── metadata.json                      │
│  ├── outline.txt                        │
│  ├── chapter_01.txt                     │
│  ├── chapter_02.txt                     │
│  └── full_novel.txt                     │
└─────────────────────────────────────────┘
```

### 3.2 資料流程

**小說生成完整流程:**

```
Step 1: 使用者輸入基本資訊
    ↓
    標題、類型、主題、角色 → metadata.json

Step 2: 生成故事大綱 + 分卷規劃
    ↓
    輸入資訊 → AI → 分卷結構 + 全局大綱 → outline.txt
    
Step 3: 為每卷生成詳細大綱
    ↓
    卷資訊 + 全局大綱 → AI → 卷大綱
    
Step 4: 章節逐一生成
    ↓
    Loop for each chapter:
        上下文(雙層架構) 
            → API 
            → chapter_N.txt
            → 更新追蹤系統
    
Step 5: 卷完成時生成摘要
    ↓
    合併本卷章節 → AI → 卷摘要 → 壓縮存儲
    
Step 6: 全書完成後合併
    ↓
    合併所有章節 → full_novel.txt
```

### 3.3 檔案結構設計

```
novel_星際邊緣_20250103_143000/
├── metadata.json              # 專案設定
├── outline.txt                # 全局大綱
├── volume_plan.json           # 分卷規劃
│
├── volumes/                   # 卷資料夾
│   ├── volume_01/
│   │   ├── outline.txt        # 本卷大綱
│   │   ├── summary.txt        # 本卷摘要
│   │   ├── chapter_01.txt
│   │   ├── chapter_02.txt
│   │   └── ...
│   ├── volume_02/
│   └── ...
│
├── cache/                     # 緩存資料
│   ├── chapter_summaries.json
│   ├── character_states.json
│   └── embeddings/
│
├── reports/                   # 統計報告
│   ├── generation_log.json
│   └── statistics.png
│
└── full_novel.txt            # 完整小說
```

**為何這樣設計？**
1. **清晰的結構** → 一眼看出內容
2. **按卷組織** → 符合小說結構
3. **分離緩存** → 不污染主要內容
4. **詳細記錄** → 方便除錯和分析

---

## 4. 分卷管理系統

### 4.1 為何需要分卷？

傳統的按固定章節數分卷（如每 20 章一卷）存在問題：

❌ **問題**:
- 機械式切割，無視劇情結構
- 可能在高潮處斷開
- 無法適應不同節奏的故事

✅ **語義分卷的優勢**:
- 根據劇情重點自然分段
- 每卷有明確的戲劇目標
- 符合傳統小說結構

### 4.2 語義分卷原理

```
真實小說的分卷邏輯：

第一卷「初入江湖」(8章)
└─ 主線：主角從小村莊到武林大會
└─ 場景：小村→客棧→青城→武林大會
└─ 重點：成長、初次見識江湖險惡
└─ 目標：決定踏入江湖

第二卷「名門之爭」(15章)  
└─ 主線：捲入名門正邪之爭
└─ 場景：各大門派、秘境
└─ 重點：立場選擇、實力提升
└─ 目標：在正邪之間找到自己的道路

第三卷「魔教崛起」(12章)
└─ 主線：對抗魔教陰謀
└─ 場景：魔教總壇、決戰地
└─ 重點：最終對決、揭開身世之謎
└─ 目標：拯救武林，完成成長
```

### 4.3 分卷規劃流程

#### 方式一：AI 自動建議

```python
# 輸入
title = "星際邊緣"
genre = "太空歌劇科幻"
theme = "人類文明的存續與蛻變"
total_chapters = 60

# AI 生成分卷建議
volume_plan = ai_suggest_volumes(title, genre, theme, total_chapters)

# 輸出範例
{
  "volumes": [
    {
      "volume_number": 1,
      "title": "荒原覺醒",
      "main_plot": "主角在邊緣星球發現古老科技，捲入星際陰謀",
      "key_locations": ["荒原星", "廢棄研究站", "邊境空間站"],
      "estimated_chapters": 12,
      "dramatic_goal": "主角獲得關鍵線索，決定離開母星"
    },
    {
      "volume_number": 2,
      "title": "聯邦迷局",
      "main_plot": "進入人類聯邦核心區，發現政治腐敗和外星威脅",
      "key_locations": ["首都星", "議會大廈", "秘密實驗室"],
      "estimated_chapters": 18,
      "dramatic_goal": "揭露部分真相，遭到追殺"
    },
    ...
  ]
}
```

#### 方式二：手動互動規劃

```bash
=== 小說分卷規劃 ===

第1卷設定:
  卷名: 荒原覺醒
  主線劇情: 主角發現古老科技
  主要場景: 荒原星, 研究站
  預計章節數: 12
  本卷目標: 獲得線索並離開

繼續添加下一卷? [Y/n]: Y

第2卷設定:
  ...
```

### 4.4 卷完成判斷機制

#### 多重檢查策略

```python
def should_end_volume(chapter_num, volume_info):
    """判斷是否該結束當前卷"""
    
    checks = []
    
    # 檢查1：章節數範圍
    chapters_in_vol = volume_info['actual_chapters']
    estimated = volume_info['estimated_chapters']
    
    if chapters_in_vol < estimated - 2:
        return False, "章節數未達標"
    
    # 檢查2：AI 判斷目標達成
    if chapters_in_vol >= estimated - 2:
        goal = volume_info['dramatic_goal']
        recent_text = get_recent_chapters(3)
        
        ai_check = ai_check_goal_achieved(goal, recent_text)
        checks.append(ai_check)
    
    # 檢查3：關鍵詞檢測
    keyword_check = keyword_based_check(goal, recent_text)
    checks.append(keyword_check)
    
    # 檢查4：硬性上限
    if chapters_in_vol >= estimated + 3:
        return True, "章節數超限，強制結束"
    
    # 至少2個檢查通過
    if sum(checks) >= 2:
        return True, "戲劇目標達成"
    
    return False, "繼續當前卷"
```

#### 硬性限制

```python
class VolumeConfig:
    MIN_CHAPTERS = 8   # 最少8章
    MAX_CHAPTERS = 20  # 最多20章
```

這樣可以防止：
- 卷太短（劇情不完整）
- 卷太長（失控）

### 4.5 卷摘要生成

**為何需要卷摘要？**

當小說有 100 章時，不可能把所有章節都放進上下文。卷摘要可以：
- 壓縮 90% 以上的內容
- 保留關鍵信息
- 讓後續章節能「記住」前面的重點

**卷摘要包含什麼？**

```
【第一卷摘要範例】

卷名：荒原覺醒
章節：第1-12章

== 本卷主線 ==
主角李明在荒原星發現古老的外星科技遺跡，意外啟動了沉睡千年的
AI系統「阿爾法」，從中得知人類文明面臨的真正威脅...

== 關鍵轉折點 ==
1. 第3章：發現遺跡入口
2. 第7章：啟動阿爾法，得知真相
3. 第10章：遭遇聯邦特工追殺
4. 第12章：決定離開荒原星

== 角色發展 ==
- 李明：從懵懂少年到認識到自己的使命
- 阿爾法：從沉睡的AI到成為重要夥伴
- 張隊長：出場時的導師，在第11章犧牲

== 新增謎團 ==
- 外星文明為何滅亡？
- 人類真正的起源是什麼？
- 聯邦高層隱瞞了什麼？

== 已解謎團 ==
- 荒原星的異常輻射來源（古代能源核心）

== 承上啟下 ==
本卷為全書奠定基調，主角帶著阿爾法和真相碎片，
踏上前往聯邦中心的旅程。第二卷將揭露更深層的陰謀。
```

**生成提示詞**:

```python
def generate_volume_summary(volume_chapters):
    prompt = f"""
請為這一卷小說生成精煉摘要 (500-800字)，必須包含:

1. 【本卷主線】核心劇情發展
2. 【關鍵轉折】3-5個重要轉折點（標註章節）
3. 【角色變化】主要角色的成長
4. 【新增謎團】本卷引入的未解之謎
5. 【已解謎團】本卷解開的伏筆
6. 【承上啟下】與前卷聯繫、對下卷鋪墊

本卷所有章節:
{volume_chapters}

卷摘要:
"""
    return api_call(prompt)
```

---

## 5. 上下文管理方案

### 5.1 核心挑戰

```
問題：如何讓第 100 章記住第 1 章的內容？

矛盾：
  需要：讀取所有前文 (保證一致性)
    VS
  限制：Context Window 有上限

舉例：
  第 100 章生成時
  - 如果只看第 99 章 → 可能與第 5 章矛盾
  - 如果看全部 99 章 → 超過 150,000 tokens ❌
```

### 5.2 解決方案：雙層架構

```
跨卷層級（長距離壓縮）
├─ 第1卷摘要 (800字)
├─ 第2卷摘要 (800字)
├─ 第3卷摘要 (800字)
├─ ...
└─ 【第N卷】← 當前卷

卷內層級（高解析度）
├─ RAG 語義檢索 → 找到本卷最相關的片段
├─ 金字塔分層 → 結構化的摘要
└─ 上一章完整 → 緊密承接
```

### 5.3 跨卷壓縮策略

**距離越遠，壓縮越多**

```python
def get_historical_volumes_context(current_volume):
    """獲取歷史卷的上下文"""
    
    summaries = []
    
    for vol_num in range(1, current_volume):
        distance = current_volume - vol_num
        
        if distance > 5:
            # 超過5卷：極簡版 (200字)
            summary = volume_summaries[vol_num][:200] + "..."
        elif distance > 2:
            # 2-5卷：中等詳細 (500字)
            summary = volume_summaries[vol_num][:500]
        else:
            # 最近2卷：完整版 (800字)
            summary = volume_summaries[vol_num]
        
        summaries.append(f"第{vol_num}卷：{summary}")
    
    return "\n\n".join(summaries)
```

**Token 使用範例（第 17 卷第 8 章）**

```
歷史卷摘要：
├─ 第1-11卷極簡 (每卷200字) = 2,200字 → 3,300 tokens
├─ 第12-15卷中等 (每卷500字) = 2,000字 → 3,000 tokens
└─ 第16卷完整 (800字) → 1,200 tokens

小計：7,500 tokens
```

### 5.4 卷內 RAG + 金字塔

#### RAG (Retrieval-Augmented Generation)

**原理**：把章節轉成向量，按相似度檢索

```python
# 1. 存儲階段：每寫完一章
chapter_text = "李明站在懸崖邊..."
embedding = encoder.encode(chapter_text)  # 轉成768維向量
vector_db.store(chapter_num, embedding, chapter_text)

# 2. 生成階段：寫第50章時
query = "第50章重點：李明回到懸崖做出決定"
query_embedding = encoder.encode(query)

# 搜尋最相關的10個片段
relevant_chunks = vector_db.search(query_embedding, top_k=10)

# 結果可能包括：
# - 第3章：李明第一次來到懸崖
# - 第27章：李明在懸崖遇見師父
# - 第45章：懸崖上的約定
```

**優勢**：
- ✅ 自動找到相關內容（即使是很久之前的章節）
- ✅ Token 使用少（只載入相關片段）
- ✅ 語義理解（不只是關鍵字匹配）

#### 金字塔分層

```
Level 3: 全卷主線 (200字)
    ↓
Level 2: 章節摘要 (每章200字)
    ↓
Level 1: 段落摘要 (每段50字)
    ↓
Level 0: 完整章節 (每章3000字)
```

**生成第 10 章時的上下文構建**：

```python
def build_pyramid_context(target_chapter):
    """構建金字塔式上下文"""
    
    context = []
    
    # Level 3: 全卷主線
    context.append(f"【本卷主線】\n{volume_main_plot}")
    
    # Level 2: 前面章節的摘要
    for ch in range(1, target_chapter):
        summary = chapter_summaries[ch]  # 200字
        context.append(f"第{ch}章：{summary}")
    
    # Level 0: 上一章完整
    prev_chapter = load_chapter(target_chapter - 1)
    context.append(f"【上一章完整】\n{prev_chapter}")
    
    return "\n\n".join(context)
```

### 5.5 完整的上下文構建流程

```python
def build_complete_context(chapter_num, volume_num, chapter_hint):
    """為章節構建完整上下文"""
    
    parts = []
    
    # === 第一層：全局大綱 ===
    parts.append(global_outline)  # 1,000 tokens
    
    # === 第二層：歷史卷摘要 ===
    if volume_num > 1:
        historical = get_historical_volumes_context(volume_num)
        parts.append(historical)  # ~7,500 tokens
    
    # === 第三層：本卷 RAG 檢索 ===
    relevant_chunks = rag_retrieve(chapter_hint, top_k=10)
    parts.append(format_rag_results(relevant_chunks))  # ~2,000 tokens
    
    # === 第四層：本卷金字塔摘要 ===
    pyramid = build_pyramid_context(chapter_num)
    parts.append(pyramid)  # ~2,000 tokens
    
    # === 第五層：上一章完整 ===
    if chapter_num > 1:
        prev = load_chapter(chapter_num - 1)
        parts.append(f"【上一章完整】\n{prev}")  # ~4,500 tokens
    
    # 總計：~17,000 tokens
    # 如果模型 context window 是 32K，完全夠用！
    
    return "\n\n".join(parts)
```

### 5.6 Token 預算管理

**問題**：如果總 tokens 超過模型限制怎麼辦？

**解決方案**：動態裁剪

```python
def build_context_within_budget(chapter_num, max_tokens=20000):
    """確保上下文在 token 預算內"""
    
    parts = {
        'global': (global_outline, 1000, True),      # (內容, tokens, 必須)
        'historical': (historical_vols, 7500, True),
        'rag': (rag_chunks, 2000, False),            # 可選
        'pyramid': (pyramid_summary, 2000, False),
        'previous': (prev_chapter, 4500, True)
    }
    
    # 先加入必須的
    selected = []
    used_tokens = 0
    
    for key, (content, tokens, required) in parts.items():
        if required:
            selected.append(content)
            used_tokens += tokens
    
    # 剩餘空間分配給可選項
    remaining = max_tokens - used_tokens
    
    for key, (content, tokens, required) in parts.items():
        if not required and tokens <= remaining:
            selected.append(content)
            remaining -= tokens
    
    return "\n\n".join(selected)
```

---

## 6. JSON 解析容錯

### 6.1 問題分析

AI 生成的 JSON 常見問題：

```python
# 期望
{"volume_number": 1, "title": "荒原覺醒"}

# 實際可能收到
"""
好的，這是分卷規劃：

```json
{
  "卷號": 1,
  "標題": "荒原覺醒"
}
```

希望對您有幫助！
"""
```

問題：
1. ❌ 包裹在 markdown 代碼塊中
2. ❌ 使用中文 key
3. ❌ 添加了開場白和結尾
4. ❌ 可能有額外的註釋

### 6.2 暴力清洗策略

```python
import json
import re

class RobustJSONParser:
    """超強容錯的 JSON 解析器"""
    
    def parse(self, response_text):
        """嘗試所有可能的解析方式"""
        
        # 策略1：直接 parse
        try:
            return json.loads(response_text)
        except:
            pass
        
        # 策略2：提取 ```json``` 包裹的內容
        match = re.search(r'```json\s*\n(.*?)\n```', 
                         response_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except:
                pass
        
        # 策略3：提取任何 ``` 包裹的內容
        match = re.search(r'```\s*\n(.*?)\n```', 
                         response_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except:
                pass
        
        # 策略4：找第一個 { 和最後一個 }
        try:
            first = response_text.index('{')
            last = response_text.rindex('}')
            json_str = response_text[first:last+1]
            return json.loads(json_str)
        except:
            pass
        
        # 策略5：找第一個 [ 和最後一個 ]
        try:
            first = response_text.index('[')
            last = response_text.rindex(']')
            json_str = response_text[first:last+1]
            return json.loads(json_str)
        except:
            pass
        
        # 全部失敗
        raise ValueError(f"無法解析 JSON:\n{response_text[:200]}...")
```

### 6.3 Key 映射修正

```python
def parse_with_key_mapping(self, response_text, key_map):
    """解析並修正 key 名稱"""
    
    # 先解析
    data = self.parse(response_text)
    
    # 遞歸修正 key
    return self._fix_keys(data, key_map)

def _fix_keys(self, data, key_map):
    """修正 key 名稱（支援中英文混用）"""
    
    if isinstance(data, dict):
        fixed = {}
        for k, v in data.items():
            # 找標準 key
            standard_key = key_map.get(k, k)
            fixed[standard_key] = self._fix_keys(v, key_map)
        return fixed
    
    elif isinstance(data, list):
        return [self._fix_keys(item, key_map) for item in data]
    
    else:
        return data

# Key 映射表範例
key_map = {
    # 中文 → 英文
    "卷號": "volume_number",
    "標題": "title",
    "卷名": "title",
    
    # 其他可能的變體
    "vol_num": "volume_number",
    "volume": "volume_number",
    "name": "title",
}

# 使用
parser = RobustJSONParser()
result = parser.parse_with_key_mapping(ai_response, key_map)
```

### 6.4 重試機制

```python
def generate_json_with_retry(self, prompt, max_attempts=3):
    """帶重試的 JSON 生成"""
    
    for attempt in range(max_attempts):
        try:
            # 生成
            response = api_call(prompt)
            
            # 解析
            data = parser.parse_with_key_mapping(response, key_map)
            
            # 驗證
            if validate_structure(data):
                return data
            else:
                print(f"第{attempt+1}次：格式不符，重試...")
                # 在 prompt 中加入錯誤提示
                prompt = add_error_feedback(prompt, data)
        
        except Exception as e:
            print(f"第{attempt+1}次失敗：{e}")
            if attempt == max_attempts - 1:
                raise
    
    raise ValueError("多次嘗試後仍無法生成有效 JSON")
```

### 6.5 手動降級方案

```python
def fallback_interactive_input():
    """降級方案：手動輸入"""
    
    print("\n自動生成失敗，改用手動輸入")
    
    volumes = []
    while True:
        print(f"\n第{len(volumes)+1}卷:")
        title = input("  卷名: ")
        if not title:
            break
        
        plot = input("  主線: ")
        locations = input("  場景(逗號分隔): ").split(',')
        chapters = int(input("  章節數: ") or "10")
        goal = input("  目標: ")
        
        volumes.append({
            'volume_number': len(volumes) + 1,
            'title': title,
            'main_plot': plot,
            'key_locations': [l.strip() for l in locations],
            'estimated_chapters': chapters,
            'dramatic_goal': goal
        })
        
        if input("\n繼續? [Y/n]: ").lower() == 'n':
            break
    
    return {'volumes': volumes}
```

---

## 7. 提示詞管理

### 7.1 核心問題

**AI 會遺忘和產生幻覺**

```
第1次生成: AI 很乖，完全按照指示
    ↓
第5次生成: AI 開始「理解」你的意思，自作主張
    ↓  
第10次生成: AI 完全忘記最初的規則，開始 freestyle
    ↓
第20次生成: AI 產生幻覺，混淆不同章節的內容
```

### 7.2 解決方案：每次重建提示詞

**關鍵原則**：
- ✅ 每次都是全新的對話
- ✅ 不累積歷史 messages
- ✅ 每次都注入完整規則

```python
# ❌ 錯誤做法
messages_history = []  # 累積所有對話

def generate_chapter(n):
    messages_history.append({
        "role": "user",
        "content": f"寫第{n}章"
    })
    response = api_call(messages_history)  # 會被歷史影響
    messages_history.append({"role": "assistant", "content": response})

# ✅ 正確做法
def generate_chapter(n):
    # 每次重新構建完整提示詞
    full_prompt = build_complete_prompt(n)
    
    # 只用這一次的 message
    messages = [{"role": "user", "content": full_prompt}]
    
    # 完全獨立的調用
    response = api_call(messages)
    return response
```

### 7.3 提示詞模板系統

```python
class PromptTemplateManager:
    def __init__(self):
        # 核心系統規則（永遠不變）
        self.SYSTEM_CORE = """
你是專業小說作家。

核心規則（永遠遵守）:
1. 嚴格按照大綱創作
2. 保持角色性格一致
3. 延續前文劇情
4. 字數 2500-3500 字
5. 不添加章節標題
6. 第三人稱敘述

禁止事項:
- 不要跳出故事做旁白
- 不要編造大綱中沒有的設定
- 不要讓角色突然性格大變
"""
        
        # 格式控制
        self.FORMAT_RULES = """
輸出格式:
1. 只輸出正文
2. 不要 ``` 標記
3. 段落間空行分隔
4. 直接開始，不要開場白
5. 結尾不要「本章完」
"""
        
        # 一致性要求
        self.CONSISTENCY_RULES = """
一致性要求:
1. 仔細閱讀【前文回顧】
2. 角色設定必須一致
3. 時間線合理
4. 不重複已發生事件
5. 設定前後統一
"""
    
    def build_chapter_prompt(self, chapter_num, context_data):
        """構建完整提示詞"""
        
        parts = []
        
        # 1. 系統規則（最高優先級）
        parts.append(self.SYSTEM_CORE)
        parts.append(self.FORMAT_RULES)
        parts.append(self.CONSISTENCY_RULES)
        
        # 2. 當前任務
        parts.append(f"""
當前任務:
- 第 {chapter_num} 章
- 所屬：第 {context_data['volume_num']} 卷
""")
        
        # 3. 全局設定
        parts.append(f"【全書大綱】\n{context_data['global_outline']}")
        
        # 4. 當前卷設定
        parts.append(f"【本卷大綱】\n{context_data['volume_outline']}")
        
        # 5. 角色設定
        parts.append(f"【角色設定】\n{context_data['characters']}")
        
        # 6. 前文回顧
        parts.append(f"【前文回顧】\n{context_data['history']}")
        
        # 7. 上一章完整
        if context_data.get('previous_chapter'):
            parts.append(f"【上一章】\n{context_data['previous_chapter']}")
        
        # 8. 本章要求
        parts.append(f"""
現在創作第 {chapter_num} 章:
字數: 2500-3500字
開始:
""")
        
        return "\n\n".join(parts)
```

### 7.4 週期性強化

```python
def generate_with_reinforcement(self, chapter_num, context):
    """帶週期性強化的生成"""
    
    prompt = self.build_chapter_prompt(chapter_num, context)
    
    # 每 5 章：加強一致性檢查
    if chapter_num % 5 == 0:
        prompt = add_consistency_reminder(prompt)
    
    # 每 10 章：回顧全局設定
    if chapter_num % 10 == 0:
        prompt = add_global_review(prompt)
    
    return api_call(prompt)

def add_consistency_reminder(prompt):
    reminder = """
🔍 一致性檢查點:
請確認:
□ 角色性格一致
□ 時間線合理
□ 無重複情節
□ 伏筆未遺忘
"""
    return reminder + "\n" + prompt
```

### 7.5 防幻覺機制

```python
ANTI_HALLUCINATION_RULES = """
防止錯誤:
1. 只使用【角色設定】中的角色
2. 不編造大綱沒有的設定
3. 不確定的細節寧可模糊
4. 不讓已死角色復活
5. 地名物品與前文一致

檢查清單:
- 這個角色之前出現過嗎？
- 這個設定前文提過嗎？
- 這會矛盾嗎？
"""

def build_safe_prompt(self, chapter_num, context):
    """構建防幻覺提示詞"""
    
    prompt = f"""
{ANTI_HALLUCINATION_RULES}

你只能使用以下資源:

【已確定的角色】
{list_confirmed_characters(context)}

【已確定的地點】
{list_confirmed_locations(context)}

如需新元素，保持次要和模糊。

現在創作第 {chapter_num} 章:
"""
    return prompt
```

---

## 8. 生成監控統計

### 8.1 監控指標

```python
class NovelGenerationMonitor:
    """生成監控系統"""
    
    def __init__(self, project_name):
        self.project_name = project_name
        self.start_time = time.time()
        
        # 基礎統計
        self.stats = {
            'total_chapters': 0,
            'total_volumes': 0,
            'total_words': 0,
            'total_tokens_input': 0,
            'total_tokens_output': 0,
            'total_cost_rmb': 0.0,
            'generation_times': [],
            'regeneration_count': 0,
            'quality_issues': [],
        }
        
        # 詳細記錄
        self.chapter_logs = []
        self.api_calls = []
        self.errors = []
```

### 8.2 章節級監控

```python
def start_chapter(self, chapter_num, volume_num):
    """開始生成章節"""
    return {
        'chapter_num': chapter_num,
        'volume_num': volume_num,
        'start_time': time.time(),
        'attempts': 0
    }

def end_chapter(self, session, chapter_text, tokens_in, tokens_out, cost):
    """結束章節生成"""
    
    duration = time.time() - session['start_time']
    word_count = len(chapter_text)
    
    # 更新統計
    self.stats['total_chapters'] += 1
    self.stats['total_words'] += word_count
    self.stats['total_tokens_input'] += tokens_in
    self.stats['total_tokens_output'] += tokens_out
    self.stats['total_cost_rmb'] += cost
    self.stats['generation_times'].append(duration)
    
    # 記錄日誌
    log_entry = {
        'chapter_num': session['chapter_num'],
        'volume_num': session['volume_num'],
        'word_count': word_count,
        'tokens_input': tokens_in,
        'tokens_output': tokens_out,
        'cost_rmb': cost,
        'duration_seconds': duration,
        'attempts': session['attempts'],
        'timestamp': datetime.now().isoformat()
    }
    
    self.chapter_logs.append(log_entry)
    return log_entry
```

### 8.3 即時進度顯示

```python
def print_progress(self):
    """列印進度"""
    
    print("\n" + "="*60)
    print(f"📊 《{self.project_name}》生成進度")
    print("="*60)
    
    print(f"已生成章節............ {self.stats['total_chapters']}")
    print(f"已完成卷數............ {self.stats['total_volumes']}")
    print(f"總字數................ {self.stats['total_words']:,}")
    print(f"總成本................ ¥{self.stats['total_cost_rmb']:.2f}")
    
    if self.stats['generation_times']:
        avg_time = sum(self.stats['generation_times']) / len(self.stats['generation_times'])
        print(f"平均每章耗時.......... {avg_time:.1f}秒")
    
    print(f"重新生成次數.......... {self.stats['regeneration_count']}")
    print(f"品質問題.............. {len(self.stats['quality_issues'])}")
    
    print("="*60 + "\n")

# 使用
monitor = NovelGenerationMonitor("星際邊緣")

session = monitor.start_chapter(1, 1)
# ... 生成章節 ...
monitor.end_chapter(session, chapter_text, 5000, 3000, 0.003)

if chapter_num % 5 == 0:
    monitor.print_progress()
```

### 8.4 生成報告

```python
def generate_report(self, save_path=None):
    """生成詳細報告"""
    
    report = {
        'project_name': self.project_name,
        'generation_date': datetime.now().isoformat(),
        'summary': self.get_realtime_stats(),
        'chapter_logs': self.chapter_logs,
        'quality_issues': self.stats['quality_issues'],
        'errors': self.errors,
    }
    
    # 分析
    if self.chapter_logs:
        word_counts = [log['word_count'] for log in self.chapter_logs]
        times = [log['duration_seconds'] for log in self.chapter_logs]
        
        report['analysis'] = {
            '平均章節字數': sum(word_counts) / len(word_counts),
            '最短章節': min(word_counts),
            '最長章節': max(word_counts),
            '平均生成時間': sum(times) / len(times),
            '最快生成': min(times),
            '最慢生成': max(times),
        }
    
    # 儲存
    if save_path:
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
    
    return report
```

### 8.5 視覺化統計

```python
def plot_statistics(self):
    """繪製統計圖表"""
    
    import matplotlib.pyplot as plt
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    chapters = [log['chapter_num'] for log in self.chapter_logs]
    word_counts = [log['word_count'] for log in self.chapter_logs]
    times = [log['duration_seconds'] for log in self.chapter_logs]
    costs = [log['cost_rmb'] for log in self.chapter_logs]
    
    # 1. 字數趨勢
    axes[0, 0].plot(chapters, word_counts, marker='o')
    axes[0, 0].axhline(y=3000, color='r', linestyle='--')
    axes[0, 0].set_title('章節字數趨勢')
    axes[0, 0].set_ylabel('字數')
    
    # 2. 生成時間
    axes[0, 1].plot(chapters, times, marker='s', color='green')
    axes[0, 1].set_title('生成時間趨勢')
    axes[0, 1].set_ylabel('耗時(秒)')
    
    # 3. Token 使用
    tokens_in = [log['tokens_input'] for log in self.chapter_logs]
    axes[1, 0].plot(chapters, tokens_in, label='輸入tokens')
    axes[1, 0].set_title('Token使用量')
    axes[1, 0].legend()
    
    # 4. 累積成本
    cumulative = [sum(costs[:i+1]) for i in range(len(costs))]
    axes[1, 1].plot(chapters, cumulative, color='red')
    axes[1, 1].set_title('累積成本')
    axes[1, 1].set_ylabel('成本(¥)')
    
    plt.tight_layout()
    plt.savefig(f'{self.project_name}_statistics.png')
```

---

## 9. 緩存優化系統

### 9.1 為何需要緩存？

**問題**：
- 全局大綱每章都要載入 → 重複讀取檔案
- 卷大綱每章都要載入 → 重複讀取
- 角色設定每章都要查詢 → 重複查詢
- 章節摘要需要 AI 生成 → 重複計算

**解決**：
- 記憶體緩存：常用數據
- 磁碟緩存：生成的摘要
- LRU 緩存：最近使用的數據

### 9.2 緩存架構

```python
class SmartCache:
    """智能緩存系統"""
    
    def __init__(self, cache_dir=".cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
        # 記憶體緩存（快）
        self.memory_cache = {}
        
        # 磁碟緩存（持久）
        self.disk_cache_enabled = True
    
    def get(self, key):
        """獲取緩存"""
        
        # 先查記憶體
        if key in self.memory_cache:
            return self.memory_cache[key]
        
        # 再查磁碟
        cache_file = f"{self.cache_dir}/{key}.pkl"
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                data = pickle.load(f)
                self.memory_cache[key] = data  # 載入到記憶體
                return data
        
        return None
    
    def set(self, key, value, to_disk=True):
        """設定緩存"""
        
        # 存記憶體
        self.memory_cache[key] = value
        
        # 存磁碟
        if to_disk:
            cache_file = f"{self.cache_dir}/{key}.pkl"
            with open(cache_file, 'wb') as f:
                pickle.dump(value, f)
```

### 9.3 緩存策略

```python
class CachedNovelGenerator:
    """帶緩存的生成器"""
    
    def __init__(self):
        self.cache = SmartCache()
    
    def get_global_outline(self, title, genre, theme, force=False):
        """獲取全局大綱（帶緩存）"""
        
        key = f"outline_{title}_{genre}_{theme}"
        
        if not force:
            cached = self.cache.get(key)
            if cached:
                print("✓ 使用緩存的大綱")
                return cached
        
        # 生成新的
        print("⚙️ 生成大綱...")
        outline = self._generate_outline(title, genre, theme)
        
        # 緩存
        self.cache.set(key, outline)
        
        return outline
    
    def get_chapter_summary(self, chapter_num, content):
        """獲取章節摘要（帶緩存）"""
        
        # 用內容 hash 作為 key
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        key = f"summary_{chapter_num}_{content_hash}"
        
        cached = self.cache.get(key)
        if cached:
            return cached
        
        summary = self._generate_summary(content)
        self.cache.set(key, summary)
        
        return summary
```

### 9.4 LRU 緩存

```python
from functools import lru_cache

class CharacterManager:
    """角色管理（使用 LRU 緩存）"""
    
    @lru_cache(maxsize=50)
    def get_character(self, name):
        """獲取角色（自動緩存最近 50 個）"""
        return self._load_from_db(name)
```

### 9.5 預載入

```python
def preload_common_data(self):
    """預載入常用數據"""
    
    print("⚙️ 預載入中...")
    
    # 預載全局大綱
    self.cache.get('global_outline')
    
    # 預載所有角色設定
    for char_name in all_characters:
        self.get_character(char_name)
    
    print("✓ 預載入完成")
```

---

## 10. 一致性檢查

### 10.1 檢查維度

```
一致性檢查系統
├─ 角色一致性
│   ├─ 性格是否一致
│   ├─ 能力是否合理
│   ├─ 外貌是否統一
│   └─ 生死狀態
├─ 時間線一致性
│   ├─ 相對時間合理性
│   ├─ 絕對時間合理性
│   └─ 事件順序
├─ 設定一致性
│   ├─ 地點描述
│   ├─ 物品屬性
│   └─ 規則設定
└─ 劇情邏輯
    ├─ 事件重複檢測
    ├─ 謎團管理
    └─ 因果關係
```

### 10.2 角色一致性追蹤

```python
class CharacterConsistencyTracker:
    """角色一致性追蹤"""
    
    def __init__(self):
        self.character_db = {}  # 角色數據庫
        self.character_states = {}  # 各章狀態
    
    def register_character(self, name, profile):
        """註冊角色"""
        self.character_db[name] = {
            'personality': profile['personality'],
            'appearance': profile['appearance'],
            'abilities': profile['abilities'],
            'relationships': profile['relationships']
        }
    
    def check(self, chapter_content, context):
        """檢查章節中的角色一致性"""
        
        issues = []
        
        # 提取出現的角色
        chars = self._extract_characters(chapter_content)
        
        for char in chars:
            if char not in self.character_db:
                issues.append({
                    'type': 'unknown_character',
                    'severity': 'high',
                    'message': f'出現未定義角色：{char}'
                })
                continue
            
            # 檢查性格
            if not self._check_personality(char, chapter_content):
                issues.append({
                    'type': 'personality_inconsistency',
                    'severity': 'medium',
                    'character': char,
                    'message': f'{char}的行為與性格設定不符'
                })
            
            # 檢查能力
            if not self._check_abilities(char, chapter_content):
                issues.append({
                    'type': 'ability_inconsistency',
                    'severity': 'high',
                    'character': char,
                    'message': f'{char}使用了未定義的能力'
                })
            
            # 檢查生死
            if self._is_dead(char, context):
                if not self._is_flashback(chapter_content):
                    issues.append({
                        'type': 'dead_character_appears',
                        'severity': 'critical',
                        'character': char,
                        'message': f'{char}已死亡卻再次出現'
                    })
        
        return issues
```

### 10.3 時間線追蹤

```python
class TimelineTracker:
    """時間線追蹤"""
    
    def __init__(self):
        self.events = []  # 事件時間軸
        self.current_time = None
    
    def check(self, chapter_num, content):
        """檢查時間線"""
        
        issues = []
        
        # 提取時間標記
        markers = self._extract_time_markers(content)
        
        for marker in markers:
            if not self._is_chronologically_valid(marker):
                issues.append({
                    'type': 'timeline_error',
                    'severity': 'high',
                    'message': f'時間線錯誤：{marker}'
                })
        
        return issues
    
    def _extract_time_markers(self, content):
        """提取時間標記"""
        
        markers = []
        
        # 相對時間
        patterns = ['第二天', '三天後', '一週後', '同時']
        for p in patterns:
            if p in content:
                markers.append({'type': 'relative', 'marker': p})
        
        # 絕對時間
        import re
        dates = re.findall(r'\d+年\d+月\d+日', content)
        for d in dates:
            markers.append({'type': 'absolute', 'marker': d})
        
        return markers
```

### 10.4 完整檢查流程

```python
class ConsistencyChecker:
    """一致性檢查系統"""
    
    def __init__(self):
        self.character_tracker = CharacterConsistencyTracker()
        self.timeline_tracker = TimelineTracker()
        self.setting_tracker = SettingTracker()
        self.plot_tracker = PlotConsistencyTracker()
    
    def check_chapter(self, chapter_num, content, context):
        """全面檢查章節"""
        
        all_issues = []
        
        # 1. 角色
        issues = self.character_tracker.check(content, context)
        all_issues.extend(issues)
        
        # 2. 時間線
        issues = self.timeline_tracker.check(chapter_num, content)
        all_issues.extend(issues)
        
        # 3. 設定
        issues = self.setting_tracker.check(content, context)
        all_issues.extend(issues)
        
        # 4. 劇情
        issues = self.plot_tracker.check(content, context)
        all_issues.extend(issues)
        
        # 分級處理
        critical = [i for i in all_issues if i['severity'] == 'critical']
        high = [i for i in all_issues if i['severity'] == 'high']
        
        if critical:
            print(f"❌ 發現 {len(critical)} 個嚴重問題")
            for issue in critical:
                print(f"   - {issue['message']}")
            return False, all_issues
        
        if high:
            print(f"⚠️  發現 {len(high)} 個重要問題")
            for issue in high:
                print(f"   - {issue['message']}")
        
        return True, all_issues

# 使用
checker = ConsistencyChecker()
ok, issues = checker.check_chapter(chapter_num, content, context)

if not ok:
    print("需要重新生成")
```

---

## 11. 完整程式碼

### 11.1 專案結構

```
novel-generator/
├── core/
│   ├── __init__.py
│   ├── generator.py          # 核心生成器
│   ├── context_manager.py    # 上下文管理
│   └── api_client.py         # API 調用
│
├── utils/
│   ├── __init__.py
│   ├── json_parser.py        # JSON 解析
│   ├── cache.py              # 緩存系統
│   ├── monitor.py            # 監控統計
│   └── consistency.py        # 一致性檢查
│
├── novel_generator.py        # 主程式
├── requirements.txt
└── README.md
```

### 11.2 requirements.txt

```txt
requests>=2.31.0
sentence-transformers>=2.2.0
chromadb>=0.4.0
matplotlib>=3.7.0
```

### 11.3 核心生成器範例

```python
# novel_generator.py

import requests
import json
import os
from datetime import datetime

class NovelGenerator:
    """AI 小說生成器主類別"""
    
    def __init__(self, api_key, model="Qwen/Qwen2.5-7B-Instruct"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.siliconflow.cn/v1/chat/completions"
        self.project_dir = None
        
    def create_project(self, title):
        """建立專案"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.project_dir = f"novel_{title}_{timestamp}"
        os.makedirs(self.project_dir, exist_ok=True)
        os.makedirs(f"{self.project_dir}/volumes", exist_ok=True)
        print(f"✓ 專案建立: {self.project_dir}")
    
    def generate(self, prompt, temperature=0.8, max_tokens=5000):
        """調用 API 生成內容"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        response = requests.post(self.base_url, headers=headers, json=data)
        result = response.json()
        
        return result['choices'][0]['message']['content']
    
    def generate_chapter(self, chapter_num, context):
        """生成章節"""
        
        prompt = self._build_chapter_prompt(chapter_num, context)
        chapter = self.generate(prompt)
        
        # 儲存
        filename = f"{self.project_dir}/chapter_{chapter_num:02d}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(chapter)
        
        print(f"✓ 第{chapter_num}章完成 ({len(chapter)}字)")
        return chapter
    
    def _build_chapter_prompt(self, chapter_num, context):
        """構建提示詞"""
        
        prompt = f"""
你是專業小說作家。

{context['global_outline']}

{context['volume_outline']}

{context['previous_chapter']}

現在創作第{chapter_num}章，字數2500-3500字:
"""
        return prompt

# 使用範例
if __name__ == "__main__":
    generator = NovelGenerator(api_key="your_api_key")
    generator.create_project("測試小說")
    
    context = {
        'global_outline': "這是一部科幻小說...",
        'volume_outline': "第一卷講述...",
        'previous_chapter': ""
    }
    
    chapter = generator.generate_chapter(1, context)
```

---

## 12. 使用指南

### 12.1 快速開始

**步驟 1：安裝依賴**

```bash
pip install -r requirements.txt
```

**步驟 2：設定 API Key**

```bash
export SILICONFLOW_API_KEY="your_api_key_here"
```

**步驟 3：執行生成**

```bash
python novel_generator.py
```

### 12.2 互動流程

```
=== AI 小說自動生成器 ===

小說標題: 星際邊緣
類型: 科幻
主題: 人類文明存續
預計章節: 60

選擇分卷方式:
1. AI 自動建議
2. 手動規劃
[1]: 1

生成分卷規劃中...

建議結構:
第1卷: 荒原覺醒 (12章)
第2卷: 聯邦迷局 (18章)
...

接受? [Y/n]: Y

生成全局大綱中...
✓ 大綱完成

開始生成第1章...
✓ 第1章完成 (2,847字)

繼續? [Y/n]: Y
```

### 12.3 進階使用

**從斷點恢復:**

```bash
python novel_generator.py --continue novel_xxx_20250103/
```

**重新生成特定章節:**

```bash
python novel_generator.py --regenerate 5 --project novel_xxx/
```

**查看統計:**

```bash
python novel_generator.py --stats novel_xxx/
```

---

## 13. 常見問題

### Q1: 生成的內容重複怎麼辦？

**A**: 調高 temperature 參數

```python
chapter = generator.generate(prompt, temperature=0.9)  # 提高到 0.9
```

### Q2: AI 忘記前面的設定？

**A**: 檢查提示詞是否完整重建

```python
# 確保每次都重新構建完整提示詞
prompt = build_complete_prompt(chapter_num)
```

### Q3: JSON 解析失敗？

**A**: 使用容錯解析器

```python
parser = RobustJSONParser()
data = parser.parse_with_key_mapping(response, key_map)
```

### Q4: Token 超限怎麼辦？

**A**: 動態裁剪上下文

```python
context = build_context_within_budget(chapter_num, max_tokens=20000)
```

### Q5: 成本太高？

**A**: 使用較小的模型或減少生成長度

```python
# 使用 7B 模型
generator = NovelGenerator(model="Qwen/Qwen2.5-7B-Instruct")

# 減少 max_tokens
chapter = generator.generate(prompt, max_tokens=3000)
```

---

## 附錄 A：API 價格參考

| 模型 | 價格（每 1K tokens） |
|-----|-------------------|
| Qwen2.5-7B-Instruct | ¥0.0007 |
| Qwen2.5-14B-Instruct | ¥0.0014 |
| Qwen2.5-32B-Instruct | ¥0.0035 |
| Qwen2.5-72B-Instruct | ¥0.0070 |

**成本估算（100 章小說）:**
- 使用 7B: 約 ¥0.30
- 使用 14B: 約 ¥0.60
- 使用 32B: 約 ¥1.50

---

## 附錄 B：Token 計算

```python
# 粗估：中文 1 字 ≈ 1.5 tokens

# 精確計算
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B-Instruct")

def count_tokens(text):
    return len(tokenizer.encode(text))

# 使用
tokens = count_tokens("這是一段測試文本")
print(f"Token 數: {tokens}")
```

---

## 附錄 C：推薦閱讀

- [Qwen2.5 官方文檔](https://qwen.readthedocs.io/)
- [矽基流動 API 文檔](https://siliconflow.cn/docs)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

---

## 變更日誌

**v1.0 (2025-01-03)**
- 初始版本
- 完整架構設計
- 核心功能實作

---

**文檔結束**

*如有問題或建議，請聯繫開發者*
