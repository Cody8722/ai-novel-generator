# -*- coding: utf-8 -*-
"""
V0.3.1 優化測試套件

測試內容：
1. 卷摘要生成 Bug 修復
2. 大綱驗證閾值優化 (0.75 → 0.85)
3. DEVELOPMENT 階段參數微調
4. 字數控制功能
5. 字數控制提示

運行方法：
    python tests/test_v031_optimizations.py
    pytest tests/test_v031_optimizations.py -v
"""

import sys
import os

# 添加項目根目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from typing import Tuple, Optional


class TestOutlineValidatorThreshold(unittest.TestCase):
    """測試大綱驗證閾值優化"""

    def test_default_threshold_is_085(self):
        """測試默認閾值為 0.85"""
        from utils.outline_validator import OutlineValidator

        validator = OutlineValidator()
        self.assertEqual(
            validator.similarity_threshold,
            0.85,
            "V0.3.1: 閾值應為 0.85（從 0.75 提高）"
        )

    def test_custom_threshold_can_be_set(self):
        """測試可以設置自定義閾值"""
        from utils.outline_validator import OutlineValidator

        validator = OutlineValidator(similarity_threshold=0.70)
        self.assertEqual(validator.similarity_threshold, 0.70)

    def test_similarity_084_should_pass(self):
        """測試相似度 0.84 應該通過（低於閾值）"""
        from utils.outline_validator import OutlineValidator

        validator = OutlineValidator()
        # 兩個不太相似的大綱
        outline1 = "主角在森林中遇到神秘老人，學習了新的武功秘訣"
        outline2 = "主角來到城市，參加了武林大會，展現實力"

        result = validator.validate_chapter_outline(
            outline=outline2,
            previous_outlines=[outline1],
            chapter_num=2
        )

        # 應該通過驗證（相似度應低於 0.85）
        self.assertTrue(
            result['is_valid'],
            f"不相似的大綱應通過驗證，相似度: {result['similarity_score']}"
        )


class TestDevelopmentStageParams(unittest.TestCase):
    """測試優化後的 DEVELOPMENT 參數"""

    def test_development_temperature(self):
        """測試 DEVELOPMENT temperature 為 0.80"""
        from core.stage_config import StageConfigManager, NovelStage

        manager = StageConfigManager()
        config = manager.get_config(NovelStage.DEVELOPMENT)

        self.assertEqual(
            config.temperature,
            0.80,
            "V0.3.1: DEVELOPMENT temperature 應為 0.80（從 0.85 降低）"
        )

    def test_development_top_p(self):
        """測試 DEVELOPMENT top_p 為 0.91"""
        from core.stage_config import StageConfigManager, NovelStage

        manager = StageConfigManager()
        config = manager.get_config(NovelStage.DEVELOPMENT)

        self.assertEqual(
            config.top_p,
            0.91,
            "V0.3.1: DEVELOPMENT top_p 應為 0.91（從 0.93 降低）"
        )

    def test_development_repetition_penalty(self):
        """測試 DEVELOPMENT repetition_penalty 為 1.04"""
        from core.stage_config import StageConfigManager, NovelStage

        manager = StageConfigManager()
        config = manager.get_config(NovelStage.DEVELOPMENT)

        self.assertEqual(
            config.repetition_penalty,
            1.04,
            "V0.3.1: DEVELOPMENT repetition_penalty 應為 1.04（從 1.03 提高）"
        )


class TestWordCountControl(unittest.TestCase):
    """測試字數控制功能"""

    def test_outline_has_no_target_words(self):
        """測試大綱階段沒有字數限制"""
        from core.stage_config import StageConfigManager, NovelStage

        manager = StageConfigManager()
        config = manager.get_config(NovelStage.OUTLINE)

        self.assertIsNone(
            config.target_words,
            "OUTLINE 階段不應有字數限制"
        )

    def test_opening_has_target_words(self):
        """測試開篇階段有字數控制"""
        from core.stage_config import StageConfigManager, NovelStage

        manager = StageConfigManager()
        config = manager.get_config(NovelStage.OPENING)

        self.assertIsNotNone(config.target_words)
        self.assertEqual(config.target_words, (1000, 1500))

    def test_development_has_target_words(self):
        """測試發展階段有字數控制"""
        from core.stage_config import StageConfigManager, NovelStage

        manager = StageConfigManager()
        config = manager.get_config(NovelStage.DEVELOPMENT)

        self.assertIsNotNone(config.target_words)
        self.assertEqual(config.target_words, (1200, 2000))

    def test_climax_has_target_words(self):
        """測試高潮階段有字數控制"""
        from core.stage_config import StageConfigManager, NovelStage

        manager = StageConfigManager()
        config = manager.get_config(NovelStage.CLIMAX)

        self.assertIsNotNone(config.target_words)
        self.assertEqual(config.target_words, (1500, 2500))

    def test_ending_has_target_words(self):
        """測試結局階段有字數控制"""
        from core.stage_config import StageConfigManager, NovelStage

        manager = StageConfigManager()
        config = manager.get_config(NovelStage.ENDING)

        self.assertIsNotNone(config.target_words)
        self.assertEqual(config.target_words, (1200, 1800))

    def test_all_chapter_stages_have_target_words(self):
        """測試所有章節階段都有 target_words 配置"""
        from core.stage_config import StageConfigManager, NovelStage

        manager = StageConfigManager()

        chapter_stages = [
            NovelStage.OPENING,
            NovelStage.DEVELOPMENT,
            NovelStage.CLIMAX,
            NovelStage.ENDING
        ]

        for stage in chapter_stages:
            config = manager.get_config(stage)
            self.assertIsNotNone(
                config.target_words,
                f"{stage.name} 階段應有 target_words 配置"
            )


