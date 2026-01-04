# -*- coding: utf-8 -*-
"""
自動化測試腳本 - 生成 3 章測試小說
"""

import os
import sys
from dotenv import load_dotenv
from core.generator import NovelGenerator

# 載入環境變數
load_dotenv()

def main():
    print("="*60)
    print("🧪 開始自動化測試：生成 3 章測試小說")
    print("="*60)

    # 測試參數
    test_config = {
        'title': '星際邊緣',
        'genre': '科幻',
        'theme': '人類文明存續',
        'total_chapters': 3
    }

    print(f"\n測試配置:")
    print(f"  標題: {test_config['title']}")
    print(f"  類型: {test_config['genre']}")
    print(f"  主題: {test_config['theme']}")
    print(f"  章節數: {test_config['total_chapters']}")
    print()

    # 獲取 API Key
    api_key = os.getenv('SILICONFLOW_API_KEY')
    if not api_key:
        print("❌ 錯誤: 未設定 API Key")
        sys.exit(1)

    try:
        # 初始化生成器
        print("⏳ 步驟 1: 初始化生成器...")
        generator = NovelGenerator(api_key)
        print("✓ 生成器初始化完成\n")

        # 建立專案
        print("⏳ 步驟 2: 建立專案...")
        project_dir = generator.create_project(
            title=test_config['title'],
            genre=test_config['genre'],
            theme=test_config['theme'],
            total_chapters=test_config['total_chapters']
        )
        print(f"✓ 專案建立完成: {project_dir}\n")

        # 生成大綱
        print("⏳ 步驟 3: 生成故事大綱...")
        print("─"*60)
        outline = generator.generate_outline()
        print("\n大綱預覽（前 500 字）:")
        print("─"*60)
        print(outline[:500])
        if len(outline) > 500:
            print("...\n")
        print("─"*60)
        print(f"✓ 大綱生成完成（{len(outline)} 字）\n")

        # 生成章節
        print("⏳ 步驟 4: 生成章節...")
        print("─"*60)

        for i in range(1, test_config['total_chapters'] + 1):
            print(f"\n[{i}/{test_config['total_chapters']}] 生成第 {i} 章...")
            chapter_info = generator.generate_chapter(i)
            print(f"✓ 第 {i} 章完成")
            print(f"  字數: {chapter_info['word_count']}")
            print(f"  成本: ¥{chapter_info['cost']:.4f}")

        print("\n" + "─"*60)
        print("✓ 所有章節生成完成\n")

        # 合併章節
        print("⏳ 步驟 5: 合併完整小說...")
        generator.merge_chapters()
        print("✓ 完整小說已合併\n")

        # 統計信息
        stats = generator.get_statistics()
        api_stats = stats['api_statistics']

        print("="*60)
        print("📊 測試結果統計")
        print("="*60)
        print(f"專案目錄............ {stats['project_dir']}")
        print(f"已生成章節.......... {stats['chapters_generated']}/{stats['total_chapters']}")
        print(f"總字數.............. {stats['total_words']:,} 字")
        print(f"總 Token 使用........ {api_stats['total_tokens']:,}")
        print(f"  ├─ 輸入........... {api_stats['total_tokens_input']:,}")
        print(f"  └─ 輸出........... {api_stats['total_tokens_output']:,}")
        print(f"總成本.............. ¥{api_stats['total_cost']:.4f}")
        print(f"平均每章成本........ ¥{api_stats['avg_cost_per_request']:.4f}")
        print("="*60)

        # 驗證結果
        print("\n🔍 驗證測試結果:")
        print("─"*60)

        success = True

        # 驗證 1: 章節數
        if stats['chapters_generated'] == test_config['total_chapters']:
            print(f"✅ 章節數量正確: {stats['chapters_generated']}/{test_config['total_chapters']}")
        else:
            print(f"❌ 章節數量錯誤: {stats['chapters_generated']}/{test_config['total_chapters']}")
            success = False

        # 驗證 2: 平均字數
        avg_words = stats['total_words'] / stats['chapters_generated']
        if 2500 <= avg_words <= 3500:
            print(f"✅ 平均字數符合預期: {avg_words:.0f} 字/章 (目標: 2500-3500)")
        else:
            print(f"⚠️  平均字數偏離: {avg_words:.0f} 字/章 (目標: 2500-3500)")

        # 驗證 3: 成本
        expected_cost_min = 0.007
        expected_cost_max = 0.012
        if expected_cost_min <= api_stats['total_cost'] <= expected_cost_max:
            print(f"✅ 總成本符合預期: ¥{api_stats['total_cost']:.4f} (預期: ¥{expected_cost_min}-¥{expected_cost_max})")
        else:
            print(f"⚠️  總成本偏離預期: ¥{api_stats['total_cost']:.4f} (預期: ¥{expected_cost_min}-¥{expected_cost_max})")

        # 驗證 4: 檔案結構
        required_files = [
            'metadata.json',
            'outline.txt',
            'chapter_001.txt',
            'chapter_002.txt',
            'chapter_003.txt',
            'full_novel.txt'
        ]

        all_files_exist = True
        for filename in required_files:
            filepath = os.path.join(project_dir, filename)
            if os.path.exists(filepath):
                print(f"✅ 檔案存在: {filename}")
            else:
                print(f"❌ 檔案缺失: {filename}")
                all_files_exist = False
                success = False

        print("─"*60)

        if success and all_files_exist:
            print("\n🎉 測試完全成功！")
            print(f"\n📁 生成的小說位於: {project_dir}")
            print("   您可以查看以下檔案:")
            print("   - outline.txt (故事大綱)")
            print("   - chapter_001.txt ~ chapter_003.txt (各章節)")
            print("   - full_novel.txt (完整小說)")
        else:
            print("\n⚠️  測試完成，但有部分問題")

        return 0

    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
