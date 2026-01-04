# -*- coding: utf-8 -*-
"""
AI 小說自動生成器 - CLI 主程式
"""

import os
import sys
import argparse
from dotenv import load_dotenv

from core.generator import NovelGenerator
from config import MODELS


def print_banner():
    """打印歡迎橫幅"""
    banner = """
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║       AI 小說自動生成器 - MVP 版本                        ║
║       Powered by 矽基流動 + Qwen2.5                      ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""
    print(banner)


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


def select_model():
    """讓使用者選擇模型"""
    print("\n請選擇模型：\n")

    models_list = list(MODELS.items())
    for i, (model_id, model_info) in enumerate(models_list, 1):
        print(f"{i}. {model_info['name']}")
        print(f"   {model_info['description']}")
        print(f"   價格: 輸入/輸出 {model_info['price_input']*1000:.2f}/千tokens\n")

    while True:
        choice = input(f"請選擇模型 [1-{len(models_list)}]（直接回車使用預設）: ").strip()

        if not choice:
            return None  # 使用預設模型

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(models_list):
                selected_model = models_list[idx][0]
                print(f"✓ 已選擇: {MODELS[selected_model]['name']}\n")
                return selected_model
            else:
                print(f"❌ 請輸入 1-{len(models_list)} 之間的數字")
        except ValueError:
            print("❌ 請輸入有效的數字")


def test_api_connection(api_key: str, model: str = None):
    """測試 API 連接"""
    print("\n⏳ 測試 API 連接...")

    try:
        from core.api_client import SiliconFlowClient
        client = SiliconFlowClient(api_key, model)

        result = client.generate("請用一句話介紹你自己。", max_tokens=100)

        print("✓ API 連接成功")
        print(f"  模型回應: {result['content'][:50]}...")
        print(f"  Token 使用: {result['tokens_input']} + {result['tokens_output']}")
        print(f"  成本: ¥{result['cost']:.4f}\n")
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

    # 選擇模型
    if args.model:
        selected_model = args.model
    else:
        selected_model = select_model()

    # 獲取使用者輸入
    user_input = get_user_input()

    # 確認信息
    print("\n" + "="*60)
    print("📝 專案信息確認")
    print("="*60)
    print(f"標題: {user_input['title']}")
    print(f"類型: {user_input['genre']}")
    print(f"主題: {user_input['theme']}")
    print(f"章節數: {user_input['total_chapters']}")
    if selected_model:
        print(f"模型: {MODELS[selected_model]['name']}")
    else:
        print(f"模型: 預設 (Qwen2.5-7B)")
    print("="*60)

    confirm = input("\n確認開始生成? [Y/n]: ")
    if confirm.lower() == 'n':
        print("已取消")
        return

    try:
        # 初始化生成器
        print("\n⏳ 初始化生成器...")
        generator = NovelGenerator(api_key, selected_model)

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
        print("="*60)

        print("\n生成的文件:")
        print(f"  📋 大綱: outline.txt")
        print(f"  📖 章節: chapter_001.txt ~ chapter_{stats['total_chapters']:03d}.txt")
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
