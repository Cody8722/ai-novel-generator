# -*- coding: utf-8 -*-
"""
動態階段參數配置系統 - 測試腳本

測試內容：
1. 所有階段配置正確性
2. 章節進度到階段的映射
3. 30 章小說模擬
4. API 客戶端參數更新
5. 配置啟用/禁用開關
"""

import sys
import os
import logging

# 添加項目根目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.stage_config import (
    StageConfigManager,
    NovelStage,
    StageConfig,
    get_default_manager,
    get_stage_params,
    get_chapter_params
)

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_stage_configs():
    """測試所有階段配置"""
    print("\n" + "=" * 70)
    print("📋 測試 1: 階段配置正確性")
    print("=" * 70)

    manager = StageConfigManager()

    # 預期配置值（基於 305 組測試結果）
    expected_configs = {
        NovelStage.OUTLINE: {
            'temperature': 0.68,
            'top_p': 0.91,
            'repetition_penalty': 1.06,
            'max_tokens': 6000,
            'score': 90.2
        },
        NovelStage.OPENING: {
            'temperature': 0.65,
            'top_p': 0.92,
            'repetition_penalty': 1.02,
            'max_tokens': 5000,
            'cv': 3.54  # 最穩定
        },
        NovelStage.DEVELOPMENT: {
            'temperature': 0.85,
            'top_p': 0.93,
            'repetition_penalty': 1.03,
            'max_tokens': 5000
        },
        NovelStage.CLIMAX: {
            'temperature': 0.75,
            'top_p': 0.88,
            'repetition_penalty': 1.03,
            'max_tokens': 6000
        },
        NovelStage.ENDING: {
            'temperature': 0.68,
            'top_p': 0.91,
            'repetition_penalty': 1.06,
            'max_tokens': 5000
        }
    }

    all_passed = True
    for stage in NovelStage:
        config = manager.get_config(stage)
        expected = expected_configs[stage]

        # 驗證核心參數
        checks = [
            ('temperature', config.temperature, expected['temperature']),
            ('top_p', config.top_p, expected['top_p']),
            ('repetition_penalty', config.repetition_penalty, expected['repetition_penalty']),
            ('max_tokens', config.max_tokens, expected['max_tokens'])
        ]

        stage_passed = True
        for param_name, actual, expect in checks:
            if actual != expect:
                print(f"  ❌ {stage.name}.{param_name}: 期望 {expect}, 實際 {actual}")
                stage_passed = False
                all_passed = False

        if stage_passed:
            print(f"  ✅ {stage.name}: temp={config.temperature}, "
                  f"top_p={config.top_p}, penalty={config.repetition_penalty}")

    print(f"\n結果: {'✅ 全部通過' if all_passed else '❌ 有失敗項'}")
    return all_passed


def test_chapter_stage_mapping():
    """測試章節到階段的映射"""
    print("\n" + "=" * 70)
    print("📋 測試 2: 章節進度到階段映射")
    print("=" * 70)

    manager = StageConfigManager()
    total_chapters = 100  # 使用 100 章便於計算百分比

    # 預期映射
    expected_mappings = [
        # (章節範圍, 預期階段)
        ((1, 10), NovelStage.OPENING),      # 0-10%
        ((11, 80), NovelStage.DEVELOPMENT), # 10-80%
        ((81, 93), NovelStage.CLIMAX),      # 80-93%
        ((94, 100), NovelStage.ENDING)      # 93-100%
    ]

    all_passed = True
    for (start, end), expected_stage in expected_mappings:
        for chapter in [start, end]:
            _, actual_stage = manager.get_config_by_chapter(chapter, total_chapters)
            if actual_stage != expected_stage:
                print(f"  ❌ 章節 {chapter}: 期望 {expected_stage.name}, 實際 {actual_stage.name}")
                all_passed = False
            else:
                print(f"  ✅ 章節 {chapter} ({chapter}%) -> {actual_stage.name}")

    print(f"\n結果: {'✅ 全部通過' if all_passed else '❌ 有失敗項'}")
    return all_passed


