# -*- coding: utf-8 -*-
"""
AI 小說生成器 - 提示詞模板管理
"""


class PromptTemplates:
    """提示詞模板管理類別"""

    # 系統核心規則（每次生成都要注入）
    SYSTEM_CORE = """你是專業小說作家，擅長創作引人入勝的故事。

核心規則（永遠遵守）:
1. 嚴格按照大綱創作，不偏離主線
2. 保持角色性格一致，不突然改變
3. 延續前文劇情，確保連貫性
4. 字數控制在 2500-3500 字之間
5. 不添加章節標題，直接開始正文
6. 使用第三人稱敘述
7. 段落間使用空行分隔

禁止事項:
- 不要跳出故事做旁白評論
- 不要編造大綱中沒有的設定
- 不要讓角色突然性格大變
- 不要重複已發生的事件
"""

    # 格式控制
    FORMAT_RULES = """
輸出格式要求:
1. 只輸出正文內容
2. 不要使用 ``` 代碼塊標記
3. 段落間用空行分隔
4. 直接開始故事，不要開場白
5. 結尾不要「本章完」等標記
6. 不要添加任何 JSON 格式
"""

    # 一致性要求
    CONSISTENCY_RULES = """
一致性檢查:
1. 仔細閱讀【前文回顧】，確保情節連貫
2. 角色設定必須與之前一致
3. 時間線要合理，不能錯亂
4. 不重複已發生的事件
5. 世界觀設定前後統一
"""

    @staticmethod
    def build_outline_prompt(title, genre, theme, total_chapters):
        """
        構建生成大綱的提示詞

        Args:
            title: 小說標題
            genre: 類型
            theme: 主題
            total_chapters: 總章節數

        Returns:
            完整的提示詞
        """
        return f"""請為以下小說創作詳細大綱：

小說資訊:
- 標題：{title}
- 類型：{genre}
- 主題：{theme}
- 總章節數：{total_chapters}

請生成包含以下內容的大綱：

1. 【故事概要】（200-300字）
   - 核心劇情
   - 主要衝突
   - 故事走向

2. 【主要角色】（列出3-5個重要角色）
   每個角色包含：
   - 姓名
   - 性格特點（2-3個關鍵詞）
   - 在故事中的作用

3. 【章節規劃】（簡要說明每章重點）
   第1章：[章節重點]
   第2章：[章節重點]
   ...

請開始創作大綱："""

    @staticmethod
    def build_chapter_prompt(chapter_num, total_chapters, outline, previous_chapter=""):
        """
        構建生成章節的提示詞

        Args:
            chapter_num: 當前章節號
            total_chapters: 總章節數
            outline: 故事大綱
            previous_chapter: 上一章內容（可選）

        Returns:
            完整的提示詞
        """
        parts = []

        # 1. 系統規則
        parts.append(PromptTemplates.SYSTEM_CORE)
        parts.append(PromptTemplates.FORMAT_RULES)
        parts.append(PromptTemplates.CONSISTENCY_RULES)

        # 2. 當前任務
        parts.append(f"""
當前任務:
- 創作第 {chapter_num} 章（共 {total_chapters} 章）
- 字數要求：2500-3500 字
""")

        # 3. 故事大綱
        parts.append(f"【故事大綱】\n{outline}\n")

        # 4. 上一章內容（如果有）
        if previous_chapter and chapter_num > 1:
            # 只保留上一章的最後 1000 字作為上下文
            preview_length = min(1000, len(previous_chapter))
            preview = previous_chapter[-preview_length:]
            parts.append(f"【上一章結尾】\n...{preview}\n")

        # 5. 本章要求
        if chapter_num == 1:
            parts.append(f"""
本章要求（第 1 章）:
- 引入主角和背景設定
- 建立故事的基本世界觀
- 設置初始衝突或懸念
- 吸引讀者繼續閱讀

現在創作第 {chapter_num} 章，字數 2500-3500 字：
""")
        elif chapter_num == total_chapters:
            parts.append(f"""
本章要求（最終章）:
- 解決主要衝突
- 為角色提供結局
- 收尾所有重要伏筆
- 給讀者滿意的結束

現在創作第 {chapter_num} 章，字數 2500-3500 字：
""")
        else:
            parts.append(f"""
本章要求（第 {chapter_num} 章）:
- 承接上一章劇情
- 推進故事發展
- 保持節奏和張力
- 為下一章埋下伏筆

現在創作第 {chapter_num} 章，字數 2500-3500 字：
""")

        return "\n".join(parts)

    @staticmethod
    def build_test_prompt():
        """構建 API 測試提示詞"""
        return "請用一句話介紹你自己。"


if __name__ == '__main__':
    # 測試提示詞生成
    templates = PromptTemplates()

    print("=== 大綱生成提示詞 ===")
    outline_prompt = templates.build_outline_prompt(
        title="星際邊緣",
        genre="科幻",
        theme="人類文明的存續與蛻變",
        total_chapters=30
    )
    print(outline_prompt[:500], "...\n")

    print("=== 章節生成提示詞 ===")
    chapter_prompt = templates.build_chapter_prompt(
        chapter_num=1,
        total_chapters=30,
        outline="這是一個關於星際探索的故事...",
        previous_chapter=""
    )
    print(chapter_prompt[:500], "...")
