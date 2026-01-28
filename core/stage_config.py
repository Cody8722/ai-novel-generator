# -*- coding: utf-8 -*-
"""
AI 小說生成器 - 動態階段參數配置系統

基於 305 組參數測試結果，為不同小說階段提供最佳化參數配置。

階段劃分：
- OUTLINE: 大綱生成（需要結構性和創意平衡）
- OPENING: 開篇（10%，需要穩定性和吸引力）
- DEVELOPMENT: 發展（70%，需要創意和多樣性）
- CLIMAX: 高潮（13%，需要張力和情感強度）
- ENDING: 結局（7%，需要收束和呼應）

測試來源: tests/test_glm4_params_mega.py (305 組參數測試)
"""

import logging
from enum import Enum, auto
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class NovelStage(Enum):
    """
    小說生成階段枚舉

    每個階段有不同的創作需求和最佳參數配置
    """
    OUTLINE = auto()      # 大綱生成
    OPENING = auto()      # 開篇階段 (0-10%)
    DEVELOPMENT = auto()  # 發展階段 (10-80%)
    CLIMAX = auto()       # 高潮階段 (80-93%)
    ENDING = auto()       # 結局階段 (93-100%)


@dataclass
class StageConfig:
    """
    階段配置數據類

    Attributes:
        temperature: 溫度參數（控制隨機性）
        top_p: 核採樣參數（控制詞彙多樣性）
        repetition_penalty: 重複懲罰（避免重複內容）
        max_tokens: 最大生成 token 數
        description: 配置說明
        source: 配置來源（測試組別）
        score: 測試分數
        cv: 變異係數（穩定性指標）
    """
    temperature: float
    top_p: float
    repetition_penalty: float
    max_tokens: int
    description: str
    source: str = ""
    score: float = 0.0
    cv: float = 0.0

    def to_dict(self) -> Dict:
        """轉換為字典格式（用於 API 調用）"""
        return {
            'temperature': self.temperature,
            'top_p': self.top_p,
            'repetition_penalty': self.repetition_penalty,
            'max_tokens': self.max_tokens
        }

    def to_api_params(self) -> Dict:
        """
        轉換為 API 參數格式

        只包含 API 需要的核心參數
        """
        return {
            'temperature': self.temperature,
            'top_p': self.top_p,
            'repetition_penalty': self.repetition_penalty,
            'max_tokens': self.max_tokens
        }


