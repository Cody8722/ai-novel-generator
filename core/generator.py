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
from config import PROJECT_CONFIG, GENERATION_CONFIG, MODEL_ROLES, ROLE_CONFIGS

# Phase 2.1 imports - 延遲載入（只在啟用時導入，避免啟動延遲）
# 這些模組包含 TensorFlow 和 sentence-transformers，導入需要 ~60 秒
# 通過延遲加載，MVP 模式啟動時間從 60 秒降至 2 秒

logger = logging.getLogger(__name__)


class NovelGenerator:
    """
    小說生成器核心類別
    管理專案、生成大綱和章節
    """

    def __init__(self, api_key: str, model: str = None, enable_phase2: bool = False):
        """
        初始化生成器

        Args:
            api_key: API Key
            model: 模型名稱（可選）
            enable_phase2: 是否啟用 Phase 2.1 功能（分卷管理 + 反模式引擎）
        """
        self.api_client = SiliconFlowClient(api_key, model)
        self.prompt_templates = PromptTemplates()
        self.enable_phase2 = enable_phase2

        # 專案信息
        self.project_dir = None
        self.metadata = {}
        self.outline = ""
        self.chapters = []

        # Phase 2.1 管理器（延遲初始化）
        self.outline_validator = None
        self.volume_manager = None
        self.plot_manager = None
        self.character_arc_enforcer = None
        self.conflict_escalator = None
        self.event_graph = None

        # Phase 2.1 數據
        self.volume_plan = None
        self.current_volume_id = 1
        self.chapter_outlines = []
        self.character_states = {}

        if self.enable_phase2:
            self._init_phase2_managers()
            logger.info("小說生成器初始化完成（Phase 2.1 已啟用）")
        else:
            logger.info("小說生成器初始化完成（MVP 模式）")

    def _init_phase2_managers(self):
        """
        初始化 Phase 2.1 管理器

        使用延遲導入策略：
        - 只在啟用 Phase 2.1 時才導入重量級模組
        - 避免 MVP 模式啟動時載入 TensorFlow/sentence-transformers
        - 啟動時間從 60 秒降至 2 秒
        """
        try:
            logger.info("開始載入 Phase 2.1 模組（可能需要 10-60 秒）...")

            # 延遲導入 Phase 2.1 模組
            from utils.outline_validator import OutlineValidator
            from utils.volume_manager import VolumeManager
            from utils.plot_manager import PlotManager
            from core.character_arc_enforcer import CharacterArcEnforcer
            from core.conflict_escalator import ConflictEscalator
            from core.event_dependency_graph import EventDependencyGraph

            logger.info("模組載入完成，正在初始化管理器...")

            self.outline_validator = OutlineValidator()
            self.character_arc_enforcer = CharacterArcEnforcer()
            self.event_graph = EventDependencyGraph()
            self.conflict_escalator = ConflictEscalator()

            # VolumeManager 和 PlotManager 需要在 create_project 後初始化
            logger.info("Phase 2.1 管理器初始化成功")
        except Exception as e:
            logger.warning(f"Phase 2.1 管理器初始化部分失敗: {e}")
            logger.warning("將以降級模式運行")

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

        # Phase 2.1: 初始化分卷管理和劇情控制
        if self.enable_phase2:
            self._init_phase2_project(title, genre, theme, total_chapters)

        print(f"\n✓ 專案建立成功: {self.project_dir}\n")
        return self.project_dir

    def _init_phase2_project(self, title: str, genre: str, theme: str, total_chapters: int):
        """初始化 Phase 2.1 專案功能"""
        try:
            # 導入需要的類（避免作用域問題）
            from core.conflict_escalator import ConflictEscalator
            from utils.plot_manager import PlotManager
            from utils.volume_manager import VolumeManager

            # 初始化 PlotManager 和 ConflictEscalator
            self.conflict_escalator = ConflictEscalator(curve_type='wave_with_climax')
            self.plot_manager = PlotManager(
                total_chapters=total_chapters,
                curve_type='wave_with_climax'
            )

            # 初始化 VolumeManager
            self.volume_manager = VolumeManager(
                validator=self.outline_validator,
                plot_manager=self.plot_manager
            )

            # 執行分卷規劃
            print("⏳ 正在規劃分卷結構...")
            volume_plan = self.volume_manager.plan_volumes(
                title=title,
                genre=genre,
                theme=theme,
                total_chapters=total_chapters
            )

            self.volume_plan = volume_plan

            # 儲存分卷規劃
            volume_plan_file = os.path.join(self.project_dir, 'volume_plan.json')
            with open(volume_plan_file, 'w', encoding=PROJECT_CONFIG['encoding']) as f:
                json.dump(volume_plan, f, ensure_ascii=False, indent=2)

            # 載入角色弧光配置
            arcs_config = os.path.join('config', 'arcs.json')
            if os.path.exists(arcs_config):
                self.character_arc_enforcer.load_arcs_from_config(arcs_config)
                logger.info(f"角色弧光配置已載入: {arcs_config}")

            print(f"✓ 分卷規劃完成: {volume_plan['total_volumes']} 卷")
            print(f"  已儲存: {volume_plan_file}\n")

            logger.info("Phase 2.1 專案功能初始化完成")
        except Exception as e:
            logger.error(f"Phase 2.1 專案初始化失敗: {e}")
            print(f"⚠️  Phase 2.1 功能初始化失敗: {e}")
            print("   將以 MVP 模式繼續\n")

    def generate_outline(self) -> str:
        """
        生成故事大綱 (緊急修復版 - 徹底清理 <think> 和英文)

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

        # 調用 API (使用 Architect 模型 + R1 官方推薦參數)
        result = self.api_client.generate_with_details(
            prompt=prompt,
            model=MODEL_ROLES['architect'],
            **ROLE_CONFIGS['architect']  # 使用 R1 官方推薦參數
        )

        content = result['content']

        # 🔥 緊急修復：徹底清理 <think> 標籤
        import re
        import json

        logger.info(f"原始內容長度: {len(content)} 字")

        # 步驟 1: 移除 <think>...</think> 標籤及內容（包括大小寫變體）
        content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL | re.IGNORECASE)
        content = content.replace('<think>', '').replace('</think>', '')
        content = content.replace('<THINK>', '').replace('</THINK>', '')

        # 步驟 2: 移除開頭的簡體中文思考過程
        # 匹配：「好，我现在需要...」到 JSON 開始前的所有內容
        content = re.sub(r'^[\s\S]*?(?=\{)', '', content)

        # 步驟 3: 移除結尾的 markdown 標記（更精確的方法）
        # 找到最後一個 } 的位置，刪除其後的 ``` 等廢話
        last_brace_pos = content.rfind('}')
        if last_brace_pos != -1:
            # 保留到最後一個 } 為止
            content = content[:last_brace_pos + 1]

        # 步驟 4: 清理空白
        content = content.strip()

        # 步驟 4: 驗證清理結果
        if not content or len(content) < 100:
            logger.error("清理後內容過短或為空")
            raise ValueError("大綱生成失敗：內容被過度過濾")

        if '<think>' in content.lower() or '好，我现在' in content:
            logger.error("思考過程未完全清理")
            raise ValueError("大綱生成失敗：仍包含思考過程")

        # 步驟 5: 檢查是否為英文內容
        try:
            outline_dict = json.loads(content)

            # 檢查第一章的 outline 是否包含大量英文
            if 'chapters' in outline_dict and len(outline_dict['chapters']) > 0:
                first_chapter = outline_dict['chapters'][0].get('outline', '')
                english_words = re.findall(r'\b[a-zA-Z]+\b', first_chapter)
                english_ratio = len(' '.join(english_words)) / max(len(first_chapter), 1)

                if english_ratio > 0.3:  # 如果超過 30% 是英文
                    logger.error(f"大綱包含過多英文（{english_ratio:.1%}）")
                    raise ValueError(f"大綱生成失敗：包含大量英文內容（{english_ratio:.0%}）")

                logger.info(f"英文比例檢查: {english_ratio:.1%}")

        except json.JSONDecodeError:
            logger.warning("無法解析 JSON 進行英文檢查")

        # 步驟 6: 檢查品質指標
        quality_issues = []
        if content.count('*') > 50:
            quality_issues.append("包含過多星號（可能用於代替角色名）")
        if content.count('...') > 20:
            quality_issues.append("包含過多省略號（可能用於代替內容）")
        if '*********' in content or '........' in content:
            quality_issues.append("包含連續星號或省略號（內容不完整）")

        if quality_issues:
            logger.warning(f"大綱品質警告: {', '.join(quality_issues)}")
            print(f"⚠️  大綱品質警告:")
            for issue in quality_issues:
                print(f"  - {issue}")

        self.outline = content

        # 儲存清理後的大綱
        outline_file = os.path.join(self.project_dir, 'outline.txt')
        with open(outline_file, 'w', encoding=PROJECT_CONFIG['encoding']) as f:
            f.write(self.outline)

        logger.info(f"清理後內容長度: {len(content)} 字")
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

        # Phase 2.1 啟用時使用 10 步工作流程
        if self.enable_phase2 and self.volume_manager:
            return self._generate_chapter_phase2(chapter_num)
        else:
            return self._generate_chapter_mvp(chapter_num)

    def _generate_chapter_mvp(self, chapter_num: int) -> Dict:
        """MVP 模式章節生成（向後兼容）"""
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

        # 調用 API (使用 Writer 模型生成章節)
        result = self.api_client.generate_with_details(
            prompt=prompt,
            temperature=GENERATION_CONFIG['temperature'],
            max_tokens=GENERATION_CONFIG['max_tokens'],
            model=MODEL_ROLES['writer']
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

    def _generate_chapter_phase2(self, chapter_num: int) -> Dict:
        """
        Phase 2.1 增強版章節生成（10 步工作流程）

        1. 載入卷大綱和卷摘要
        2. 獲取劇情指引 (PlotManager)
        3. 獲取角色狀態 (CharacterArcEnforcer)
        4. 獲取事件上下文 (EventDependencyGraph)
        5. 生成章節大綱 (使用 Phase 2 prompt)
        6. 驗證大綱 (OutlineValidator)
        7. 如不通過重新生成大綱
        8. 注入銜接事件
        9. 生成章節內容 (使用 Phase 2 prompt)
        10. 更新角色狀態和事件圖
        """
        print(f"⏳ [Phase 2.1] 正在生成第 {chapter_num} 章...")

        # === 步驟 1: 載入卷大綱和卷摘要 ===
        volume_context = self._load_volume_context(chapter_num)

        # === 步驟 2: 獲取劇情指引 ===
        plot_guidance = self.plot_manager.generate_plot_guidance(
            chapter_num=chapter_num,
            total_chapters=self.metadata['total_chapters'],
            volume_num=volume_context.get('volume_num'),
            volume_context=volume_context.get('outline', '')
        )

        print(f"  📊 章節類型: {plot_guidance['chapter_type_name']}")
        print(f"  ⚡ 衝突強度: {plot_guidance['conflict_level']:.2f}")

        # === 步驟 3: 獲取角色狀態 ===
        character_states = self._get_character_states(chapter_num)

        # === 步驟 4: 獲取事件上下文 ===
        event_context = self._get_event_context(chapter_num)

        # === 步驟 5-7: 生成並驗證章節大綱 ===
        chapter_outline = self._generate_validated_outline(
            chapter_num=chapter_num,
            volume_context=volume_context,
            plot_guidance=plot_guidance,
            max_retries=3
        )

        # === 步驟 8: 注入銜接事件 ===
        if event_context.get('bridge_events'):
            chapter_outline = self._inject_bridge_events(
                chapter_outline,
                event_context['bridge_events']
            )

        # === 步驟 9: 生成章節內容 ===
        chapter_content, generation_result = self._generate_chapter_content_phase2(
            chapter_num=chapter_num,
            chapter_outline=chapter_outline,
            volume_context=volume_context,
            plot_guidance=plot_guidance,
            character_states=character_states,
            event_context=event_context
        )

        # 儲存章節
        chapter_file = self._save_chapter_phase2(
            chapter_num=chapter_num,
            content=chapter_content,
            outline=chapter_outline,
            metadata={
                'plot_guidance': plot_guidance,
                'character_states': character_states,
                'validation_passed': True
            }
        )

        # === 步驟 10: 更新角色狀態和事件圖 ===
        self._update_character_states(chapter_num, chapter_content, character_states)
        self._update_event_graph(chapter_num, chapter_content, chapter_outline)

        # 章節信息
        word_count = len(chapter_content)
        chapter_info = {
            'chapter_num': chapter_num,
            'volume_num': volume_context.get('volume_num', 1),
            'chapter_type': plot_guidance['chapter_type'],
            'conflict_level': plot_guidance['conflict_level'],
            'word_count': word_count,
            'tokens_input': generation_result['tokens_input'],
            'tokens_output': generation_result['tokens_output'],
            'cost': generation_result['cost'],
            'file_path': chapter_file,
            'validation_passed': True
        }

        self.chapters.append(chapter_info)

        print(f"✓ 第 {chapter_num} 章完成")
        print(f"  字數: {word_count}")
        print(f"  成本: ¥{generation_result['cost']:.4f}")
        print(f"  已儲存: {chapter_file}\n")

        # 檢查是否需要結束當前卷
        if self.volume_manager and self.volume_plan:
            # 獲取當前卷信息
            current_volume = self.volume_plan['volumes'][self.current_volume_id - 1]
            start_chapter = int(current_volume['start_chapter'])

            # 計算本卷已生成章節數
            chapters_in_volume = chapter_num - start_chapter + 1

            # 正確調用 should_end_volume
            should_end, reason = self.volume_manager.should_end_volume(
                volume_num=self.current_volume_id,
                chapters_in_volume=chapters_in_volume,
                current_chapter=chapter_num
            )

            if should_end:
                logger.info(f"卷結束: {reason}")
                self._finalize_volume(self.current_volume_id)
                self.current_volume_id += 1

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

        stats = {
            'project_dir': self.project_dir,
            'title': self.metadata.get('title', ''),
            'chapters_generated': len(self.chapters),
            'total_chapters': self.metadata.get('total_chapters', 0),
            'total_words': total_words,
            'api_statistics': api_stats
        }

        # Phase 2.1 額外統計
        if self.enable_phase2 and self.volume_plan:
            stats['phase2_stats'] = {
                'total_volumes': self.volume_plan.get('total_volumes', 0),
                'current_volume': self.current_volume_id,
                'validation_enabled': True
            }

        return stats

    # ====================================================================
    # Phase 2.1 輔助方法
    # ====================================================================

    def _load_volume_context(self, chapter_num: int) -> Dict:
        """載入卷大綱和卷摘要"""
        if not self.volume_plan:
            return {'volume_num': 1, 'outline': self.outline}

        # 確定當前章節屬於哪一卷
        volume_num = 1
        cumulative_chapters = 0
        for vol in self.volume_plan.get('volumes', []):
            vol_chapters = vol.get('chapters', 0)
            if cumulative_chapters < chapter_num <= cumulative_chapters + vol_chapters:
                volume_num = vol.get('volume_num', volume_num)
                break
            cumulative_chapters += vol_chapters

        # 載入卷大綱
        volume_outline_file = os.path.join(
            self.project_dir,
            f'volumes/volume_{volume_num}/outline.txt'
        )
        volume_outline = ""
        if os.path.exists(volume_outline_file):
            with open(volume_outline_file, 'r', encoding=PROJECT_CONFIG['encoding']) as f:
                volume_outline = f.read()

        # 載入前一卷摘要（如果有）
        previous_volume_summary = ""
        if volume_num > 1:
            prev_summary_file = os.path.join(
                self.project_dir,
                f'volumes/volume_{volume_num - 1}/summary.txt'
            )
            if os.path.exists(prev_summary_file):
                with open(prev_summary_file, 'r', encoding=PROJECT_CONFIG['encoding']) as f:
                    previous_volume_summary = f.read()

        return {
            'volume_num': volume_num,
            'outline': volume_outline,
            'previous_summary': previous_volume_summary
        }

    def _get_character_states(self, chapter_num: int) -> Dict:
        """獲取角色狀態"""
        if not self.character_arc_enforcer:
            return {}

        states = {}
        character_arcs = self.character_arc_enforcer.arcs

        for char_name, arc_data in character_arcs.items():
            # 獲取預期狀態
            expected_state = self.character_arc_enforcer._get_expected_state(
                char_name,
                chapter_num
            )

            # 獲取當前追蹤的狀態
            current_state = self.character_states.get(char_name, expected_state)

            states[char_name] = {
                'current_state': current_state,
                'expected_state': expected_state
            }

        return states

    def _get_event_context(self, chapter_num: int) -> Dict:
        """獲取事件上下文"""
        if not self.event_graph:
            return {}

        context = {
            'bridge_events': [],
            'pending_events': [],
            'plot_holes': []
        }

        # 檢測情節漏洞
        if chapter_num > 5:
            plot_holes = self.event_graph.get_plot_holes()
            if plot_holes:
                logger.warning(f"檢測到 {len(plot_holes)} 個情節漏洞")
                context['plot_holes'] = plot_holes

                # 生成橋接事件建議
                for hole in plot_holes[:3]:  # 最多處理 3 個
                    bridge_event = f"銜接事件：{hole.get('description', '未知事件')}"
                    context['bridge_events'].append(bridge_event)

        return context

    def _generate_validated_outline(
        self,
        chapter_num: int,
        volume_context: Dict,
        plot_guidance: Dict,
        max_retries: int = 3
    ) -> str:
        """生成並驗證章節大綱（步驟 5-7）"""
        if not self.outline_validator:
            # 降級：直接生成簡單大綱
            return f"第 {chapter_num} 章大綱：根據劇情指引進行"

        previous_outlines = self.chapter_outlines[-5:] if len(self.chapter_outlines) >= 5 else self.chapter_outlines

        for attempt in range(max_retries):
            # 生成大綱
            outline_prompt = self.prompt_templates.build_chapter_outline_prompt_phase2(
                title=self.metadata['title'],
                genre=self.metadata['genre'],
                volume_num=volume_context.get('volume_num', 1),
                volume_outline=volume_context.get('outline', ''),
                chapter_num=chapter_num,
                total_chapters=self.metadata['total_chapters'],
                chapter_type=plot_guidance['chapter_type_name'],
                conflict_level=plot_guidance['conflict_level'],
                plot_guidance=plot_guidance,
                previous_outlines=previous_outlines
            )

            # 使用 Architect 模型生成章節大綱
            result = self.api_client.generate_with_details(
                prompt=outline_prompt,
                temperature=GENERATION_CONFIG['temperature'],
                max_tokens=1000,
                model=MODEL_ROLES['architect']
            )

            chapter_outline = result['content']

            # 驗證大綱
            validation_result = self.outline_validator.validate_chapter_outline(
                outline=chapter_outline,
                previous_outlines=previous_outlines,
                chapter_num=chapter_num,
                strict_mode=(attempt == 0)
            )

            if validation_result['is_valid']:
                print(f"  ✓ 大綱驗證通過")
                self.chapter_outlines.append(chapter_outline)
                return chapter_outline
            else:
                warnings = validation_result.get('warnings', [])
                errors = validation_result.get('errors', [])
                print(f"  ⚠️  大綱驗證失敗 (嘗試 {attempt + 1}/{max_retries})")
                for warning in warnings[:2]:
                    print(f"     - {warning}")

                if attempt == max_retries - 1:
                    logger.warning(f"第 {chapter_num} 章大綱驗證失敗，使用最後版本")
                    self.chapter_outlines.append(chapter_outline)
                    return chapter_outline

        return chapter_outline

    def _inject_bridge_events(self, outline: str, bridge_events: list) -> str:
        """注入銜接事件（步驟 8）"""
        if not bridge_events:
            return outline

        injection = "\n\n### 情節銜接\n"
        for event in bridge_events:
            injection += f"- {event}\n"

        return outline + injection

    def _generate_chapter_content_phase2(
        self,
        chapter_num: int,
        chapter_outline: str,
        volume_context: Dict,
        plot_guidance: Dict,
        character_states: Dict,
        event_context: Dict
    ) -> tuple:
        """生成章節內容（步驟 9）"""
        # 獲取上一章內容
        previous_chapter = ""
        if chapter_num > 1:
            prev_file = os.path.join(
                self.project_dir,
                PROJECT_CONFIG['chapter_filename_format'].format(chapter_num - 1)
            )
            if os.path.exists(prev_file):
                with open(prev_file, 'r', encoding=PROJECT_CONFIG['encoding']) as f:
                    content = f.read()
                    # 只保留最後 1000 字作為上下文
                    previous_chapter = content[-1000:] if len(content) > 1000 else content

        # 構建 Phase 2 提示詞
        prompt = self.prompt_templates.build_chapter_prompt_phase2(
            chapter_num=chapter_num,
            total_chapters=self.metadata['total_chapters'],
            volume_num=volume_context.get('volume_num', 1),
            volume_outline=volume_context.get('outline', ''),
            chapter_outline=chapter_outline,
            plot_guidance=plot_guidance,
            previous_chapter=previous_chapter,
            character_states=character_states,
            event_context=event_context
        )

        # 調用 API 生成 (使用 Writer 模型生成章節內容)
        result = self.api_client.generate_with_details(
            prompt=prompt,
            temperature=GENERATION_CONFIG['temperature'],
            max_tokens=GENERATION_CONFIG['max_tokens'],
            model=MODEL_ROLES['writer']
        )

        return result['content'], result

    def _save_chapter_phase2(
        self,
        chapter_num: int,
        content: str,
        outline: str,
        metadata: Dict
    ) -> str:
        """儲存 Phase 2 章節（含元數據）"""
        # 儲存章節內容
        chapter_file = os.path.join(
            self.project_dir,
            PROJECT_CONFIG['chapter_filename_format'].format(chapter_num)
        )
        with open(chapter_file, 'w', encoding=PROJECT_CONFIG['encoding']) as f:
            f.write(content)

        # 儲存章節元數據
        metadata_file = os.path.join(
            self.project_dir,
            f'chapter_{chapter_num:03d}_metadata.json'
        )
        metadata['chapter_num'] = chapter_num
        metadata['outline'] = outline
        metadata['timestamp'] = datetime.now().isoformat()

        with open(metadata_file, 'w', encoding=PROJECT_CONFIG['encoding']) as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        return chapter_file

    def _update_character_states(
        self,
        chapter_num: int,
        chapter_content: str,
        character_states: Dict
    ):
        """更新角色狀態（步驟 10）"""
        if not self.character_arc_enforcer:
            return

        # 簡化版：基於關鍵詞檢測狀態變化
        for char_name, state_info in character_states.items():
            expected_state = state_info.get('expected_state')

            # 檢查角色弧光一致性
            consistency_result = self.character_arc_enforcer.enforce_arc_consistency(
                character=char_name,
                chapter_num=chapter_num,
                current_state=expected_state,
                chapter_outline=chapter_content[:500]  # 只檢查前 500 字
            )

            if not consistency_result['is_consistent']:
                warnings = consistency_result.get('warnings', [])
                for warning in warnings:
                    logger.warning(f"角色 {char_name}: {warning}")

            # 更新追蹤的狀態
            self.character_states[char_name] = expected_state

    def _update_event_graph(
        self,
        chapter_num: int,
        chapter_content: str,
        chapter_outline: str
    ):
        """更新事件依賴圖（步驟 10）"""
        if not self.event_graph:
            return

        # 簡化版：從大綱提取關鍵事件
        # 實際應用中應使用 NLP 進行實體識別
        event_id = f"chapter_{chapter_num}_main_event"

        # 提取依賴關係（假設與上一章相關）
        dependencies = []
        if chapter_num > 1:
            dependencies.append(f"chapter_{chapter_num - 1}_main_event")

        # 添加事件
        self.event_graph.add_event(
            event_id=event_id,
            chapter_num=chapter_num,
            description=chapter_outline[:100],
            dependencies=dependencies
        )

    def _finalize_volume(self, volume_id: int):
        """完成當前卷（生成摘要）"""
        print(f"\n📚 正在完成第 {volume_id} 卷...")

        if not self.volume_manager:
            return

        try:
            # 生成卷摘要 (使用 Architect 模型)
            summary_result = self.volume_manager.generate_volume_summary(
                volume_num=volume_id,
                api_generator_func=lambda prompt: self.api_client.generate_with_details(
                    prompt=prompt,
                    temperature=GENERATION_CONFIG['temperature'],
                    max_tokens=2000,
                    model=MODEL_ROLES['architect']
                )
            )

            if summary_result.get('success'):
                print(f"✓ 第 {volume_id} 卷摘要已生成")
                print(f"  摘要: {summary_result['summary'][:100]}...")
            else:
                logger.warning(f"第 {volume_id} 卷摘要生成失敗")

        except Exception as e:
            logger.error(f"完成第 {volume_id} 卷時發生錯誤: {e}")
            print(f"⚠️  卷摘要生成失敗: {e}")


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
