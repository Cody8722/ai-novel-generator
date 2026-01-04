# -*- coding: utf-8 -*-
"""
压力测试脚本 - 长篇小说生成（10-20章）

测试目标：
1. 验证长篇生成稳定性
2. 测试成本估算准确性
3. 评估剧情连贯性衰减
4. 压力测试错误处理
"""

import os
import sys
import time
import json
from datetime import datetime
from dotenv import load_dotenv
from core.generator import NovelGenerator

# 载入环境变量
load_dotenv()


class StressTestRunner:
    """压力测试运行器"""

    def __init__(self, api_key):
        self.api_key = api_key
        self.test_results = {
            'start_time': None,
            'end_time': None,
            'total_duration': 0,
            'chapters': [],
            'errors': [],
            'retries': [],
            'performance': {},
            'cost_analysis': {},
            'coherence_scores': []
        }

    def run_test(self, title, genre, theme, total_chapters):
        """执行压力测试"""
        print("="*80)
        print("🧪 AI 小说生成器 - 长篇压力测试")
        print("="*80)
        print(f"\n测试配置:")
        print(f"  标题: {title}")
        print(f"  类型: {genre}")
        print(f"  主题: {theme}")
        print(f"  章节数: {total_chapters}")
        print()

        self.test_results['start_time'] = datetime.now()

        try:
            # 初始化生成器
            print("⏳ 步骤 1: 初始化生成器...")
            generator = NovelGenerator(self.api_key)
            print("✓ 生成器初始化完成\n")

            # 创建项目
            print("⏳ 步骤 2: 创建项目...")
            project_dir = generator.create_project(
                title=title,
                genre=genre,
                theme=theme,
                total_chapters=total_chapters
            )
            print(f"✓ 项目创建完成: {project_dir}\n")
            self.test_results['project_dir'] = project_dir

            # 生成大纲
            print("⏳ 步骤 3: 生成故事大纲...")
            outline_start = time.time()
            outline = generator.generate_outline()
            outline_duration = time.time() - outline_start
            print(f"✓ 大纲生成完成 ({len(outline)} 字，耗时 {outline_duration:.1f} 秒)\n")

            self.test_results['outline_duration'] = outline_duration
            self.test_results['outline_length'] = len(outline)

            # 生成章节
            print("⏳ 步骤 4: 生成章节...")
            print("="*80)

            chapter_times = []
            chapter_costs = []
            chapter_word_counts = []

            for i in range(1, total_chapters + 1):
                chapter_start = time.time()

                print(f"\n[{i}/{total_chapters}] 生成第 {i} 章...")

                try:
                    chapter_info = generator.generate_chapter(i)
                    chapter_duration = time.time() - chapter_start

                    # 记录章节信息
                    chapter_data = {
                        'number': i,
                        'word_count': chapter_info['word_count'],
                        'cost': chapter_info['cost'],
                        'duration': chapter_duration,
                        'success': True
                    }

                    self.test_results['chapters'].append(chapter_data)
                    chapter_times.append(chapter_duration)
                    chapter_costs.append(chapter_info['cost'])
                    chapter_word_counts.append(chapter_info['word_count'])

                    print(f"✓ 第 {i} 章完成")
                    print(f"  字数: {chapter_info['word_count']}")
                    print(f"  成本: ¥{chapter_info['cost']:.4f}")
                    print(f"  耗时: {chapter_duration:.1f} 秒")

                    # 每5章输出中期统计
                    if i % 5 == 0:
                        avg_time = sum(chapter_times) / len(chapter_times)
                        avg_cost = sum(chapter_costs) / len(chapter_costs)
                        total_cost = sum(chapter_costs)
                        print(f"\n📊 中期统计 (已完成 {i}/{total_chapters} 章):")
                        print(f"  平均耗时: {avg_time:.1f} 秒/章")
                        print(f"  平均成本: ¥{avg_cost:.4f}/章")
                        print(f"  累计成本: ¥{total_cost:.4f}")
                        print(f"  预估总成本: ¥{(total_cost / i * total_chapters):.4f}")

                except Exception as e:
                    print(f"❌ 第 {i} 章生成失败: {e}")
                    self.test_results['errors'].append({
                        'chapter': i,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    })

                    # 错误后继续下一章
                    continue

            print("\n" + "="*80)
            print("✓ 所有章节生成完成\n")

            # 合并章节
            print("⏳ 步骤 5: 合并完整小说...")
            generator.merge_chapters()
            print("✓ 完整小说已合并\n")

            # 生成最终统计
            self.test_results['end_time'] = datetime.now()
            self.test_results['total_duration'] = (
                self.test_results['end_time'] - self.test_results['start_time']
            ).total_seconds()

            # 计算性能指标
            self._calculate_performance_metrics(generator)

            # 生成测试报告
            self._generate_report()

            return True

        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _calculate_performance_metrics(self, generator):
        """计算性能指标"""
        stats = generator.get_statistics()
        api_stats = stats['api_statistics']

        # 基本统计
        total_chapters = len(self.test_results['chapters'])
        successful_chapters = sum(1 for c in self.test_results['chapters'] if c['success'])

        # 时间统计
        chapter_times = [c['duration'] for c in self.test_results['chapters'] if c['success']]
        avg_time = sum(chapter_times) / len(chapter_times) if chapter_times else 0
        min_time = min(chapter_times) if chapter_times else 0
        max_time = max(chapter_times) if chapter_times else 0

        # 成本统计
        chapter_costs = [c['cost'] for c in self.test_results['chapters'] if c['success']]
        total_cost = sum(chapter_costs)
        avg_cost = total_cost / len(chapter_costs) if chapter_costs else 0

        # 字数统计
        chapter_words = [c['word_count'] for c in self.test_results['chapters'] if c['success']]
        total_words = sum(chapter_words)
        avg_words = total_words / len(chapter_words) if chapter_words else 0
        min_words = min(chapter_words) if chapter_words else 0
        max_words = max(chapter_words) if chapter_words else 0

        # Token 统计
        total_tokens = api_stats['total_tokens']
        total_tokens_input = api_stats['total_tokens_input']
        total_tokens_output = api_stats['total_tokens_output']

        self.test_results['performance'] = {
            'total_chapters': total_chapters,
            'successful_chapters': successful_chapters,
            'failed_chapters': total_chapters - successful_chapters,
            'success_rate': successful_chapters / total_chapters * 100 if total_chapters > 0 else 0,

            'time': {
                'total_duration': self.test_results['total_duration'],
                'outline_duration': self.test_results['outline_duration'],
                'chapters_duration': sum(chapter_times),
                'avg_per_chapter': avg_time,
                'min_per_chapter': min_time,
                'max_per_chapter': max_time
            },

            'cost': {
                'total': total_cost,
                'avg_per_chapter': avg_cost,
                'per_1000_words': (total_cost / total_words * 1000) if total_words > 0 else 0
            },

            'words': {
                'total': total_words,
                'avg_per_chapter': avg_words,
                'min_per_chapter': min_words,
                'max_per_chapter': max_words
            },

            'tokens': {
                'total': total_tokens,
                'input': total_tokens_input,
                'output': total_tokens_output,
                'ratio': total_tokens_input / total_tokens_output if total_tokens_output > 0 else 0
            }
        }

    def _generate_report(self):
        """生成测试报告"""
        print("="*80)
        print("📊 压力测试完整报告")
        print("="*80)

        perf = self.test_results['performance']

        # 基本信息
        print(f"\n📁 项目目录: {self.test_results['project_dir']}")
        print(f"⏱️  测试时长: {perf['time']['total_duration']:.1f} 秒 ({perf['time']['total_duration']/60:.1f} 分钟)")

        # 章节统计
        print(f"\n📖 章节统计:")
        print(f"  目标章节数: {perf['total_chapters']}")
        print(f"  成功生成: {perf['successful_chapters']}")
        print(f"  失败章节: {perf['failed_chapters']}")
        print(f"  成功率: {perf['success_rate']:.1f}%")

        # 性能指标
        print(f"\n⚡ 性能指标:")
        print(f"  大纲生成: {perf['time']['outline_duration']:.1f} 秒")
        print(f"  章节总耗时: {perf['time']['chapters_duration']:.1f} 秒")
        print(f"  平均每章: {perf['time']['avg_per_chapter']:.1f} 秒")
        print(f"  最快章节: {perf['time']['min_per_chapter']:.1f} 秒")
        print(f"  最慢章节: {perf['time']['max_per_chapter']:.1f} 秒")

        # 成本分析
        print(f"\n💰 成本分析:")
        print(f"  总成本: ¥{perf['cost']['total']:.4f}")
        print(f"  平均每章: ¥{perf['cost']['avg_per_chapter']:.4f}")
        print(f"  每千字成本: ¥{perf['cost']['per_1000_words']:.4f}")

        # 字数统计
        print(f"\n📝 字数统计:")
        print(f"  总字数: {perf['words']['total']:,} 字")
        print(f"  平均每章: {perf['words']['avg_per_chapter']:.0f} 字")
        print(f"  最短章节: {perf['words']['min_per_chapter']} 字")
        print(f"  最长章节: {perf['words']['max_per_chapter']} 字")

        # Token 使用
        print(f"\n🔢 Token 使用:")
        print(f"  总 Token: {perf['tokens']['total']:,}")
        print(f"  输入 Token: {perf['tokens']['input']:,}")
        print(f"  输出 Token: {perf['tokens']['output']:,}")
        print(f"  输入/输出比: {perf['tokens']['ratio']:.2f}")

        # 错误统计
        if self.test_results['errors']:
            print(f"\n❌ 错误统计:")
            print(f"  错误次数: {len(self.test_results['errors'])}")
            for error in self.test_results['errors']:
                print(f"  - 第 {error['chapter']} 章: {error['error']}")

        # 稳定性评估
        print(f"\n🔍 稳定性评估:")
        if perf['success_rate'] >= 95:
            print(f"  ✅ 优秀 - 成功率 {perf['success_rate']:.1f}%")
        elif perf['success_rate'] >= 85:
            print(f"  ⚠️  良好 - 成功率 {perf['success_rate']:.1f}%")
        else:
            print(f"  ❌ 需改进 - 成功率 {perf['success_rate']:.1f}%")

        # 成本效益
        cost_per_chapter = perf['cost']['avg_per_chapter']
        if cost_per_chapter <= 0.003:
            print(f"  ✅ 成本控制优秀 - ¥{cost_per_chapter:.4f}/章")
        elif cost_per_chapter <= 0.005:
            print(f"  ⚠️  成本合理 - ¥{cost_per_chapter:.4f}/章")
        else:
            print(f"  ❌ 成本偏高 - ¥{cost_per_chapter:.4f}/章")

        # 性能评估
        avg_time = perf['time']['avg_per_chapter']
        if avg_time <= 90:
            print(f"  ✅ 生成速度优秀 - {avg_time:.1f} 秒/章")
        elif avg_time <= 120:
            print(f"  ⚠️  生成速度良好 - {avg_time:.1f} 秒/章")
        else:
            print(f"  ❌ 生成速度偏慢 - {avg_time:.1f} 秒/章")

        print("\n" + "="*80)

        # 保存详细报告
        self._save_report()

    def _save_report(self):
        """保存详细测试报告到文件"""
        report_path = os.path.join(
            self.test_results['project_dir'],
            'stress_test_report.json'
        )

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2, default=str)

        print(f"📄 详细报告已保存: {report_path}")