class StageConfigManager:
    """
    階段配置管理器

    管理不同小說階段的最佳參數配置，支持：
    1. 按階段獲取配置
    2. 按章節進度自動選擇配置
    3. 配置啟用/禁用開關
    4. 完整的日誌記錄

    使用示例：
        manager = StageConfigManager()

        # 按階段獲取
        config = manager.get_config(NovelStage.OUTLINE)

        # 按章節進度獲取
        config = manager.get_config_by_chapter(5, 30)
    """

    # 基於 305 組測試的最佳配置
    # 測試來源: tests/test_glm4_params_mega.py
    DEFAULT_CONFIGS = {
        NovelStage.OUTLINE: StageConfig(
            temperature=0.68,
            top_p=0.91,
            repetition_penalty=1.06,
            max_tokens=6000,
            description="大綱生成 - 冠軍配置",
            source="305組測試冠軍",
            score=90.2,
            cv=4.12
        ),
        NovelStage.OPENING: StageConfig(
            temperature=0.65,
            top_p=0.92,
            repetition_penalty=1.02,
            max_tokens=5000,
            description="開篇階段 - 穩定配置",
            source="305組測試最穩定",
            score=87.5,
            cv=3.54  # 最低變異係數，最穩定
        ),
        NovelStage.DEVELOPMENT: StageConfig(
            temperature=0.85,
            top_p=0.93,
            repetition_penalty=1.03,
            max_tokens=5000,
            description="發展階段 - 創意配置",
            source="305組測試高創意組",
            score=85.8,
            cv=5.21
        ),
        NovelStage.CLIMAX: StageConfig(
            temperature=0.75,
            top_p=0.88,
            repetition_penalty=1.03,
            max_tokens=6000,  # 高潮章節需要更多空間
            description="高潮階段 - 張力配置",
            source="305組測試張力組",
            score=88.3,
            cv=4.56
        ),
        NovelStage.ENDING: StageConfig(
            temperature=0.68,
            top_p=0.91,
            repetition_penalty=1.06,
            max_tokens=5000,
            description="結局階段 - 收束配置（同大綱）",
            source="與大綱相同，確保前後呼應",
            score=90.2,
            cv=4.12
        ),
    }

    # 章節進度到階段的映射閾值
    STAGE_THRESHOLDS = {
        'opening_end': 0.10,      # 0-10%: OPENING
        'development_end': 0.80,  # 10-80%: DEVELOPMENT
        'climax_end': 0.93,       # 80-93%: CLIMAX
        # 93-100%: ENDING
    }

    def __init__(self, enabled: bool = True, custom_configs: Optional[Dict] = None):
        """
        初始化階段配置管理器

        Args:
            enabled: 是否啟用動態階段參數（默認啟用）
            custom_configs: 自定義配置（可覆蓋默認配置）
        """
        self.enabled = enabled
        self._configs = self.DEFAULT_CONFIGS.copy()
        self._current_stage: Optional[NovelStage] = None
        self._last_params: Optional[Dict] = None

        # 應用自定義配置
        if custom_configs:
            self._apply_custom_configs(custom_configs)

        logger.info(f"StageConfigManager 初始化完成，動態參數: {'啟用' if enabled else '禁用'}")

    def _apply_custom_configs(self, custom_configs: Dict) -> None:
        """
        應用自定義配置

        Args:
            custom_configs: 自定義配置字典
        """
        for stage, config in custom_configs.items():
            if isinstance(stage, NovelStage) and isinstance(config, StageConfig):
                self._configs[stage] = config
                logger.info(f"應用自定義配置: {stage.name}")
            elif isinstance(stage, str):
                # 支持字符串形式的階段名
                try:
                    stage_enum = NovelStage[stage.upper()]
                    if isinstance(config, dict):
                        self._configs[stage_enum] = StageConfig(**config)
                    logger.info(f"應用自定義配置: {stage}")
                except (KeyError, TypeError) as e:
                    logger.warning(f"無效的自定義配置: {stage}, 錯誤: {e}")

    def get_config(self, stage: NovelStage) -> StageConfig:
        """
        獲取指定階段的配置

        Args:
            stage: 小說階段

        Returns:
            階段配置
        """
        config = self._configs.get(stage, self._configs[NovelStage.DEVELOPMENT])

        # 記錄階段變化
        if self._current_stage != stage:
            self._log_stage_change(stage, config)
            self._current_stage = stage

        return config

    def get_config_by_chapter(
        self,
        chapter_num: int,
        total_chapters: int
    ) -> Tuple[StageConfig, NovelStage]:
        """
        根據章節號自動選擇配置

        章節進度映射：
        - 0-10%: OPENING（開篇，建立世界觀和角色）
        - 10-80%: DEVELOPMENT（發展，推進劇情）
        - 80-93%: CLIMAX（高潮，衝突爆發）
        - 93-100%: ENDING（結局，收束故事）

        Args:
            chapter_num: 當前章節號（從 1 開始）
            total_chapters: 總章節數

        Returns:
            (階段配置, 階段枚舉) 元組
        """
        if not self.enabled:
            # 禁用時返回默認發展階段配置
            return self._configs[NovelStage.DEVELOPMENT], NovelStage.DEVELOPMENT

        # 計算進度百分比
        progress = chapter_num / total_chapters

        # 確定階段
        stage = self._determine_stage_by_progress(progress)

        # 獲取配置
        config = self.get_config(stage)

        logger.debug(
            f"章節 {chapter_num}/{total_chapters} (進度 {progress:.1%}) "
            f"-> 階段: {stage.name}, 配置: temp={config.temperature}, "
            f"top_p={config.top_p}, penalty={config.repetition_penalty}"
        )

        return config, stage

    def _determine_stage_by_progress(self, progress: float) -> NovelStage:
        """
        根據進度確定階段

        Args:
            progress: 進度百分比 (0.0 - 1.0)

        Returns:
            對應的階段枚舉
        """
        if progress <= self.STAGE_THRESHOLDS['opening_end']:
            return NovelStage.OPENING
        elif progress <= self.STAGE_THRESHOLDS['development_end']:
            return NovelStage.DEVELOPMENT
        elif progress <= self.STAGE_THRESHOLDS['climax_end']:
            return NovelStage.CLIMAX
        else:
            return NovelStage.ENDING

    def _log_stage_change(self, new_stage: NovelStage, config: StageConfig) -> None:
        """
        記錄階段變化日誌

        Args:
            new_stage: 新階段
            config: 新配置
        """
        old_stage_name = self._current_stage.name if self._current_stage else "None"

        logger.info(
            f"階段切換: {old_stage_name} -> {new_stage.name} | "
            f"配置: temp={config.temperature}, top_p={config.top_p}, "
            f"penalty={config.repetition_penalty}, max_tokens={config.max_tokens}"
        )

        # 記錄詳細信息
        if config.source:
            logger.debug(f"  來源: {config.source}")
        if config.score > 0:
            logger.debug(f"  測試分數: {config.score}, CV: {config.cv}%")

    def get_params_dict(self, stage: NovelStage) -> Dict:
        """
        獲取階段的 API 參數字典

        Args:
            stage: 小說階段

        Returns:
            API 參數字典
        """
        config = self.get_config(stage)
        params = config.to_api_params()
        self._last_params = params
        return params

    def get_params_by_chapter(
        self,
        chapter_num: int,
        total_chapters: int
    ) -> Dict:
        """
        根據章節號獲取 API 參數字典

        Args:
            chapter_num: 當前章節號
            total_chapters: 總章節數

        Returns:
            API 參數字典
        """
        config, stage = self.get_config_by_chapter(chapter_num, total_chapters)
        params = config.to_api_params()
        self._last_params = params
        return params

    def enable(self) -> None:
        """啟用動態階段參數"""
        self.enabled = True
        logger.info("動態階段參數已啟用")

    def disable(self) -> None:
        """禁用動態階段參數"""
        self.enabled = False
        logger.info("動態階段參數已禁用")

    def is_enabled(self) -> bool:
        """檢查是否啟用"""
        return self.enabled

    def get_all_configs(self) -> Dict[NovelStage, StageConfig]:
        """獲取所有配置"""
        return self._configs.copy()

    def get_stage_info(self, stage: NovelStage) -> Dict:
        """
        獲取階段的詳細信息

        Args:
            stage: 小說階段

        Returns:
            包含配置和元數據的字典
        """
        config = self._configs.get(stage)
        if not config:
            return {}

        return {
            'stage': stage.name,
            'temperature': config.temperature,
            'top_p': config.top_p,
            'repetition_penalty': config.repetition_penalty,
            'max_tokens': config.max_tokens,
            'description': config.description,
            'source': config.source,
            'score': config.score,
            'cv': config.cv
        }

    def print_all_configs(self) -> None:
        """打印所有配置信息"""
        print("\n" + "=" * 70)
        print("📊 動態階段參數配置")
        print("=" * 70)
        print(f"狀態: {'✅ 啟用' if self.enabled else '❌ 禁用'}")
        print("-" * 70)

        for stage in NovelStage:
            config = self._configs.get(stage)
            if config:
                print(f"\n【{stage.name}】{config.description}")
                print(f"  Temperature: {config.temperature}")
                print(f"  Top-P:       {config.top_p}")
                print(f"  Penalty:     {config.repetition_penalty}")
                print(f"  Max Tokens:  {config.max_tokens}")
                if config.score > 0:
                    print(f"  測試分數:    {config.score} (CV: {config.cv}%)")

        print("\n" + "=" * 70)
        print("階段閾值:")
        print(f"  OPENING:     0% - {self.STAGE_THRESHOLDS['opening_end']*100:.0f}%")
        print(f"  DEVELOPMENT: {self.STAGE_THRESHOLDS['opening_end']*100:.0f}% - {self.STAGE_THRESHOLDS['development_end']*100:.0f}%")
        print(f"  CLIMAX:      {self.STAGE_THRESHOLDS['development_end']*100:.0f}% - {self.STAGE_THRESHOLDS['climax_end']*100:.0f}%")
        print(f"  ENDING:      {self.STAGE_THRESHOLDS['climax_end']*100:.0f}% - 100%")
        print("=" * 70 + "\n")


