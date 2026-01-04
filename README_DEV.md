# AI 小說自動生成器 - MVP 版本

> **版本**: v1.0-MVP
> **更新**: 2026-01-04
> **技術棧**: Python 3.9+ | 矽基流動 API | Qwen2.5

---

## 📦 快速開始

### 1. 安裝依賴

```bash
# 建議使用虛擬環境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安裝依賴套件
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
# 複製環境變數範本
cp .env.example .env

# 編輯 .env 檔案，填入您的 API Key
# SILICONFLOW_API_KEY=your_api_key_here
```

**獲取 API Key**: https://cloud.siliconflow.cn/account/ak

### 3. 測試 API 連接

```bash
python novel_generator.py --test-api
```

### 4. 生成小說

```bash
python novel_generator.py
```

---

## 🏗️ 專案結構

```
AI 小說生成器/
├── core/                      # 核心模組
│   ├── __init__.py
│   ├── api_client.py          # API 客戶端（請求/重試/成本追蹤）
│   └── generator.py           # 小說生成器（專案/大綱/章節管理）
│
├── utils/                     # 工具模組
│   ├── __init__.py
│   └── json_parser.py         # JSON 解析器（容錯解析）
│
├── templates/                 # 提示詞模板
│   └── prompts.py             # 提示詞構建邏輯
│
├── novel_generator.py         # CLI 主程式（使用者入口）
├── config.py                  # 配置文件（API/模型/參數）
├── requirements.txt           # Python 依賴
├── .env.example               # 環境變數範本
│
├── README.md                  # 使用者指南
├── README_DEV.md              # 開發文檔（本文件）
└── AI小說生成器完整技術文檔.md  # 完整設計文檔
```

---

## 🎯 MVP 功能範圍

### ✅ 已實作功能

1. **API 客戶端** (`core/api_client.py`)
   - ✅ 矽基流動 API 封裝
   - ✅ 自動重試機制（最多 3 次，指數退避）
   - ✅ Token 計數與成本追蹤
   - ✅ 詳細日誌記錄
   - ✅ 統計信息輸出

2. **小說生成器** (`core/generator.py`)
   - ✅ 專案初始化（建立目錄、元數據）
   - ✅ 故事大綱生成
   - ✅ 章節逐一生成
   - ✅ 自動儲存（大綱、章節、元數據）
   - ✅ 完整小說合併
   - ✅ 生成統計

3. **JSON 解析器** (`utils/json_parser.py`)
   - ✅ 5 策略級聯解析
   - ✅ Markdown 代碼塊提取
   - ✅ Key 映射修正（中英文）
   - ✅ 重試機制

4. **提示詞管理** (`templates/prompts.py`)
   - ✅ 系統規則模板
   - ✅ 大綱生成提示詞
   - ✅ 章節生成提示詞
   - ✅ 一致性規則注入

5. **CLI 介面** (`novel_generator.py`)
   - ✅ 互動式輸入
   - ✅ 模型選擇
   - ✅ 進度顯示
   - ✅ 成本統計
   - ✅ 錯誤處理
   - ✅ API 連接測試

### ❌ 未實作功能（後續迭代）

- ❌ 分卷管理（語義分卷）
- ❌ 雙層上下文架構（RAG + 金字塔）
- ❌ 一致性檢查系統
- ❌ 視覺化統計報告
- ❌ 緩存優化系統
- ❌ 卷摘要生成

---

## 💻 使用範例

### 基本使用

```bash
# 啟動互動式生成
python novel_generator.py
```

互動流程：
```
請輸入小說基本信息：

📚 小說標題: 星際邊緣
🏷️  小說類型（如：科幻、武俠、言情等）: 科幻
💡 核心主題（如：人工智能覺醒、武林爭霸等）: 人類文明的存續
📖 總章節數（建議 5-30 章）: 10

請選擇模型：
1. Qwen2.5-7B
   輕量快速，適合測試
   ...

確認開始生成? [Y/n]: Y
```

### 指定模型

```bash
python novel_generator.py --model "Qwen/Qwen2.5-14B-Instruct"
```

### 測試 API

```bash
python novel_generator.py --test-api
```

---

## 📊 成本估算

### Token 使用（單章）

```
輸入 Token:   ~15,000 (大綱 + 上一章 + 規則)
輸出 Token:   ~3,000  (2500-3500 字章節)
總計:         ~18,000 tokens
```

### 價格（100 章小說）