class TestWordCountHint(unittest.TestCase):
    """測試字數控制提示"""

    def test_get_word_count_hint_with_target(self):
        """測試有目標字數時返回提示"""
        from core.stage_config import StageConfig

        config = StageConfig(
            temperature=0.8,
            top_p=0.9,
            repetition_penalty=1.0,
            max_tokens=5000,
            description="測試配置",
            target_words=(1000, 2000)
        )

        hint = config.get_word_count_hint()

        self.assertIsNotNone(hint)
        self.assertIn("1,000", hint)
        self.assertIn("2,000", hint)

    def test_get_word_count_hint_without_target(self):
        """測試沒有目標字數時返回 None"""
        from core.stage_config import StageConfig

        config = StageConfig(
            temperature=0.8,
            top_p=0.9,
            repetition_penalty=1.0,
            max_tokens=5000,
            description="測試配置",
            target_words=None
        )

        hint = config.get_word_count_hint()
        self.assertIsNone(hint)

    def test_opening_stage_hint(self):
        """測試開篇階段的字數提示"""
        from core.stage_config import StageConfigManager, NovelStage

        manager = StageConfigManager()
        config = manager.get_config(NovelStage.OPENING)

        hint = config.get_word_count_hint()

        self.assertIsNotNone(hint)
        self.assertIn("1,000", hint)
        self.assertIn("1,500", hint)


class TestStageConfigIntegration(unittest.TestCase):
    """測試階段配置整體功能"""

    def test_to_dict_includes_target_words(self):
        """測試 to_dict 包含 target_words"""
        from core.stage_config import StageConfigManager, NovelStage

        manager = StageConfigManager()
        config = manager.get_config(NovelStage.DEVELOPMENT)

        result = config.to_dict()

        self.assertIn('target_words', result)
        self.assertEqual(result['target_words'], (1200, 2000))

    def test_to_api_params_excludes_target_words(self):
        """測試 to_api_params 不包含 target_words（API 不需要）"""
        from core.stage_config import StageConfigManager, NovelStage

        manager = StageConfigManager()
        config = manager.get_config(NovelStage.DEVELOPMENT)

        result = config.to_api_params()

        self.assertNotIn('target_words', result)
        self.assertIn('temperature', result)
        self.assertIn('top_p', result)

    def test_chapter_30_gets_ending_config(self):
        """測試第 30 章（100%）使用 ENDING 配置"""
        from core.stage_config import StageConfigManager, NovelStage

        manager = StageConfigManager()
        config, stage = manager.get_config_by_chapter(30, 30)

        self.assertEqual(stage, NovelStage.ENDING)
        self.assertEqual(config.target_words, (1200, 1800))


class TestVersionInfo(unittest.TestCase):
    """測試版本信息"""

    def test_config_version(self):
        """測試 config.py 版本為 0.3.1"""
        from config import VERSION

        self.assertEqual(VERSION, '0.3.1', "版本號應為 0.3.1")


def run_all_tests():
    """運行所有測試"""
    print("\n" + "=" * 70)
    print("🧪 V0.3.1 優化測試套件")
    print("=" * 70 + "\n")

    # 創建測試套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加所有測試類
    test_classes = [
        TestOutlineValidatorThreshold,
        TestDevelopmentStageParams,
        TestWordCountControl,
        TestWordCountHint,
        TestStageConfigIntegration,
        TestVersionInfo,
    ]

    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # 運行測試
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 打印摘要
    print("\n" + "=" * 70)
    print("📊 測試摘要")
    print("=" * 70)
    print(f"  測試總數: {result.testsRun}")
    print(f"  通過: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  失敗: {len(result.failures)}")
    print(f"  錯誤: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n🎉 所有測試通過！V0.3.1 優化驗證成功")
    else:
        print("\n❌ 部分測試失敗，請檢查輸出")

    print("=" * 70 + "\n")

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