# 全局默認實例（可選使用）
_default_manager: Optional[StageConfigManager] = None


def get_default_manager() -> StageConfigManager:
    """
    獲取默認的配置管理器實例

    Returns:
        全局配置管理器
    """
    global _default_manager
    if _default_manager is None:
        _default_manager = StageConfigManager()
    return _default_manager


def get_stage_params(stage: NovelStage) -> Dict:
    """
    便捷函數：獲取階段參數

    Args:
        stage: 小說階段

    Returns:
        API 參數字典
    """
    return get_default_manager().get_params_dict(stage)


def get_chapter_params(chapter_num: int, total_chapters: int) -> Dict:
    """
    便捷函數：根據章節獲取參數

    Args:
        chapter_num: 當前章節號
        total_chapters: 總章節數

    Returns:
        API 參數字典
    """
    return get_default_manager().get_params_by_chapter(chapter_num, total_chapters)


if __name__ == '__main__':
    # 測試代碼
    logging.basicConfig(level=logging.DEBUG)

    manager = StageConfigManager()
    manager.print_all_configs()

    # 模擬 30 章小說
    print("\n📖 模擬 30 章小說的參數變化:\n")
    for chapter in range(1, 31):
        config, stage = manager.get_config_by_chapter(chapter, 30)
        progress = chapter / 30 * 100
        print(f"第 {chapter:2d} 章 ({progress:5.1f}%) -> {stage.name:12s} | "
              f"temp={config.temperature:.2f}, top_p={config.top_p:.2f}, "
              f"penalty={config.repetition_penalty:.2f}")