def test_30_chapter_simulation():
    """模擬 30 章小說的參數變化"""
    print("\n" + "=" * 70)
    print("📋 測試 3: 30 章小說模擬")
    print("=" * 70)

    manager = StageConfigManager()
    total_chapters = 30

    # 追蹤階段變化
    stage_counts = {stage: 0 for stage in NovelStage}
    stage_chapters = {stage: [] for stage in NovelStage}

    print("\n章節配置詳情:")
    print("-" * 70)
    print(f"{'章節':^6} | {'進度':^8} | {'階段':^12} | {'temp':^6} | {'top_p':^6} | {'penalty':^7}")
    print("-" * 70)

    for chapter in range(1, total_chapters + 1):
        config, stage = manager.get_config_by_chapter(chapter, total_chapters)
        progress = chapter / total_chapters * 100

        stage_counts[stage] += 1
        stage_chapters[stage].append(chapter)

        # 只打印關鍵章節（階段轉換點）
        is_key_chapter = (
            chapter == 1 or
            chapter == total_chapters or
            chapter in [3, 4, 24, 25, 28, 29]  # 可能的轉換點
        )

        if is_key_chapter:
            print(f"  {chapter:3d}   | {progress:5.1f}%  | {stage.name:12s} | "
                  f"{config.temperature:.2f}  | {config.top_p:.2f}  | {config.repetition_penalty:.2f}")

    print("-" * 70)

    # 打印階段分佈統計
    print("\n階段分佈統計:")
    for stage in NovelStage:
        if stage == NovelStage.OUTLINE:
            continue  # 大綱階段不用於章節

        count = stage_counts[stage]
        chapters = stage_chapters[stage]
        percentage = count / total_chapters * 100

        if chapters:
            chapter_range = f"{min(chapters)}-{max(chapters)}"
        else:
            chapter_range = "無"

        print(f"  {stage.name:12s}: {count:2d} 章 ({percentage:5.1f}%) | 範圍: {chapter_range}")

    # 驗證分佈合理性
    # OPENING: 約 10% = 3 章
    # DEVELOPMENT: 約 70% = 21 章
    # CLIMAX: 約 13% = 4 章
    # ENDING: 約 7% = 2 章

    print("\n分佈驗證:")
    distribution_ok = True

    if not (2 <= stage_counts[NovelStage.OPENING] <= 4):
        print(f"  ⚠️  OPENING 章節數異常: {stage_counts[NovelStage.OPENING]}")
        distribution_ok = False
    else:
        print(f"  ✅ OPENING: {stage_counts[NovelStage.OPENING]} 章")

    if not (18 <= stage_counts[NovelStage.DEVELOPMENT] <= 23):
        print(f"  ⚠️  DEVELOPMENT 章節數異常: {stage_counts[NovelStage.DEVELOPMENT]}")
        distribution_ok = False
    else:
        print(f"  ✅ DEVELOPMENT: {stage_counts[NovelStage.DEVELOPMENT]} 章")

    if not (3 <= stage_counts[NovelStage.CLIMAX] <= 5):
        print(f"  ⚠️  CLIMAX 章節數異常: {stage_counts[NovelStage.CLIMAX]}")
        distribution_ok = False
    else:
        print(f"  ✅ CLIMAX: {stage_counts[NovelStage.CLIMAX]} 章")

    if not (1 <= stage_counts[NovelStage.ENDING] <= 3):
        print(f"  ⚠️  ENDING 章節數異常: {stage_counts[NovelStage.ENDING]}")
        distribution_ok = False
    else:
        print(f"  ✅ ENDING: {stage_counts[NovelStage.ENDING]} 章")

    print(f"\n結果: {'✅ 分佈合理' if distribution_ok else '⚠️ 分佈需調整'}")
    return distribution_ok


