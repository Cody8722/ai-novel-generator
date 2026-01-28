#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
參數交互效應分析系統

功能：
1. 加載所有測試結果
2. 分析 Temperature × Repetition_Penalty 二維交互效應
3. 分析 Temperature × Top_P 二維交互效應
4. 分析 Temperature × Top_P × Penalty 三維交互效應
5. 尋找協同效應模式
6. 生成詳細分析報告

使用方法：
    python tests/analyze_param_interaction.py
    python tests/analyze_param_interaction.py --top 30
    python tests/analyze_param_interaction.py --output report.md
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

# 嘗試導入數據分析庫
try:
    import numpy as np
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    print("⚠️ 未安裝 pandas/numpy，將使用基本分析模式")

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ParamInteractionAnalyzer:
    """參數交互效應分析器"""

    def __init__(self, results_dir: Path = None):
        """
        初始化分析器

        Args:
            results_dir: 測試結果目錄
        """
        if results_dir is None:
            results_dir = Path(__file__).parent.parent / "test_results" / "mega_test"

        self.results_dir = results_dir
        self.all_results = []
        self.df = None  # pandas DataFrame

        self.report = {
            'timestamp': datetime.now().isoformat(),
            'total_results': 0,
            'interactions': {},
            'synergies': {},
            'best_combinations': [],
            'conclusions': []
        }

    def load_results(self) -> bool:
        """
        加載所有批次測試結果

        Returns:
            是否成功加載
        """
        logger.info("\n" + "=" * 60)
        logger.info("📂 加載測試結果")
        logger.info("=" * 60 + "\n")

        if not self.results_dir.exists():
            logger.error(f"❌ 結果目錄不存在: {self.results_dir}")
            return False

        # 查找所有批次結果文件
        batch_files = sorted(self.results_dir.glob("batch_*_results.json"))

        if not batch_files:
            logger.error(f"❌ 找不到批次結果文件")
            return False

        logger.info(f"找到 {len(batch_files)} 個批次文件")

        # 加載所有結果
        for batch_file in batch_files:
            try:
                with open(batch_file, 'r', encoding='utf-8') as f:
                    batch_results = json.load(f)

                    # 過濾成功的結果
                    for result in batch_results:
                        if result.get('success', False):
                            self.all_results.append(result)

                    logger.info(f"  ✅ {batch_file.name}: {len(batch_results)} 組")
            except Exception as e:
                logger.error(f"  ❌ {batch_file.name}: {e}")
                continue

        self.report['total_results'] = len(self.all_results)
        logger.info(f"\n✅ 成功加載 {len(self.all_results)} 組有效結果\n")

        # 如果有 pandas，創建 DataFrame
        if HAS_PANDAS and self.all_results:
            self._create_dataframe()

        return len(self.all_results) > 0

    def _create_dataframe(self):
        """創建 pandas DataFrame"""
        data = []
        for result in self.all_results:
            params = result.get('params', {})
            score = result.get('score', {})

            row = {
                'temperature': params.get('temperature'),
                'top_p': params.get('top_p'),
                'repetition_penalty': params.get('repetition_penalty'),
                'max_tokens': params.get('max_tokens'),
                'total_score': score.get('total_score', 0),
                'base_score': score.get('total_score', 0) - score.get('glm4_score', 0),
                'glm4_score': score.get('glm4_score', 0),
                'stage': result.get('stage', 'unknown'),
                'focus': result.get('focus', 'unknown')
            }

            # 添加 GLM-4 細分指標
            glm4_checks = score.get('glm4_checks', {})
            row['chinese_fluency'] = glm4_checks.get('chinese_fluency', 0)
            row['cultural_depth'] = glm4_checks.get('cultural_depth', 0)
            row['creativity'] = glm4_checks.get('creativity', 0)
            row['coherence'] = glm4_checks.get('coherence', 0)

            data.append(row)

        self.df = pd.DataFrame(data)
        logger.info(f"📊 DataFrame 創建完成: {len(self.df)} 行 x {len(self.df.columns)} 列")

    def analyze_2d_interaction(self, param1: str, param2: str) -> Dict:
        """
        分析二維參數交互效應

        Args:
            param1: 第一個參數名
            param2: 第二個參數名

        Returns:
            交互分析結果
        """
        logger.info(f"\n📊 分析 {param1} × {param2} 交互效應...")

        if HAS_PANDAS and self.df is not None:
            return self._analyze_2d_pandas(param1, param2)
        else:
            return self._analyze_2d_basic(param1, param2)

    def _analyze_2d_pandas(self, param1: str, param2: str) -> Dict:
        """使用 pandas 分析二維交互"""
        # 創建交叉表
        pivot = self.df.pivot_table(
            values='total_score',
            index=param1,
            columns=param2,
            aggfunc=['mean', 'count', 'std']
        )

        # 找出最佳組合
        grouped = self.df.groupby([param1, param2]).agg({
            'total_score': ['mean', 'count', 'std', 'max', 'min']
        }).reset_index()

        grouped.columns = [param1, param2, 'avg_score', 'count', 'std', 'max_score', 'min_score']
        grouped = grouped.sort_values('avg_score', ascending=False)

        # 提取結果
        result = {
            'param1': param1,
            'param2': param2,
            'best_combinations': [],
            'interaction_matrix': {},
            'summary': {}
        }

        # Top 10 組合
        for _, row in grouped.head(10).iterrows():
            result['best_combinations'].append({
                param1: row[param1],
                param2: row[param2],
                'avg_score': round(row['avg_score'], 2),
                'count': int(row['count']),
                'std': round(row['std'], 2) if not pd.isna(row['std']) else 0
            })

        # 交互矩陣
        for idx in pivot['mean'].index:
            result['interaction_matrix'][idx] = {}
            for col in pivot['mean'].columns:
                val = pivot['mean'].loc[idx, col]
                if not pd.isna(val):
                    result['interaction_matrix'][idx][col] = round(val, 2)

        # 摘要統計
        result['summary'] = {
            'total_combinations': len(grouped),
            'avg_score_overall': round(self.df['total_score'].mean(), 2),
            'best_avg_score': round(grouped['avg_score'].max(), 2),
            'worst_avg_score': round(grouped['avg_score'].min(), 2),
            'score_range': round(grouped['avg_score'].max() - grouped['avg_score'].min(), 2)
        }

        # 打印結果
        self._print_2d_results(result)

        return result

    def _analyze_2d_basic(self, param1: str, param2: str) -> Dict:
        """使用基本方法分析二維交互"""
        # 按參數組合分組
        groups = defaultdict(list)

        for result in self.all_results:
            params = result.get('params', {})
            score = result.get('score', {})

            key = (params.get(param1), params.get(param2))
            groups[key].append(score.get('total_score', 0))

        # 計算統計
        stats = []
        for (v1, v2), scores in groups.items():
            if scores:
                avg = sum(scores) / len(scores)
                std = (sum((s - avg) ** 2 for s in scores) / len(scores)) ** 0.5 if len(scores) > 1 else 0
                stats.append({
                    param1: v1,
                    param2: v2,
                    'avg_score': round(avg, 2),
                    'count': len(scores),
                    'std': round(std, 2),
                    'max_score': max(scores),
                    'min_score': min(scores)
                })

        # 排序
        stats.sort(key=lambda x: x['avg_score'], reverse=True)

        result = {
            'param1': param1,
            'param2': param2,
            'best_combinations': stats[:10],
            'summary': {
                'total_combinations': len(stats),
                'best_avg_score': stats[0]['avg_score'] if stats else 0,
                'worst_avg_score': stats[-1]['avg_score'] if stats else 0
            }
        }

        self._print_2d_results(result)
        return result

    def _print_2d_results(self, result: Dict):
        """打印二維分析結果"""
        param1 = result['param1']
        param2 = result['param2']

        print(f"\n  🏆 {param1} × {param2} Top 10 組合:")
        print(f"  {'排名':<4} {param1:<12} {param2:<12} {'平均分':<10} {'次數':<6} {'標準差':<8}")
        print("  " + "-" * 56)

        for i, combo in enumerate(result['best_combinations'], 1):
            print(f"  {i:<4} {combo[param1]:<12.2f} {combo[param2]:<12.2f} "
                  f"{combo['avg_score']:<10.2f} {combo['count']:<6} {combo['std']:<8.2f}")

        print(f"\n  📈 摘要:")
        print(f"     總組合數: {result['summary']['total_combinations']}")
        print(f"     最佳平均分: {result['summary']['best_avg_score']}")
        print(f"     最差平均分: {result['summary']['worst_avg_score']}")

    def analyze_3d_interaction(self, param1: str, param2: str, param3: str) -> Dict:
        """
        分析三維參數交互效應

        Args:
            param1: 第一個參數
            param2: 第二個參數
            param3: 第三個參數

        Returns:
            三維交互分析結果
        """
        logger.info(f"\n📊 分析 {param1} × {param2} × {param3} 三維交互效應...")

        if HAS_PANDAS and self.df is not None:
            grouped = self.df.groupby([param1, param2, param3]).agg({
                'total_score': ['mean', 'count', 'std']
            }).reset_index()

            grouped.columns = [param1, param2, param3, 'avg_score', 'count', 'std']
            grouped = grouped.sort_values('avg_score', ascending=False)

            result = {
                'params': [param1, param2, param3],
                'best_combinations': [],
                'summary': {}
            }

            # Top 20 組合
            for _, row in grouped.head(20).iterrows():
                result['best_combinations'].append({
                    param1: row[param1],
                    param2: row[param2],
                    param3: row[param3],
                    'avg_score': round(row['avg_score'], 2),
                    'count': int(row['count']),
                    'std': round(row['std'], 2) if not pd.isna(row['std']) else 0
                })

            result['summary'] = {
                'total_combinations': len(grouped),
                'best_avg_score': round(grouped['avg_score'].max(), 2),
                'worst_avg_score': round(grouped['avg_score'].min(), 2)
            }
        else:
            # 基本方法
            groups = defaultdict(list)
            for r in self.all_results:
                params = r.get('params', {})
                score = r.get('score', {})
                key = (params.get(param1), params.get(param2), params.get(param3))
                groups[key].append(score.get('total_score', 0))

            stats = []
            for (v1, v2, v3), scores in groups.items():
                if scores:
                    avg = sum(scores) / len(scores)
                    std = (sum((s - avg) ** 2 for s in scores) / len(scores)) ** 0.5 if len(scores) > 1 else 0
                    stats.append({
                        param1: v1, param2: v2, param3: v3,
                        'avg_score': round(avg, 2),
                        'count': len(scores),
                        'std': round(std, 2)
                    })

            stats.sort(key=lambda x: x['avg_score'], reverse=True)
            result = {
                'params': [param1, param2, param3],
                'best_combinations': stats[:20],
                'summary': {'total_combinations': len(stats)}
            }

        # 打印結果
        print(f"\n  🏆 {param1} × {param2} × {param3} Top 20 組合:")
        print(f"  {'排名':<4} {param1:<10} {param2:<10} {param3:<10} {'平均分':<10} {'次數':<6} {'標準差':<8}")
        print("  " + "-" * 68)

        for i, combo in enumerate(result['best_combinations'], 1):
            print(f"  {i:<4} {combo[param1]:<10.2f} {combo[param2]:<10.2f} {combo[param3]:<10.2f} "
                  f"{combo['avg_score']:<10.2f} {combo['count']:<6} {combo['std']:<8.2f}")

        return result

    def analyze_synergy_patterns(self) -> Dict:
        """
        分析協同效應模式

        Returns:
            協同效應分析結果
        """
        logger.info("\n" + "=" * 60)
        logger.info("🔬 分析協同效應模式")
        logger.info("=" * 60)

        result = {
            'patterns': [],
            'conclusions': []
        }

        if not HAS_PANDAS or self.df is None:
            logger.warning("需要 pandas 進行協同效應分析")
            return result

        # 模式 1: 低 Temperature + 高 Penalty vs 高 Temperature + 低 Penalty
        logger.info("\n📊 模式 1: Temperature × Penalty 協同效應")

        # 定義區間
        low_temp = self.df['temperature'] <= 0.65
        high_temp = self.df['temperature'] >= 0.75
        low_penalty = self.df['repetition_penalty'] <= 1.03
        high_penalty = self.df['repetition_penalty'] >= 1.08

        patterns_data = {
            '低溫低懲罰': self.df[low_temp & low_penalty]['total_score'],
            '低溫高懲罰': self.df[low_temp & high_penalty]['total_score'],
            '高溫低懲罰': self.df[high_temp & low_penalty]['total_score'],
            '高溫高懲罰': self.df[high_temp & high_penalty]['total_score'],
            '中溫中懲罰': self.df[(~low_temp & ~high_temp) & (~low_penalty & ~high_penalty)]['total_score']
        }

        print("\n  Temperature × Penalty 模式分析:")
        print(f"  {'模式':<15} {'平均分':<10} {'次數':<8} {'標準差':<10}")
        print("  " + "-" * 48)

        pattern_stats = []
        for pattern_name, scores in patterns_data.items():
            if len(scores) > 0:
                avg = scores.mean()
                std = scores.std() if len(scores) > 1 else 0
                count = len(scores)
                print(f"  {pattern_name:<15} {avg:<10.2f} {count:<8} {std:<10.2f}")
                pattern_stats.append({
                    'pattern': pattern_name,
                    'avg_score': round(avg, 2),
                    'count': count,
                    'std': round(std, 2)
                })

        result['patterns'].append({
            'name': 'Temperature × Penalty',
            'stats': pattern_stats
        })

        # 模式 2: Temperature × Top_P 協同效應
        logger.info("\n📊 模式 2: Temperature × Top_P 協同效應")

        low_topp = self.df['top_p'] <= 0.88
        high_topp = self.df['top_p'] >= 0.93

        patterns_data_2 = {
            '低溫低採樣': self.df[low_temp & low_topp]['total_score'],
            '低溫高採樣': self.df[low_temp & high_topp]['total_score'],
            '高溫低採樣': self.df[high_temp & low_topp]['total_score'],
            '高溫高採樣': self.df[high_temp & high_topp]['total_score'],
            '中溫中採樣': self.df[(~low_temp & ~high_temp) & (~low_topp & ~high_topp)]['total_score']
        }

        print("\n  Temperature × Top_P 模式分析:")
        print(f"  {'模式':<15} {'平均分':<10} {'次數':<8} {'標準差':<10}")
        print("  " + "-" * 48)

        pattern_stats_2 = []
        for pattern_name, scores in patterns_data_2.items():
            if len(scores) > 0:
                avg = scores.mean()
                std = scores.std() if len(scores) > 1 else 0
                count = len(scores)
                print(f"  {pattern_name:<15} {avg:<10.2f} {count:<8} {std:<10.2f}")
                pattern_stats_2.append({
                    'pattern': pattern_name,
                    'avg_score': round(avg, 2),
                    'count': count,
                    'std': round(std, 2)
                })

        result['patterns'].append({
            'name': 'Temperature × Top_P',
            'stats': pattern_stats_2
        })

        # 生成結論
        self._generate_synergy_conclusions(result)

        return result

    def _generate_synergy_conclusions(self, result: Dict):
        """生成協同效應結論"""
        conclusions = []

        for pattern_group in result['patterns']:
            stats = pattern_group['stats']
            if not stats:
                continue

            # 找最佳和最差模式
            sorted_stats = sorted(stats, key=lambda x: x['avg_score'], reverse=True)
            best = sorted_stats[0]
            worst = sorted_stats[-1]

            diff = best['avg_score'] - worst['avg_score']

            if diff > 5:
                conclusions.append(
                    f"🔥 {pattern_group['name']}: 顯著協同效應！"
                    f"「{best['pattern']}」比「{worst['pattern']}」高 {diff:.1f} 分"
                )
            elif diff > 2:
                conclusions.append(
                    f"📊 {pattern_group['name']}: 輕微協同效應。"
                    f"「{best['pattern']}」略優於「{worst['pattern']}」"
                )
            else:
                conclusions.append(
                    f"⚖️ {pattern_group['name']}: 無顯著協同效應，各模式表現相近"
                )

        result['conclusions'] = conclusions

        print("\n  📝 協同效應結論:")
        for conclusion in conclusions:
            print(f"     {conclusion}")

    def find_best_overall_combinations(self, top_n: int = 30) -> List[Dict]:
        """
        找出整體最佳參數組合

        Args:
            top_n: 返回前 N 個最佳組合

        Returns:
            最佳組合列表
        """
        logger.info("\n" + "=" * 60)
        logger.info(f"🏆 尋找整體最佳參數組合 (Top {top_n})")
        logger.info("=" * 60)

        if HAS_PANDAS and self.df is not None:
            # 按四個參數分組
            grouped = self.df.groupby(
                ['temperature', 'top_p', 'repetition_penalty', 'max_tokens']
            ).agg({
                'total_score': ['mean', 'count', 'std', 'max', 'min'],
                'glm4_score': 'mean',
                'chinese_fluency': 'mean',
                'cultural_depth': 'mean',
                'creativity': 'mean',
                'coherence': 'mean'
            }).reset_index()

            grouped.columns = [
                'temperature', 'top_p', 'repetition_penalty', 'max_tokens',
                'avg_score', 'count', 'std', 'max_score', 'min_score',
                'avg_glm4', 'avg_fluency', 'avg_cultural', 'avg_creativity', 'avg_coherence'
            ]

            # 排序
            grouped = grouped.sort_values('avg_score', ascending=False)

            best_combinations = []
            for _, row in grouped.head(top_n).iterrows():
                best_combinations.append({
                    'temperature': row['temperature'],
                    'top_p': row['top_p'],
                    'repetition_penalty': row['repetition_penalty'],
                    'max_tokens': int(row['max_tokens']),
                    'avg_score': round(row['avg_score'], 2),
                    'count': int(row['count']),
                    'std': round(row['std'], 2) if not pd.isna(row['std']) else 0,
                    'max_score': round(row['max_score'], 2),
                    'min_score': round(row['min_score'], 2),
                    'glm4_details': {
                        'avg_glm4': round(row['avg_glm4'], 2),
                        'avg_fluency': round(row['avg_fluency'], 2),
                        'avg_cultural': round(row['avg_cultural'], 2),
                        'avg_creativity': round(row['avg_creativity'], 2),
                        'avg_coherence': round(row['avg_coherence'], 2)
                    }
                })
        else:
            # 基本方法
            groups = defaultdict(list)
            for r in self.all_results:
                params = r.get('params', {})
                score = r.get('score', {})
                key = (
                    params.get('temperature'),
                    params.get('top_p'),
                    params.get('repetition_penalty'),
                    params.get('max_tokens')
                )
                groups[key].append(score.get('total_score', 0))

            stats = []
            for (temp, topp, penalty, tokens), scores in groups.items():
                if scores:
                    avg = sum(scores) / len(scores)
                    std = (sum((s - avg) ** 2 for s in scores) / len(scores)) ** 0.5 if len(scores) > 1 else 0
                    stats.append({
                        'temperature': temp,
                        'top_p': topp,
                        'repetition_penalty': penalty,
                        'max_tokens': tokens,
                        'avg_score': round(avg, 2),
                        'count': len(scores),
                        'std': round(std, 2),
                        'max_score': max(scores),
                        'min_score': min(scores)
                    })

            stats.sort(key=lambda x: x['avg_score'], reverse=True)
            best_combinations = stats[:top_n]

        self.report['best_combinations'] = best_combinations

        # 打印結果
        print(f"\n  {'排名':<4} {'Temp':<8} {'TopP':<8} {'Penalty':<10} {'Tokens':<8} "
              f"{'平均分':<10} {'次數':<6} {'標準差':<8} {'最高':<8} {'最低':<8}")
        print("  " + "-" * 90)

        for i, combo in enumerate(best_combinations, 1):
            print(f"  {i:<4} {combo['temperature']:<8.2f} {combo['top_p']:<8.2f} "
                  f"{combo['repetition_penalty']:<10.2f} {combo['max_tokens']:<8} "
                  f"{combo['avg_score']:<10.2f} {combo['count']:<6} {combo['std']:<8.2f} "
                  f"{combo.get('max_score', 0):<8.1f} {combo.get('min_score', 0):<8.1f}")

        return best_combinations

    def generate_report(self, output_file: Path = None):
        """
        生成完整分析報告

        Args:
            output_file: 輸出文件路徑
        """
        if output_file is None:
            output_file = self.results_dir / f"interaction_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        logger.info("\n" + "=" * 60)
        logger.info("📝 生成分析報告")
        logger.info("=" * 60)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# GLM-4 參數交互效應分析報告\n\n")
            f.write(f"**生成時間**: {self.report['timestamp']}\n")
            f.write(f"**分析樣本數**: {self.report['total_results']}\n\n")

            # 整體最佳組合
            f.write("## 🏆 整體最佳參數組合 (Top 30)\n\n")
            f.write("| 排名 | Temperature | Top_P | Penalty | Tokens | 平均分 | 次數 | 標準差 |\n")
            f.write("|------|-------------|-------|---------|--------|--------|------|--------|\n")

            for i, combo in enumerate(self.report['best_combinations'][:30], 1):
                f.write(f"| {i} | {combo['temperature']:.2f} | {combo['top_p']:.2f} | "
                        f"{combo['repetition_penalty']:.2f} | {combo['max_tokens']} | "
                        f"{combo['avg_score']:.2f} | {combo['count']} | {combo['std']:.2f} |\n")

            # 二維交互分析
            if 'temp_penalty' in self.report['interactions']:
                f.write("\n## 📊 Temperature × Penalty 交互分析\n\n")
                interaction = self.report['interactions']['temp_penalty']
                f.write("| Temperature | Penalty | 平均分 | 次數 |\n")
                f.write("|-------------|---------|--------|------|\n")
                for combo in interaction['best_combinations'][:10]:
                    f.write(f"| {combo['temperature']:.2f} | {combo['repetition_penalty']:.2f} | "
                            f"{combo['avg_score']:.2f} | {combo['count']} |\n")

            if 'temp_topp' in self.report['interactions']:
                f.write("\n## 📊 Temperature × Top_P 交互分析\n\n")
                interaction = self.report['interactions']['temp_topp']
                f.write("| Temperature | Top_P | 平均分 | 次數 |\n")
                f.write("|-------------|-------|--------|------|\n")
                for combo in interaction['best_combinations'][:10]:
                    f.write(f"| {combo['temperature']:.2f} | {combo['top_p']:.2f} | "
                            f"{combo['avg_score']:.2f} | {combo['count']} |\n")

            # 協同效應結論
            if 'synergies' in self.report and self.report['synergies'].get('conclusions'):
                f.write("\n## 🔬 協同效應結論\n\n")
                for conclusion in self.report['synergies']['conclusions']:
                    f.write(f"- {conclusion}\n")

            # 最終建議
            f.write("\n## 💡 最終建議\n\n")
            if self.report['best_combinations']:
                best = self.report['best_combinations'][0]
                f.write(f"**推薦參數配置**:\n")
                f.write(f"```python\n")
                f.write(f"params = {{\n")
                f.write(f"    'temperature': {best['temperature']},\n")
                f.write(f"    'top_p': {best['top_p']},\n")
                f.write(f"    'repetition_penalty': {best['repetition_penalty']},\n")
                f.write(f"    'max_tokens': {best['max_tokens']}\n")
                f.write(f"}}\n")
                f.write(f"# 預期分數: {best['avg_score']}/120\n")
                f.write(f"```\n")

        logger.info(f"✅ 報告已保存: {output_file}")

    def run_full_analysis(self, top_n: int = 30, output_file: Path = None):
        """
        執行完整分析流程

        Args:
            top_n: 返回前 N 個最佳組合
            output_file: 輸出文件路徑
        """
        # 加載數據
        if not self.load_results():
            logger.error("❌ 無法加載數據，分析終止")
            return

        # 二維交互分析
        self.report['interactions']['temp_penalty'] = self.analyze_2d_interaction(
            'temperature', 'repetition_penalty'
        )
        self.report['interactions']['temp_topp'] = self.analyze_2d_interaction(
            'temperature', 'top_p'
        )
        self.report['interactions']['topp_penalty'] = self.analyze_2d_interaction(
            'top_p', 'repetition_penalty'
        )

        # 三維交互分析
        self.report['interactions']['3d'] = self.analyze_3d_interaction(
            'temperature', 'top_p', 'repetition_penalty'
        )

        # 協同效應分析
        self.report['synergies'] = self.analyze_synergy_patterns()

        # 最佳組合
        self.find_best_overall_combinations(top_n)

        # 生成報告
        self.generate_report(output_file)

        # 最終摘要
        print("\n" + "=" * 60)
        print("📋 分析完成摘要")
        print("=" * 60)
        print(f"  總分析樣本: {self.report['total_results']}")
        print(f"  最佳組合數: {len(self.report['best_combinations'])}")

        if self.report['best_combinations']:
            best = self.report['best_combinations'][0]
            print(f"\n  🥇 最佳參數組合:")
            print(f"     Temperature: {best['temperature']}")
            print(f"     Top_P: {best['top_p']}")
            print(f"     Penalty: {best['repetition_penalty']}")
            print(f"     Max_Tokens: {best['max_tokens']}")
            print(f"     平均分: {best['avg_score']}/120")
            print(f"     測試次數: {best['count']}")

        print("=" * 60 + "\n")


def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='參數交互效應分析')
    parser.add_argument('--top', type=int, default=30, help='返回前 N 個最佳組合')
    parser.add_argument('--output', type=Path, help='輸出報告文件路徑')
    parser.add_argument('--results-dir', type=Path, help='測試結果目錄')

    args = parser.parse_args()

    # 創建分析器
    analyzer = ParamInteractionAnalyzer(results_dir=args.results_dir)

    # 執行分析
    analyzer.run_full_analysis(top_n=args.top, output_file=args.output)


if __name__ == "__main__":
    main()