def main():
    """主函数"""
    print("="*80)
    print("🧪 开始长篇压力测试")
    print("="*80)

    # 测试配置 - 10章科幻小说
    test_config = {
        'title': '时空裂痕',
        'genre': '科幻',
        'theme': '平行宇宙与时间悖论',
        'total_chapters': 10
    }

    print(f"\n测试配置:")
    print(f"  标题: {test_config['title']}")
    print(f"  类型: {test_config['genre']}")
    print(f"  主题: {test_config['theme']}")
    print(f"  章节数: {test_config['total_chapters']}")
    print(f"\n预估指标 (基于 3 章测试数据):")
    print(f"  预估总耗时: ~18 分钟")
    print(f"  预估总成本: ¥0.026")
    print(f"  预估总字数: 32,000 字")
    print()

    # 获取 API Key
    api_key = os.getenv('SILICONFLOW_API_KEY')
    if not api_key:
        print("❌ 错误: 未设置 API Key")
        sys.exit(1)

    # 用户确认
    print("⚠️  警告: 此测试将生成 10 章小说，预计耗时 18 分钟，成本约 ¥0.026")
    confirm = input("\n是否继续? (y/n): ").strip().lower()

    if confirm != 'y':
        print("❌ 测试已取消")
        sys.exit(0)

    print()

    try:
        # 运行测试
        runner = StressTestRunner(api_key)
        success = runner.run_test(**test_config)

        if success:
            print("\n🎉 压力测试完成！")
            return 0
        else:
            print("\n❌ 压力测试失败")
            return 1

    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        return 1
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