def test_api_client_update_params():
    """測試 API 客戶端參數更新"""
    print("\n" + "=" * 70)
    print("📋 測試 4: API 客戶端參數更新")
    print("=" * 70)

    try:
        from core.api_client import SiliconFlowClient

        # 使用假 API key 測試（不實際調用 API）
        client = SiliconFlowClient(api_key="test_key_12345")

        # 測試更新參數
        print("\n初始狀態:")
        print(f"  動態參數啟用: {client.is_dynamic_params_enabled()}")
        print(f"  當前參數: {client.get_current_params()}")

        # 更新參數
        print("\n更新參數...")
        new_params = {
            'temperature': 0.68,
            'top_p': 0.91,
            'repetition_penalty': 1.06,
            'max_tokens': 6000
        }
        client.update_params(new_params)

        print(f"  動態參數啟用: {client.is_dynamic_params_enabled()}")
        current = client.get_current_params()
        print(f"  當前參數: {current}")

        # 驗證
        all_passed = True
        for key, expected in new_params.items():
            if current.get(key) != expected:
                print(f"  ❌ {key}: 期望 {expected}, 實際 {current.get(key)}")
                all_passed = False

        # 測試重置
        print("\n重置參數...")
        client.reset_params()
        print(f"  動態參數啟用: {client.is_dynamic_params_enabled()}")
        print(f"  當前參數: {client.get_current_params()}")

        if client.get_current_params():
            print("  ❌ 重置後參數不為空")
            all_passed = False

        print(f"\n結果: {'✅ 全部通過' if all_passed else '❌ 有失敗項'}")
        return all_passed

    except ImportError as e:
        print(f"  ⚠️  無法導入 api_client: {e}")
        return False


def test_enable_disable():
    """測試啟用/禁用開關"""
    print("\n" + "=" * 70)
    print("📋 測試 5: 啟用/禁用開關")
    print("=" * 70)

    # 測試禁用狀態
    manager = StageConfigManager(enabled=False)
    print(f"\n初始化為禁用狀態: enabled={manager.is_enabled()}")

    # 禁用時應返回默認 DEVELOPMENT 配置
    config, stage = manager.get_config_by_chapter(1, 30)
    print(f"  禁用時第 1 章: 返回 {stage.name}")

    if stage != NovelStage.DEVELOPMENT:
        print("  ❌ 禁用時應返回 DEVELOPMENT 配置")
        return False

    # 啟用
    manager.enable()
    print(f"\n啟用後: enabled={manager.is_enabled()}")

    config, stage = manager.get_config_by_chapter(1, 30)
    print(f"  啟用後第 1 章: 返回 {stage.name}")

    if stage != NovelStage.OPENING:
        print("  ❌ 啟用後第 1 章應返回 OPENING 配置")
        return False

    # 再次禁用
    manager.disable()
    print(f"\n禁用後: enabled={manager.is_enabled()}")

    config, stage = manager.get_config_by_chapter(1, 30)
    print(f"  禁用後第 1 章: 返回 {stage.name}")

    if stage != NovelStage.DEVELOPMENT:
        print("  ❌ 禁用後應返回 DEVELOPMENT 配置")
        return False

    print("\n結果: ✅ 全部通過")
    return True


def test_convenience_functions():
    """測試便捷函數"""
    print("\n" + "=" * 70)
    print("📋 測試 6: 便捷函數")
    print("=" * 70)

    # 測試 get_stage_params
    print("\nget_stage_params(NovelStage.OUTLINE):")
    params = get_stage_params(NovelStage.OUTLINE)
    print(f"  {params}")

    if params['temperature'] != 0.68:
        print("  ❌ OUTLINE 溫度參數錯誤")
        return False

    # 測試 get_chapter_params
    print("\nget_chapter_params(15, 30):")  # 50% 進度，應該是 DEVELOPMENT
    params = get_chapter_params(15, 30)
    print(f"  {params}")

    if params['temperature'] != 0.85:  # DEVELOPMENT 的溫度
        print("  ❌ 章節 15/30 應使用 DEVELOPMENT 配置")
        return False

    print("\n結果: ✅ 全部通過")
    return True


