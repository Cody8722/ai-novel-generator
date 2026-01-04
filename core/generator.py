# -*- coding: utf-8 -*-
"""
AI 小說生成器 - 核心生成器
提供高層次的小說生成介面
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Optional

from core.api_client import SiliconFlowClient
from templates.prompts import PromptTemplates
from config import PROJECT_CONFIG, GENERATION_CONFIG


logger = logging.getLogger(__name__)


class NovelGenerator:
    """
    小說生成器核心類別
    管理專案、生成大綱和章節
    """

    def __init__(self, api_key: str, model: str = None):
        """
        初始化生成器

        Args:
            api_key: API Key
            model: 模型名稱（可選）
        """
        self.api_client = SiliconFlowClient(api_key, model)
        self.prompt_templates = PromptTemplates()

        # 專案信息
        self.project_dir = None
        self.metadata = {}
        self.outline = ""
        self.chapters = []

        logger.info("小說生成器初始化完成")

    def create_project(self, title: str, genre: str, theme: str, total_chapters: int):
        """
        建立新專案

        Args:
            title: 小說標題
            genre: 類型
            theme: 主題
            total_chapters: 總章節數

        Returns:
            專案目錄路徑
        """
        # 生成專案目錄名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_title = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in title)
        safe_title = safe_title.replace(' ', '_')

        project_name = f"{PROJECT_CONFIG['project_prefix']}_{safe_title}_{timestamp}"
        self.project_dir = os.path.abspath(project_name)

        # 建立目錄
        os.makedirs(self.project_dir, exist_ok=True)
        logger.info(f"專案目錄建立: {self.project_dir}")

        # 儲存元數據
        self.metadata = {
            'title': title,
            'genre': genre,
            'theme': theme,
            'total_chapters': total_chapters,
            'created_at': datetime.now().isoformat(),
            'model': self.api_client.model,
        }

        metadata_file = os.path.join(self.project_dir, 'metadata.json')
        with open(metadata_file, 'w', encoding=PROJECT_CONFIG['encoding']) as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)

        logger.info(f"元數據已儲存: {metadata_file}")

        print(f"\n✓ 專案建立成功: {self.project_dir}\n")
        return self.project_dir

    def generate_outline(self) -> str:
        """
        生成故事大綱

        Returns:
            生成的大綱文本
        """
        if not self.metadata:
            raise ValueError("請先建立專案（呼叫 create_project）")

        print("⏳ 正在生成故事大綱...")

        # 構建提示詞
        prompt = self.prompt_templates.build_outline_prompt(
            title=self.metadata['title'],
            genre=self.metadata['genre'],
            theme=self.metadata['theme'],
            total_chapters=self.metadata['total_chapters']
        )

        # 調用 API
        result = self.api_client.generate(
            prompt=prompt,
            temperature=GENERATION_CONFIG['temperature'],
            max_tokens=GENERATION_CONFIG['max_tokens']
        )

        self.outline = result['content']

        # 儲存大綱
        outline_file = os.path.join(self.project_dir, 'outline.txt')
        with open(outline_file, 'w', encoding=PROJECT_CONFIG['encoding']) as f:
            f.write(self.outline)

        print(f"✓ 大綱生成完成（{len(self.outline)} 字）")
        print(f"  成本: ¥{result['cost']:.4f}")
        print(f"  已儲存: {outline_file}\n")

        return self.outline

    def generate_chapter(self, chapter_num: int) -> Dict:
        """
        生成單一章節

        Args:
            chapter_num: 章節號（從 1 開始）

        Returns:
            章節信息字典
        """
        if not self.outline:
            raise ValueError("請先生成大綱（呼叫 generate_outline）")

        print(f"⏳ 正在生成第 {chapter_num} 章...")

        # 獲取上一章內容
        previous_chapter = ""
        if chapter_num > 1:
            prev_file = os.path.join(
                self.project_dir,
                PROJECT_CONFIG['chapter_filename_format'].format(chapter_num - 1)
            )
            if os.path.exists(prev_file):
                with open(prev_file, 'r', encoding=PROJECT_CONFIG['encoding']) as f:
                    previous_chapter = f.read()

        # 構建提示詞
        prompt = self.prompt_templates.build_chapter_prompt(
            chapter_num=chapter_num,
            total_chapters=self.metadata['total_chapters'],
            outline=self.outline,
            previous_chapter=previous_chapter
        )

        # 調用 API
        result = self.api_client.generate(
            prompt=prompt,
            temperature=GENERATION_CONFIG['temperature'],
            max_tokens=GENERATION_CONFIG['max_tokens']
        )

        chapter_content = result['content']
        word_count = len(chapter_content)

        # 儲存章節
        chapter_file = os.path.join(
            self.project_dir,
            PROJECT_CONFIG['chapter_filename_format'].format(chapter_num)
        )
        with open(chapter_file, 'w', encoding=PROJECT_CONFIG['encoding']) as f:
            f.write(chapter_content)

        # 章節信息
        chapter_info = {
            'chapter_num': chapter_num,
            'word_count': word_count,
            'tokens_input': result['tokens_input'],
            'tokens_output': result['tokens_output'],
            'cost': result['cost'],
            'file_path': chapter_file
        }

        self.chapters.append(chapter_info)

        print(f"✓ 第 {chapter_num} 章完成")
        print(f"  字數: {word_count}")
        print(f"  成本: ¥{result['cost']:.4f}")
        print(f"  已儲存: {chapter_file}\n")

        return chapter_info

    def generate_all_chapters(self, start_chapter: int = 1, end_chapter: int = None):
        """
        生成所有章節

        Args:
            start_chapter: 起始章節（默認從第 1 章）
            end_chapter: 結束章節（默認到最後一章）
        """
        if end_chapter is None:
            end_chapter = self.metadata['total_chapters']

        total = end_chapter - start_chapter + 1
        print(f"\n開始生成章節 {start_chapter}-{end_chapter}（共 {total} 章）\n")
        print("="*60)

        for i in range(start_chapter, end_chapter + 1):
            print(f"\n[{i}/{end_chapter}] ", end="")
            try:
                self.generate_chapter(i)
            except Exception as e:
                logger.error(f"第 {i} 章生成失敗: {e}")
                print(f"❌ 第 {i} 章生成失敗: {e}")
                user_input = input("\n是否繼續生成下一章? [Y/n]: ")
                if user_input.lower() == 'n':
                    break

        print("\n" + "="*60)
        print("章節生成完成！\n")

        # 打印統計
        self.api_client.print_statistics()

    def merge_chapters(self):
        """合併所有章節為完整小說"""
        if not self.chapters:
            logger.warning("沒有章節可合併")
            return

        print("⏳ 正在合併章節...")

        full_novel_file = os.path.join(self.project_dir, 'full_novel.txt')

        with open(full_novel_file, 'w', encoding=PROJECT_CONFIG['encoding']) as outfile:
            # 寫入標題資訊
            outfile.write(f"# {self.metadata['title']}\n\n")
            outfile.write(f"類型: {self.metadata['genre']}\n")
            outfile.write(f"主題: {self.metadata['theme']}\n")
            outfile.write(f"生成日期: {self.metadata['created_at']}\n")
            outfile.write(f"\n{'='*60}\n\n")

            # 合併所有章節
            for i in range(1, self.metadata['total_chapters'] + 1):
                chapter_file = os.path.join(
                    self.project_dir,
                    PROJECT_CONFIG['chapter_filename_format'].format(i)
                )

                if not os.path.exists(chapter_file):
                    logger.warning(f"第 {i} 章文件不存在，跳過")
                    continue

                with open(chapter_file, 'r', encoding=PROJECT_CONFIG['encoding']) as infile:
                    outfile.write(f"\n\n## 第 {i} 章\n\n")
                    outfile.write(infile.read())
                    outfile.write(f"\n\n{'─'*60}\n")

        print(f"✓ 完整小說已合併: {full_novel_file}\n")

    def get_statistics(self) -> Dict:
        """獲取生成統計"""
        api_stats = self.api_client.get_statistics()

        total_words = sum(ch['word_count'] for ch in self.chapters)

        return {
            'project_dir': self.project_dir,
            'title': self.metadata.get('title', ''),
            'chapters_generated': len(self.chapters),
            'total_chapters': self.metadata.get('total_chapters', 0),
            'total_words': total_words,
            'api_statistics': api_stats
        }


if __name__ == '__main__':
    # 測試
    import os
    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv('SILICONFLOW_API_KEY')

    if api_key:
        generator = NovelGenerator(api_key)

        # 建立測試專案
        generator.create_project(
            title="測試小說",
            genre="科幻",
            theme="人工智能覺醒",
            total_chapters=3
        )

        # 生成大綱
        generator.generate_outline()

        # 生成第一章
        generator.generate_chapter(1)

        # 打印統計
        stats = generator.get_statistics()
        print("\n統計信息:", json.dumps(stats, ensure_ascii=False, indent=2))
    else:
        print("請設定 SILICONFLOW_API_KEY 環境變數")
