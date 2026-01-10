# -*- coding: utf-8 -*-
"""
AI 小說自動生成器 - CLI 主程式
"""

import os
import sys
import argparse
from dotenv import load_dotenv

from core.generator import NovelGenerator
from config import MODEL_ROLES


def print_banner():
    """打印歡迎橫幅"""
    banner = """
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║       AI 小說自動生成器 - Phase 2.1 增強版                ║
║       🤖 三模型智能協作系統                               ║
║       📋 GLM-4 (大綱+寫作) + 🔍 Qwen Coder (編輯)         ║
║       ✨ 分卷管理 + 反模式引擎                             ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""
    print(banner)
    print("\n🤖 智能模型分工（緊急修復版）:")
    print(f"  📋 總編劇: GLM-4 - 負責大綱規劃（中文能力極強）")
    print(f"  ✍️  作家: GLM-4 - 負責章節創作與敘事")
    print(f"  🔍 編輯: Qwen Coder - 負責品質檢查\n")


def get_user_input():
    """互動式獲取使用者輸入"""
    print("\n請輸入小說基本信息：\n")

    title = input("📚 小說標題: ").strip()
    if not title:
        print("❌ 標題不能為空")
        sys.exit(1)

    genre = input("🏷️  小說類型（如：科幻、武俠、言情等）: ").strip()
    if not genre:
        genre = "小說"

    theme = input("💡 核心主題（如：人工智能覺醒、武林爭霸等）: ").strip()
    if not theme:
        theme = "未設定"

    while True:
        total_chapters_str = input("📖 總章節數（建議 5-30 章）: ").strip()
        try:
            total_chapters = int(total_chapters_str)
            if total_chapters <= 0:
                print("❌ 章節數必須大於 0")
                continue
            if total_chapters > 100:
                confirm = input(f"⚠️  您要生成 {total_chapters} 章，這可能需要很長時間。確定? [y/N]: ")
                if confirm.lower() != 'y':
                    continue
            break
        except ValueError:
            print("❌ 請輸入有效的數字")

    return {
        'title': title,
        'genre': genre,
        'theme': theme,
        'total_chapters': total_chapters
    }


def ask_enable_phase2():
    """詢問是否啟用 Phase 2.1 功能"""
    print("\n" + "="*60)
    print("🚀 Phase 2.1 增強功能")
    print("="*60)
    print("Phase 2.1 包含以下功能:")
    print("  📚 分卷管理系統 - 自動規劃卷結構")
    print("  🎭 劇情節奏控制 - 智能衝突升級曲線")
    print("  ✓ 大綱驗證器 - 防止情節重複")
    print("  👥 角色弧光強制器 - 保證角色成長")
    print("  🔗 事件依賴圖 - 檢測情節漏洞")
    print()
    print("建議:")
    print("  • 10 章以下 → 可以不啟用（MVP 模式更快）")
    print("  • 10-30 章 → 建議啟用")
    print("  • 30 章以上 → 強烈建議啟用")
    print("="*60)

    while True:
        choice = input("\n是否啟用 Phase 2.1 功能? [Y/n]: ").strip().lower()
        if choice in ['', 'y', 'yes']:
            print("✓ 已啟用 Phase 2.1 增強功能\n")
            return True
        elif choice in ['n', 'no']:
            print("✓ 使用 MVP 模式（更快速但功能較少）\n")
            return False
        else:
            print("❌ 請輸入 Y 或 N")


def test_api_connection(api_key: str, model: str = None):
    """測試 API 連接"""
    print("\n⏳ 測試 API 連接...")

    try:
        from core.api_client import SiliconFlowClient
        client = SiliconFlowClient(api_key, model)

        result = client.generate("請用一句話介紹你自己。", max_tokens=100)

        print("✓ API 連接成功")
        print(f"  模型回應: {result[:50]}...")
        print()
        return True

    except Exception as e:
        print(f"❌ API 連接失敗: {e}\n")
        return False


def main():
    """主程式"""
    # 載入環境變數
    load_dotenv()

    # 命令列參數解析
    parser = argparse.ArgumentParser(description='AI 小說自動生成器')
    parser.add_argument('--test-api', action='store_true', help='測試 API 連接')
    parser.add_argument('--model', type=str, help='指定模型')
    parser.add_argument('--chapters', type=int, help='章節數')
    parser.add_argument('--api-key', type=str, help='API Key（也可透過環境變數設定）')

    args = parser.parse_args()

    # 打印橫幅
    print_banner()

    # 獲取 API Key
    api_key = args.api_key or os.getenv('SILICONFLOW_API_KEY')

    if not api_key:
        print("❌ 錯誤: 未設定 API Key\n")
        print("請使用以下方式之一設定 API Key:")
        print("1. 複製 .env.example 為 .env 並填入 API Key")
        print("2. 設定環境變數: export SILICONFLOW_API_KEY=your_key")
        print("3. 使用命令列參數: --api-key your_key\n")
        sys.exit(1)

    # 測試 API 模式
    if args.test_api:
        test_api_connection(api_key, args.model)
        return

    # 獲取使用者輸入
    user_input = get_user_input()

    # 詢問是否啟用 Phase 2.1
    enable_phase2 = ask_enable_phase2()

    # 確認信息
    print("\n" + "="*60)
    print("📝 專案信息確認")
    print("="*60)
    print(f"標題: {user_input['title']}")
    print(f"類型: {user_input['genre']}")
    print(f"主題: {user_input['theme']}")
    print(f"章節數: {user_input['total_chapters']}")
    print(f"模型協作: 三模型智能分工")
    print(f"  📋 DeepSeek R1 → 大綱規劃")
    print(f"  ✍️  GLM-4 → 章節創作")
    print(f"模式: {'Phase 2.1 增強版' if enable_phase2 else 'MVP 基礎版'}")
    print("="*60)

    confirm = input("\n確認開始生成? [Y/n]: ")
    if confirm.lower() == 'n':
        print("已取消")
        return

    try:
        # 初始化生成器（使用 Architect 模型作為主模型）
        print("\n⏳ 初始化生成器...")
        generator = NovelGenerator(api_key, MODEL_ROLES['architect'], enable_phase2=enable_phase2)

        # 建立專案
        generator.create_project(
            title=user_input['title'],
            genre=user_input['genre'],
            theme=user_input['theme'],
            total_chapters=user_input['total_chapters']
        )

        # 生成大綱
        print("📋 步驟 1/3: 生成故事大綱")
        print("─"*60)
        generator.generate_outline()

        # 顯示大綱預覽
        print("大綱預覽:")
        print("─"*60)
        print(generator.outline[:500])
        if len(generator.outline) > 500:
            print("...")
        print("─"*60)

        # 確認是否繼續
        confirm = input("\n大綱生成完成，是否繼續生成章節? [Y/n]: ")
        if confirm.lower() == 'n':
            print("\n已儲存大綱，您可以稍後繼續")
            print(f"專案目錄: {generator.project_dir}")
            return

        # 生成所有章節
        print("\n📖 步驟 2/3: 生成章節內容")
        print("─"*60)
        generator.generate_all_chapters()

        # 合併章節
        print("📚 步驟 3/3: 合併完整小說")
        print("─"*60)
        generator.merge_chapters()

        # 最終統計
        stats = generator.get_statistics()

        print("\n" + "="*60)
        print("🎉 小說生成完成！")
        print("="*60)
        print(f"專案目錄: {stats['project_dir']}")
        print(f"已生成章節: {stats['chapters_generated']}/{stats['total_chapters']}")
        print(f"總字數: {stats['total_words']:,}")
        print(f"總成本: ¥{stats['api_statistics']['total_cost']:.4f}")

        # Phase 2.1 額外統計
        if 'phase2_stats' in stats:
            p2_stats = stats['phase2_stats']
            print(f"\n📚 分卷信息:")
            print(f"  總卷數: {p2_stats.get('total_volumes', 0)}")
            print(f"  當前卷: {p2_stats.get('current_volume', 1)}")
            print(f"  大綱驗證: {'✓ 已啟用' if p2_stats.get('validation_enabled') else '未啟用'}")

        print("="*60)

        print("\n生成的文件:")
        print(f"  📋 大綱: outline.txt")
        if enable_phase2 and 'phase2_stats' in stats:
            print(f"  📚 分卷規劃: volume_plan.json")
            print(f"  📖 卷大綱: volumes/volume_N/outline.txt")
        print(f"  📄 章節: chapter_001.txt ~ chapter_{stats['total_chapters']:03d}.txt")
        if enable_phase2:
            print(f"  📊 章節元數據: chapter_NNN_metadata.json")
        print(f"  📚 完整小說: full_novel.txt")
        print(f"  ℹ️  元數據: metadata.json")

        print(f"\n✨ 請到 {stats['project_dir']} 查看您的小說！\n")

    except KeyboardInterrupt:
        print("\n\n⚠️  使用者中斷操作")
        if 'generator' in locals():
            print(f"專案已部分完成，儲存於: {generator.project_dir}")
        sys.exit(0)

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