def test_custom_configs():
    """測試自定義配置"""
    print("\n" + "=" * 70)
    print("📋 測試 7: 自定義配置")
    print("=" * 70)

    # 創建自定義配置
    custom_configs = {
        NovelStage.OUTLINE: StageConfig(
            temperature=0.70,
            top_p=0.90,
            repetition_penalty=1.10,
            max_tokens=8000,
            description="自定義大綱配置"
        )
    }

    manager = StageConfigManager(custom_configs=custom_configs)

    # 驗證自定義配置已應用
    config = manager.get_config(NovelStage.OUTLINE)
    print(f"\n自定義 OUTLINE 配置:")
    print(f"  temperature: {config.temperature}")
    print(f"  top_p: {config.top_p}")
    print(f"  repetition_penalty: {config.repetition_penalty}")
    print(f"  max_tokens: {config.max_tokens}")

    if config.temperature != 0.70:
        print("  ❌ 自定義配置未正確應用")
        return False

    # 驗證其他階段仍使用默認配置
    dev_config = manager.get_config(NovelStage.DEVELOPMENT)
    if dev_config.temperature != 0.85:
        print("  ❌ 其他階段配置被錯誤修改")
        return False

    print("\n結果: ✅ 全部通過")
    return True


def run_all_tests():
    """運行所有測試"""
    print("\n" + "=" * 70)
    print("🧪 動態階段參數配置系統 - 完整測試")
    print("=" * 70)

    results = []

    # 運行所有測試
    tests = [
        ("階段配置正確性", test_stage_configs),
        ("章節階段映射", test_chapter_stage_mapping),
        ("30章小說模擬", test_30_chapter_simulation),
        ("API客戶端參數更新", test_api_client_update_params),
        ("啟用/禁用開關", test_enable_disable),
        ("便捷函數", test_convenience_functions),
        ("自定義配置", test_custom_configs)
    ]

    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n❌ 測試 '{name}' 發生錯誤: {e}")
            results.append((name, False))

    # 打印總結
    print("\n" + "=" * 70)
    print("📊 測試總結")
    print("=" * 70)

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for name, passed in results:
        status = "✅ 通過" if passed else "❌ 失敗"
        print(f"  {name}: {status}")

    print("-" * 70)
    print(f"總計: {passed_count}/{total_count} 通過")

    if passed_count == total_count:
        print("\n🎉 所有測試通過!")
    else:
        print(f"\n⚠️  {total_count - passed_count} 個測試失敗")

    print("=" * 70 + "\n")

    return passed_count == total_count


def print_key_chapter_configs():
    """打印關鍵章節的配置（用於驗證）"""
    print("\n" + "=" * 70)
    print("📖 30 章小說關鍵章節配置")
    print("=" * 70)

    manager = StageConfigManager()
    total_chapters = 30

    # 關鍵章節
    key_chapters = [1, 3, 4, 10, 15, 20, 24, 25, 28, 29, 30]

    print(f"\n{'章節':^6} | {'進度':^8} | {'階段':^12} | {'temp':^6} | {'top_p':^6} | {'penalty':^7} | {'max_tokens':^10}")
    print("-" * 80)

    for chapter in key_chapters:
        config, stage = manager.get_config_by_chapter(chapter, total_chapters)
        progress = chapter / total_chapters * 100

        print(f"  {chapter:3d}   | {progress:5.1f}%  | {stage.name:12s} | "
              f"{config.temperature:.2f}  | {config.top_p:.2f}  | {config.repetition_penalty:.2f}   | "
              f"{config.max_tokens:5d}")

    print("-" * 80)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='動態階段參數配置系統測試')
    parser.add_argument('--full', action='store_true', help='運行完整測試')
    parser.add_argument('--quick', action='store_true', help='快速測試（只打印配置）')
    parser.add_argument('--verbose', '-v', action='store_true', help='詳細輸出')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.quick:
        # 快速模式：只打印配置
        manager = StageConfigManager()
        manager.print_all_configs()
        print_key_chapter_configs()
    else:
        # 完整測試
        success = run_all_tests()

        # 額外打印配置信息
        print_key_chapter_configs()

        # 返回退出碼
        sys.exit(0 if success else 1)