| 模型 | 每章成本 | 100 章成本 |
|------|---------|-----------|
| Qwen2.5-7B  | ¥0.003 | **¥0.30** |
| Qwen2.5-14B | ¥0.006 | ¥0.60 |
| Qwen2.5-32B | ¥0.015 | ¥1.50 |
| Qwen2.5-72B | ¥0.030 | ¥3.00 |

---

## 🔧 程式碼說明

### API 客戶端

```python
from core.api_client import SiliconFlowClient

# 初始化
client = SiliconFlowClient(api_key="your_key")

# 生成文本
result = client.generate(
    prompt="寫一段故事",
    temperature=0.8,
    max_tokens=5000
)

print(result['content'])      # 生成的文本
print(result['cost'])          # 成本（人民幣）

# 查看統計
client.print_statistics()
```

### 小說生成器

```python
from core.generator import NovelGenerator

# 初始化
generator = NovelGenerator(api_key="your_key")

# 建立專案
generator.create_project(
    title="測試小說",
    genre="科幻",
    theme="AI 覺醒",
    total_chapters=10
)

# 生成大綱
generator.generate_outline()

# 生成章節
generator.generate_chapter(1)
generator.generate_chapter(2)

# 合併完整小說
generator.merge_chapters()
```

---

## 🐛 常見問題

### Q1: API Key 錯誤

**問題**: `❌ 錯誤: 未設定 API Key`

**解決方案**:
1. 確認已複製 `.env.example` 為 `.env`
2. 在 `.env` 中填入正確的 API Key
3. 或使用命令列參數: `--api-key your_key`

### Q2: 網路連接失敗

**問題**: `網路連接失敗`

**解決方案**:
1. 檢查網路連接
2. 確認 API 服務是否正常（https://cloud.siliconflow.cn）
3. 檢查防火牆設定

### Q3: 生成內容重複

**問題**: 章節內容重複或循環

**解決方案**:
1. 調高 `temperature` 參數（在 `config.py` 中）
2. 使用更大的模型（14B 或 32B）
3. 檢查提示詞是否包含足夠的上下文

### Q4: Token 超限

**問題**: `max_tokens` 超過限制

**解決方案**:
1. 減少 `max_tokens` 參數
2. 簡化提示詞
3. 使用支援更大上下文的模型

### Q5: 成本太高

**問題**: 生成成本超出預期

**解決方案**:
1. 使用 7B 模型（最便宜）
2. 減少章節數
3. 調低 `max_tokens`

---

## 📝 開發指南

### 添加新提示詞模板

編輯 `templates/prompts.py`:

```python
@staticmethod
def build_custom_prompt(custom_param):
    """自訂提示詞"""
    return f"""
    你的自訂提示詞...
    參數: {custom_param}
    """
```

### 調整生成參數

編輯 `config.py`:

```python
GENERATION_CONFIG = {
    'temperature': 0.9,      # 提高創造性
    'max_tokens': 6000,      # 增加生成長度
    'target_words': 3500,    # 目標字數
}
```

### 添加新模型

編輯 `config.py`:

```python
MODELS = {
    'your/model-name': {
        'name': '模型顯示名稱',
        'price_input': 0.001,   # 輸入價格
        'price_output': 0.001,  # 輸出價格
        'description': '模型描述'
    },
}
```

---

## 🧪 測試

### 測試 API 客戶端

```bash
python core/api_client.py
```

### 測試生成器

```bash
python core/generator.py
```

### 測試 JSON 解析器

```bash
python utils/json_parser.py
```

### 測試提示詞

```bash
python templates/prompts.py
```

---

## 🚀 後續開發計劃

### Phase 2: 上下文管理（2-3 週）

- [ ] 實作 RAG 語義檢索（使用 ChromaDB）
- [ ] 實作金字塔分層摘要
- [ ] 實作跨卷摘要壓縮
- [ ] Token 預算動態管理

### Phase 3: 品質系統（1-2 週）

- [ ] 角色一致性追蹤
- [ ] 時間線檢查
- [ ] 劇情邏輯驗證
- [ ] 設定一致性檢查

### Phase 4: 優化系統（1 週）

- [ ] 記憶體 + 磁碟緩存
- [ ] 視覺化統計報告
- [ ] 生成監控儀表板
- [ ] 成本優化建議

### Phase 5: 分卷管理（1-2 週）

- [ ] 語義分卷規劃
- [ ] AI 自動建議分卷
- [ ] 卷完成判斷機制
- [ ] 卷摘要生成

---

## 📄 授權

本專案為個人學習專案，僅供參考。

---

## 👨‍💻 開發者

如有問題或建議，請查閱完整技術文檔：`AI小說生成器完整技術文檔.md`

---

**祝您創作愉快！** ✨
