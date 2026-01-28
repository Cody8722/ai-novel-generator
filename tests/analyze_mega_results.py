#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
超大規模測試結果分析系統

功能：
1. 加載所有批次測試結果
2. 分析參數影響和趨勢
3. 找出最佳參數組合
4. 生成詳細分析報告
5. 提供優化建議

使用方法：
    # 生成完整分析報告
    python tests/analyze_mega_results.py

    # 只分析特定階段
    python tests/analyze_mega_results.py --stage coarse
    python tests/analyze_mega_results.py --stage fine
    python tests/analyze_mega_results.py --stage validation

    # 生成可視化圖表（如果安裝了 matplotlib）
    python tests/analyze_mega_results.py --visualize
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import logging
import argparse
from datetime import datetime
from typing import Dict, List
from collections import defaultdict

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MegaResultsAnalyzer:
    """超大規模測試結果分析器"""

    def __init__(self, results_dir: Path = None):
        """
        初始化分析器

        Args:
            results_dir: 結果目錄路徑
        """
        if results_dir is None:
            results_dir = Path(__file__).parent.parent / "test_results" / "mega_test"

        self.results_dir = results_dir
        self.all_results = []
        self.report = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': 0,
            'successful_tests': 0,
            'failed_tests': 0,
            'stages': {},
            'parameters': {},
            'best_params': {},
            'recommendations': []
        }

    def load_results(self) -> bool:
        """
        加載所有批次結果

        Returns:
            是否成功加載
        """
        logger.info("📂 加載測試結果...")

        if not self.results_dir.exists():
            logger.error(f"❌ 結果目錄不存在: {self.results_dir}")
            return False

        # 查找所有批次結果文件
        batch_files = sorted(self.results_dir.glob("batch_*_results.json"))

        if not batch_files:
            logger.error(f"❌ 找不到批次結果文件: {self.results_dir}")
            return False

        logger.info(f"找到 {len(batch_files)} 個批次結果文件")

        # 加載所有結果
        for batch_file in batch_files:
            try:
                with open(batch_file, 'r', encoding='utf-8') as f:
                    batch_results = json.load(f)
                    self.all_results.extend(batch_results)
                    logger.info(f"  ✅ {batch_file.name}: {len(batch_results)} 組")
            except Exception as e:
                logger.error(f"  ❌ {batch_file.name}: {e}")
                continue

        # 統計
        self.report['total_tests'] = len(self.all_results)
        self.report['successful_tests'] = sum(1 for r in self.all_results if r.get('success', False))
        self.report['failed_tests'] = self.report['total_tests'] - self.report['successful_tests']

        logger.info(f"\n✅ 成功加載 {self.report['total_tests']} 組測試結果")
        logger.info(f"   成功: {self.report['successful_tests']}")
        logger.info(f"   失敗: {self.report['failed_tests']}\n")

        return True

    def analyze_by_stage(self):
        """按階段分析"""
        logger.info("📊 按階段分析...\n")

        # 按階段分組
        stages = defaultdict(list)
        for result in self.all_results:
            if result.get('success', False):
                stage = result.get('stage', 'unknown')
                stages[stage].append(result)

        # 分析每個階段
        for stage, results in stages.items():
            logger.info(f"  階段: {stage}")
            logger.info(f"    測試數: {len(results)}")

            if results:
                scores = [r['score']['total_score'] for r in results]
                avg_score = sum(scores) / len(scores)
                max_score = max(scores)
                min_score = min(scores)

                logger.info(f"    平均分: {avg_score:.1f}/120")
                logger.info(f"    最高分: {max_score:.0f}/120")
                logger.info(f"    最低分: {min_score:.0f}/120")

                # 找出該階段最佳參數
                best_result = max(results, key=lambda r: r['score']['total_score'])
                logger.info(f"    最佳參數: {best_result['params']}")

                self.report['stages'][stage] = {
                    'test_count': len(results),
                    'avg_score': avg_score,
                    'max_score': max_score,
                    'min_score': min_score,
                    'best_params': best_result['params'],
                    'best_score': best_result['score']['total_score']
                }

            logger.info("")

    def analyze_by_parameter(self):
        """按參數分析"""
        logger.info("📊 按參數分析...\n")

        # 只分析成功的結果
        successful_results = [r for r in self.all_results if r.get('success', False)]

        # Temperature 分析
        self._analyze_single_param('temperature', successful_results)

        # Top_P 分析
        self._analyze_single_param('top_p', successful_results)

        # Repetition Penalty 分析
        self._analyze_single_param('repetition_penalty', successful_results)

        # Max Tokens 分析
        self._analyze_single_param('max_tokens', successful_results)

    def _analyze_single_param(self, param_name: str, results: List[Dict]):
        """
        分析單個參數

        Args:
            param_name: 參數名稱
            results: 測試結果列表
        """
        logger.info(f"  參數: {param_name}")

        # 按參數值分組
        param_groups = defaultdict(list)
        for result in results:
            param_value = result['params'].get(param_name)
            if param_value is not None:
                param_groups[param_value].append(result['score']['total_score'])

        if not param_groups:
            logger.info(f"    無數據\n")
            return

        # 計算每個值的平均分
        param_stats = {}
        for value, scores in param_groups.items():
            avg_score = sum(scores) / len(scores)
            param_stats[value] = {
                'avg_score': avg_score,
                'count': len(scores),
                'min_score': min(scores),
                'max_score': max(scores)
            }

        # 排序並顯示前 5 個最佳值
        sorted_values = sorted(param_stats.items(), key=lambda x: x[1]['avg_score'], reverse=True)

        logger.info(f"    Top 5 值:")
        for i, (value, stats) in enumerate(sorted_values[:5], 1):
            logger.info(f"      {i}. {value}: {stats['avg_score']:.1f}/120 (n={stats['count']})")

        # 保存到報告
        self.report['parameters'][param_name] = {
            'best_value': sorted_values[0][0],
            'best_avg_score': sorted_values[0][1]['avg_score'],
            'all_values': dict(sorted_values)
        }

        logger.info("")

    def find_best_combinations(self, top_n: int = 10):
        """
        找出最佳參數組合

        Args:
            top_n: 返回前 N 個最佳組合
        """
        logger.info(f"🏆 尋找最佳參數組合 (Top {top_n})...\n")

        # 只分析成功的結果
        successful_results = [r for r in self.all_results if r.get('success', False)]

        if not successful_results:
            logger.warning("  無成功的測試結果\n")
            return

        # 按分數排序
        sorted_results = sorted(successful_results, key=lambda r: r['score']['total_score'], reverse=True)

        # 顯示前 N 個
        logger.info(f"  排名  分數    Temperature  Top_P  Penalty  Tokens  階段")
        logger.info("  " + "-" * 70)

        best_combinations = []
        for i, result in enumerate(sorted_results[:top_n], 1):
            params = result['params']
            score = result['score']['total_score']
            stage = result.get('stage', 'unknown')

            logger.info(
                f"  #{i:2d}   {score:5.1f}   "
                f"{params['temperature']:5.2f}      "
                f"{params['top_p']:5.2f}  "
                f"{params['repetition_penalty']:5.2f}   "
                f"{params['max_tokens']:5d}   "
                f"{stage}"
            )

            best_combinations.append({
                'rank': i,
                'score': score,
                'params': params,
                'stage': stage,
                'details': result['score']
            })

        self.report['best_params']['top_combinations'] = best_combinations

        logger.info("")

    def analyze_stability(self):
        """分析穩定性（重複測試的結果）"""
        logger.info("🔍 分析穩定性...\n")

        # 查找所有重複測試
        repeated_tests = defaultdict(list)

        for result in self.all_results:
            if result.get('success', False) and 'repeat_id' in result:
                # 使用參數作為鍵
                params_key = json.dumps(result['params'], sort_keys=True)
                repeated_tests[params_key].append(result['score']['total_score'])

        if not repeated_tests:
            logger.info("  無重複測試數據\n")
            return

        # 分析每組重複測試
        stability_results = []

        for params_key, scores in repeated_tests.items():
            if len(scores) < 2:
                continue

            import statistics
            avg_score = statistics.mean(scores)
            std_dev = statistics.stdev(scores)
            cv = std_dev / avg_score if avg_score > 0 else 0

            params = json.loads(params_key)

            stability_results.append({
                'params': params,
                'repeat_count': len(scores),
                'avg_score': avg_score,
                'std_dev': std_dev,
                'cv': cv,
                'scores': scores
            })

        # 排序（按標準差）
        stability_results.sort(key=lambda x: x['std_dev'])

        # 顯示最穩定的組合
        logger.info("  最穩定的參數組合 (標準差最小):")
        logger.info(f"  排名  平均分  標準差  CV     重複次數")
        logger.info("  " + "-" * 50)

        for i, result in enumerate(stability_results[:5], 1):
            logger.info(
                f"  #{i}   {result['avg_score']:6.1f}  "
                f"{result['std_dev']:5.2f}   "
                f"{result['cv']:5.2%}  "
                f"{result['repeat_count']:3d}"
            )

        self.report['stability'] = stability_results

        logger.info("")

    def generate_recommendations(self):
        """生成優化建議"""
        logger.info("💡 生成優化建議...\n")

        recommendations = []

        # 建議 1: 最佳單參數值
        if 'parameters' in self.report:
            for param_name, param_data in self.report['parameters'].items():
                best_value = param_data['best_value']
                best_score = param_data['best_avg_score']

                recommendations.append({
                    'type': 'best_single_param',
                    'param': param_name,
                    'value': best_value,
                    'avg_score': best_score,
                    'description': f'最佳 {param_name} 值為 {best_value}（平均分 {best_score:.1f}）'
                })

        # 建議 2: 最佳組合
        if 'best_params' in self.report and 'top_combinations' in self.report['best_params']:
            top_combo = self.report['best_params']['top_combinations'][0]

            recommendations.append({
                'type': 'best_combination',
                'params': top_combo['params'],
                'score': top_combo['score'],
                'description': f'最佳參數組合得分 {top_combo["score"]:.1f}/120'
            })

        # 建議 3: 穩定性建議
        if 'stability' in self.report and self.report['stability']:
            most_stable = self.report['stability'][0]

            recommendations.append({
                'type': 'most_stable',
                'params': most_stable['params'],
                'std_dev': most_stable['std_dev'],
                'avg_score': most_stable['avg_score'],
                'description': f'最穩定的參數組合（標準差 {most_stable["std_dev"]:.2f}）'
            })

        # 顯示建議
        for i, rec in enumerate(recommendations, 1):
            logger.info(f"  {i}. {rec['description']}")
            if 'params' in rec:
                logger.info(f"     參數: {rec['params']}")

        self.report['recommendations'] = recommendations

        logger.info("")

    def save_report(self):
        """保存分析報告"""
        # 保存 JSON 報告
        report_file = self.results_dir / f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, ensure_ascii=False, indent=2)

        # 生成 Markdown 報告
        md_file = self.results_dir / f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        with open(md_file, 'w', encoding='utf-8') as f:
            f.write("# GLM-4 超大規模參數測試分析報告\n\n")
            f.write(f"**生成時間**: {self.report['timestamp']}\n\n")

            # 總體統計
            f.write("## 📊 總體統計\n\n")
            f.write(f"- 總測試數: {self.report['total_tests']}\n")
            f.write(f"- 成功: {self.report['successful_tests']} ({self.report['successful_tests']/self.report['total_tests']*100:.1f}%)\n")
            f.write(f"- 失敗: {self.report['failed_tests']} ({self.report['failed_tests']/self.report['total_tests']*100:.1f}%)\n\n")

            # 階段分析
            if 'stages' in self.report:
                f.write("## 📈 階段分析\n\n")

                for stage, data in self.report['stages'].items():
                    f.write(f"### {stage.upper()}\n\n")
                    f.write(f"- 測試數: {data['test_count']}\n")
                    f.write(f"- 平均分: {data['avg_score']:.1f}/120\n")
                    f.write(f"- 分數範圍: {data['min_score']:.0f} - {data['max_score']:.0f}\n")
                    f.write(f"- 最佳參數: `{data['best_params']}`\n")
                    f.write(f"- 最佳分數: {data['best_score']:.0f}/120\n\n")

            # 參數分析
            if 'parameters' in self.report:
                f.write("## 🔧 參數分析\n\n")

                for param_name, param_data in self.report['parameters'].items():
                    f.write(f"### {param_name}\n\n")
                    f.write(f"- 最佳值: {param_data['best_value']}\n")
                    f.write(f"- 最佳平均分: {param_data['best_avg_score']:.1f}/120\n\n")

            # 最佳組合
            if 'best_params' in self.report and 'top_combinations' in self.report['best_params']:
                f.write("## 🏆 最佳參數組合 (Top 10)\n\n")
                f.write("| 排名 | 分數 | Temperature | Top_P | Penalty | Tokens | 階段 |\n")
                f.write("|------|------|-------------|-------|---------|--------|------|\n")

                for combo in self.report['best_params']['top_combinations']:
                    params = combo['params']
                    f.write(
                        f"| #{combo['rank']} | {combo['score']:.1f} | "
                        f"{params['temperature']:.2f} | "
                        f"{params['top_p']:.2f} | "
                        f"{params['repetition_penalty']:.2f} | "
                        f"{params['max_tokens']} | "
                        f"{combo['stage']} |\n"
                    )

                f.write("\n")

            # 優化建議
            if 'recommendations' in self.report:
                f.write("## 💡 優化建議\n\n")

                for i, rec in enumerate(self.report['recommendations'], 1):
                    f.write(f"{i}. **{rec['description']}**\n")
                    if 'params' in rec:
                        f.write(f"   ```json\n   {json.dumps(rec['params'], indent=2, ensure_ascii=False)}\n   ```\n")
                    f.write("\n")

        logger.info(f"✅ 報告已保存:")
        logger.info(f"   JSON: {report_file}")
        logger.info(f"   Markdown: {md_file}\n")

    def run_analysis(self):
        """執行完整分析"""
        logger.info("\n" + "="*60)
        logger.info("🔬 開始分析超大規模測試結果")
        logger.info("="*60 + "\n")

        # 加載結果
        if not self.load_results():
            return

        # 執行各項分析
        self.analyze_by_stage()
        self.analyze_by_parameter()
        self.find_best_combinations(top_n=10)
        self.analyze_stability()
        self.generate_recommendations()

        # 保存報告
        self.save_report()

        logger.info("="*60)
        logger.info("✅ 分析完成")
        logger.info("="*60 + "\n")


def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='分析超大規模測試結果')

    parser.add_argument('--stage', choices=['coarse', 'fine', 'validation'],
                        help='只分析指定階段')
    parser.add_argument('--visualize', action='store_true',
                        help='生成可視化圖表（需要 matplotlib）')
    parser.add_argument('--results-dir', type=Path,
                        help='指定結果目錄')

    args = parser.parse_args()

    # 創建分析器
    analyzer = MegaResultsAnalyzer(results_dir=args.results_dir)

    # 執行分析
    analyzer.run_analysis()


if __name__ == "__main__":
    main()
