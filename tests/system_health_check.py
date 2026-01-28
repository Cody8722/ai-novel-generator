#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
全面系統健康檢查

檢查項目：
1. GLM-4 特有指標功能
2. 參數影響分析
3. 評分系統一致性
4. API 穩定性
5. 輸出品質驗證

使用方法：
    # 執行完整檢查
    python tests/system_health_check.py

    # 執行特定檢查
    python tests/system_health_check.py --check glm4-metrics
    python tests/system_health_check.py --check param-impact
    python tests/system_health_check.py --check scoring-consistency
    python tests/system_health_check.py --check api-stability
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import time
import logging
import statistics
import argparse
from datetime import datetime
from typing import Dict, List, Tuple
from tests.test_glm4_params import GLM4ParamsTester

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SystemHealthChecker:
    """系統健康檢查器"""

    def __init__(self, api_key: str):
        """
        初始化系統檢查器

        Args:
            api_key: API 金鑰
        """
        self.api_key = api_key
        self.output_dir = Path(__file__).parent.parent / "test_results" / "health_check"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.report = {
            'timestamp': datetime.now().isoformat(),
            'checks': {},
            'overall_status': 'unknown'
        }

    def check_glm4_metrics(self) -> Dict:
        """
        檢查 GLM-4 特有指標

        Returns:
            檢查結果
        """
        logger.info("\n" + "="*60)
        logger.info("🔍 檢查 GLM-4 特有指標")
        logger.info("="*60 + "\n")

        results = {
            'status': 'unknown',
            'test_count': 10,
            'metrics': {},
            'issues': []
        }

        # 創建測試器
        tester = GLM4ParamsTester(
            self.api_key,
            quick_mode=False,
            enable_ai_review=False,
            debug_mode=False
        )

        # 測試參數
        test_params = {
            'temperature': 0.7,
            'top_p': 0.9,
            'repetition_penalty': 1.05,
            'max_tokens': 4000
        }

        # 生成測試大綱並評估
        logger.info("📝 生成 10 個測試大綱...")
        metrics_data = {
            'chinese_fluency': [],
            'cultural_depth': [],
            'creativity': [],
            'coherence': [],
            'glm4_score': []
        }

        for i in range(10):
            logger.info(f"  測試 {i+1}/10...")

            try:
                outline, cost, score = tester.test_params(test_params)

                # 提取 GLM-4 指標
                glm4_checks = score.get('glm4_checks', {})

                if glm4_checks:
                    metrics_data['chinese_fluency'].append(glm4_checks.get('chinese_fluency', 0))
                    metrics_data['cultural_depth'].append(glm4_checks.get('cultural_depth', 0))
                    metrics_data['creativity'].append(glm4_checks.get('creativity', 0))
                    metrics_data['coherence'].append(glm4_checks.get('coherence', 0))
                    metrics_data['glm4_score'].append(score.get('glm4_score', 0))
                else:
                    logger.warning(f"    ⚠️ 測試 {i+1} 沒有 GLM-4 指標數據")

                # API 延遲
                time.sleep(3)

            except Exception as e:
                logger.error(f"    ❌ 測試 {i+1} 失敗: {e}")
                continue

        # 分析結果
        logger.info("\n📊 分析指標數據...\n")

        for metric, values in metrics_data.items():
            if not values:
                logger.warning(f"  ⚠️ {metric}: 無數據")
                results['issues'].append(f"{metric} has no data")
                continue

            avg = sum(values) / len(values)
            non_zero = sum(1 for v in values if v > 0)
            zero_rate = (len(values) - non_zero) / len(values) * 100

            logger.info(f"  {metric}:")
            logger.info(f"    數據點: {len(values)}")
            logger.info(f"    平均值: {avg:.2f}")
            logger.info(f"    最小值: {min(values):.2f}")
            logger.info(f"    最大值: {max(values):.2f}")
            logger.info(f"    非零比例: {non_zero}/{len(values)} ({non_zero/len(values)*100:.1f}%)")

            results['metrics'][metric] = {
                'avg': avg,
                'min': min(values),
                'max': max(values),
                'non_zero_rate': non_zero / len(values),
                'zero_rate': zero_rate
            }

            # 檢查問題
            if zero_rate > 50:
                logger.warning(f"    ⚠️ {metric} 零值比例過高 ({zero_rate:.1f}%)")
                results['issues'].append(f"{metric} has high zero rate: {zero_rate:.1f}%")
            elif zero_rate > 20:
                logger.warning(f"    ⚠️ {metric} 零值比例偏高 ({zero_rate:.1f}%)")
                results['issues'].append(f"{metric} has elevated zero rate: {zero_rate:.1f}%")
            else:
                logger.info(f"    ✅ {metric} 表現正常")

        # 判斷狀態
        if not results['issues']:
            results['status'] = 'healthy'
            logger.info("\n✅ GLM-4 指標檢查通過\n")
        elif len(results['issues']) <= 2:
            results['status'] = 'warning'
            logger.warning(f"\n⚠️ GLM-4 指標檢查發現 {len(results['issues'])} 個警告\n")
        else:
            results['status'] = 'critical'
            logger.error(f"\n❌ GLM-4 指標檢查失敗：{len(results['issues'])} 個問題\n")

        return results

    def check_param_impact(self) -> Dict:
        """
        檢查參數影響

        Returns:
            檢查結果
        """
        logger.info("\n" + "="*60)
        logger.info("🔍 檢查參數獨立影響")
        logger.info("="*60 + "\n")

        results = {
            'status': 'unknown',
            'parameters': {},
            'issues': []
        }

        # 創建測試器
        tester = GLM4ParamsTester(
            self.api_key,
            quick_mode=False,
            enable_ai_review=False,
            debug_mode=False
        )

        # 測試 Temperature 影響
        logger.info("📈 測試 Temperature 影響...")
        temp_data = []
        for temp in [0.5, 0.6, 0.7, 0.8, 0.9]:
            logger.info(f"  Temperature = {temp}")
            params = {
                'temperature': temp,
                'top_p': 0.9,
                'repetition_penalty': 1.05,
                'max_tokens': 4000
            }

            try:
                outline, cost, score = tester.test_params(params)
                temp_data.append((temp, score['total_score']))
                logger.info(f"    分數: {score['total_score']:.0f}/120")
                time.sleep(3)
            except Exception as e:
                logger.error(f"    ❌ 失敗: {e}")
                continue

        # 分析 Temperature 趨勢
        temp_trend = self._analyze_trend('Temperature', temp_data)
        results['parameters']['temperature'] = temp_trend

        # 測試 Top_P 影響
        logger.info("\n📈 測試 Top_P 影響...")
        topp_data = []
        for top_p in [0.8, 0.85, 0.9, 0.95]:
            logger.info(f"  Top_P = {top_p}")
            params = {
                'temperature': 0.7,
                'top_p': top_p,
                'repetition_penalty': 1.05,
                'max_tokens': 4000
            }

            try:
                outline, cost, score = tester.test_params(params)
                topp_data.append((top_p, score['total_score']))
                logger.info(f"    分數: {score['total_score']:.0f}/120")
                time.sleep(3)
            except Exception as e:
                logger.error(f"    ❌ 失敗: {e}")
                continue

        topp_trend = self._analyze_trend('Top_P', topp_data)
        results['parameters']['top_p'] = topp_trend

        # 測試 Repetition Penalty 影響
        logger.info("\n📈 測試 Repetition Penalty 影響...")
        penalty_data = []
        for penalty in [1.0, 1.05, 1.1, 1.15]:
            logger.info(f"  Penalty = {penalty}")
            params = {
                'temperature': 0.7,
                'top_p': 0.9,
                'repetition_penalty': penalty,
                'max_tokens': 4000
            }

            try:
                outline, cost, score = tester.test_params(params)
                penalty_data.append((penalty, score['total_score']))
                logger.info(f"    分數: {score['total_score']:.0f}/120")
                time.sleep(3)
            except Exception as e:
                logger.error(f"    ❌ 失敗: {e}")
                continue

        penalty_trend = self._analyze_trend('Repetition Penalty', penalty_data)
        results['parameters']['repetition_penalty'] = penalty_trend

        # 判斷狀態
        if not results['issues']:
            results['status'] = 'healthy'
            logger.info("\n✅ 參數影響檢查通過\n")
        else:
            results['status'] = 'warning'
            logger.warning(f"\n⚠️ 參數影響檢查發現 {len(results['issues'])} 個異常\n")

        return results

    def _analyze_trend(self, param_name: str, data: List[Tuple[float, float]]) -> Dict:
        """
        分析參數趨勢

        Args:
            param_name: 參數名稱
            data: (參數值, 分數) 列表

        Returns:
            趨勢分析結果
        """
        if len(data) < 2:
            return {
                'trend': 'insufficient_data',
                'data': data,
                'description': '數據不足'
            }

        # 計算趨勢
        values = [d[0] for d in data]
        scores = [d[1] for d in data]

        # 簡單線性趨勢檢測
        increasing = sum(1 for i in range(len(scores) - 1) if scores[i + 1] > scores[i])
        decreasing = sum(1 for i in range(len(scores) - 1) if scores[i + 1] < scores[i])

        if increasing > decreasing:
            trend = 'increasing'
            description = f'{param_name} 增加時分數上升'
        elif decreasing > increasing:
            trend = 'decreasing'
            description = f'{param_name} 增加時分數下降'
        else:
            trend = 'stable'
            description = f'{param_name} 對分數影響不明顯'

        # 找出最佳值
        best_idx = scores.index(max(scores))
        best_value = values[best_idx]
        best_score = scores[best_idx]

        logger.info(f"\n  {param_name} 趨勢分析:")
        logger.info(f"    趨勢: {description}")
        logger.info(f"    最佳值: {best_value} (分數: {best_score:.0f})")
        logger.info(f"    分數範圍: {min(scores):.0f} - {max(scores):.0f}")

        return {
            'trend': trend,
            'description': description,
            'best_value': best_value,
            'best_score': best_score,
            'score_range': (min(scores), max(scores)),
            'data': data
        }

    def check_scoring_consistency(self) -> Dict:
        """
        檢查評分一致性

        Returns:
            檢查結果
        """
        logger.info("\n" + "="*60)
        logger.info("🔍 檢查評分一致性")
        logger.info("="*60 + "\n")

        results = {
            'status': 'unknown',
            'repetitions': 5,
            'scores': [],
            'statistics': {},
            'issues': []
        }

        # 創建測試器
        tester = GLM4ParamsTester(
            self.api_key,
            quick_mode=False,
            enable_ai_review=False,
            debug_mode=False
        )

        # 固定參數
        params = {
            'temperature': 0.7,
            'top_p': 0.9,
            'repetition_penalty': 1.05,
            'max_tokens': 4000
        }

        logger.info(f"📝 使用相同參數生成 {results['repetitions']} 次...")
        logger.info(f"   參數: {params}\n")

        scores = []
        for i in range(results['repetitions']):
            logger.info(f"  重複測試 {i+1}/{results['repetitions']}")

            try:
                outline, cost, score = tester.test_params(params)
                scores.append(score['total_score'])
                logger.info(f"    分數: {score['total_score']:.0f}/120")
                time.sleep(3)
            except Exception as e:
                logger.error(f"    ❌ 失敗: {e}")
                continue

        if len(scores) < 2:
            results['status'] = 'critical'
            results['issues'].append('測試數據不足')
            logger.error("\n❌ 評分一致性檢查失敗：數據不足\n")
            return results

        # 計算統計數據
        avg_score = statistics.mean(scores)
        std_dev = statistics.stdev(scores)
        min_score = min(scores)
        max_score = max(scores)
        score_range = max_score - min_score

        results['scores'] = scores
        results['statistics'] = {
            'mean': avg_score,
            'std_dev': std_dev,
            'min': min_score,
            'max': max_score,
            'range': score_range,
            'cv': std_dev / avg_score if avg_score > 0 else 0  # 變異係數
        }

        logger.info(f"\n📊 統計分析:")
        logger.info(f"  分數列表: {[f'{s:.0f}' for s in scores]}")
        logger.info(f"  平均分: {avg_score:.1f}")
        logger.info(f"  標準差: {std_dev:.2f}")
        logger.info(f"  最小值: {min_score:.0f}")
        logger.info(f"  最大值: {max_score:.0f}")
        logger.info(f"  分數範圍: {score_range:.1f}")
        logger.info(f"  變異係數: {std_dev / avg_score:.2%}")

        # 判斷一致性
        if std_dev > 15:
            results['status'] = 'critical'
            results['issues'].append(f'標準差過大 ({std_dev:.2f})')
            logger.error(f"\n❌ 評分波動過大：標準差 {std_dev:.2f} > 15\n")
        elif std_dev > 10:
            results['status'] = 'warning'
            results['issues'].append(f'標準差偏高 ({std_dev:.2f})')
            logger.warning(f"\n⚠️ 評分波動偏高：標準差 {std_dev:.2f} > 10\n")
        else:
            results['status'] = 'healthy'
            logger.info(f"\n✅ 評分一致性良好：標準差 {std_dev:.2f} <= 10\n")

        return results

    def check_api_stability(self) -> Dict:
        """
        檢查 API 穩定性

        Returns:
            檢查結果
        """
        logger.info("\n" + "="*60)
        logger.info("🔍 檢查 API 穩定性")
        logger.info("="*60 + "\n")

        results = {
            'status': 'unknown',
            'test_count': 10,
            'success_count': 0,
            'failure_count': 0,
            'response_times': [],
            'issues': []
        }

        # 創建測試器
        tester = GLM4ParamsTester(
            self.api_key,
            quick_mode=False,
            enable_ai_review=False,
            debug_mode=False
        )

        params = {
            'temperature': 0.7,
            'top_p': 0.9,
            'repetition_penalty': 1.05,
            'max_tokens': 4000
        }

        logger.info(f"🔄 執行 {results['test_count']} 次 API 請求...\n")

        for i in range(results['test_count']):
            logger.info(f"  請求 {i+1}/{results['test_count']}")

            start_time = time.time()
            try:
                outline, cost, score = tester.test_params(params)
                response_time = time.time() - start_time

                results['success_count'] += 1
                results['response_times'].append(response_time)

                logger.info(f"    ✅ 成功 ({response_time:.1f}秒)")
                time.sleep(2)

            except Exception as e:
                response_time = time.time() - start_time
                results['failure_count'] += 1

                logger.error(f"    ❌ 失敗: {e}")
                continue

        # 分析結果
        success_rate = results['success_count'] / results['test_count']

        if results['response_times']:
            avg_response_time = statistics.mean(results['response_times'])
            max_response_time = max(results['response_times'])
            min_response_time = min(results['response_times'])
        else:
            avg_response_time = max_response_time = min_response_time = 0

        results['success_rate'] = success_rate
        results['avg_response_time'] = avg_response_time
        results['max_response_time'] = max_response_time
        results['min_response_time'] = min_response_time

        logger.info(f"\n📊 穩定性分析:")
        logger.info(f"  成功: {results['success_count']}/{results['test_count']} ({success_rate:.1%})")
        logger.info(f"  失敗: {results['failure_count']}/{results['test_count']}")
        logger.info(f"  平均響應時間: {avg_response_time:.1f}秒")
        logger.info(f"  最快響應: {min_response_time:.1f}秒")
        logger.info(f"  最慢響應: {max_response_time:.1f}秒")

        # 判斷狀態
        if success_rate < 0.8:
            results['status'] = 'critical'
            results['issues'].append(f'成功率過低 ({success_rate:.1%})')
            logger.error(f"\n❌ API 不穩定：成功率 {success_rate:.1%} < 80%\n")
        elif success_rate < 0.95:
            results['status'] = 'warning'
            results['issues'].append(f'成功率偏低 ({success_rate:.1%})')
            logger.warning(f"\n⚠️ API 穩定性一般：成功率 {success_rate:.1%} < 95%\n")
        else:
            results['status'] = 'healthy'
            logger.info(f"\n✅ API 穩定性良好：成功率 {success_rate:.1%}\n")

        return results

    def run_all_checks(self):
        """執行所有檢查"""
        logger.info("\n" + "="*60)
        logger.info("🏥 開始系統健康檢查")
        logger.info("="*60 + "\n")

        start_time = time.time()

        # 執行各項檢查
        self.report['checks']['glm4_metrics'] = self.check_glm4_metrics()
        self.report['checks']['param_impact'] = self.check_param_impact()
        self.report['checks']['scoring_consistency'] = self.check_scoring_consistency()
        self.report['checks']['api_stability'] = self.check_api_stability()

        # 計算整體狀態
        statuses = [check['status'] for check in self.report['checks'].values()]

        if 'critical' in statuses:
            self.report['overall_status'] = 'critical'
        elif 'warning' in statuses:
            self.report['overall_status'] = 'warning'
        else:
            self.report['overall_status'] = 'healthy'

        # 保存報告
        total_time = time.time() - start_time
        self.report['total_time'] = total_time

        report_file = self.output_dir / f"health_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, ensure_ascii=False, indent=2)

        # 生成摘要
        self._print_summary(total_time, report_file)

    def _print_summary(self, total_time: float, report_file: Path):
        """列印摘要"""
        logger.info("\n" + "="*60)
        logger.info("📋 健康檢查摘要")
        logger.info("="*60)

        for check_name, check_result in self.report['checks'].items():
            status = check_result['status']
            status_emoji = {
                'healthy': '✅',
                'warning': '⚠️',
                'critical': '❌',
                'unknown': '❓'
            }.get(status, '❓')

            logger.info(f"{status_emoji} {check_name}: {status.upper()}")

            if check_result.get('issues'):
                for issue in check_result['issues']:
                    logger.info(f"    - {issue}")

        logger.info(f"\n整體狀態: {self.report['overall_status'].upper()}")
        logger.info(f"總耗時: {total_time:.1f}秒")
        logger.info(f"報告已保存: {report_file}")
        logger.info("="*60 + "\n")


def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='系統健康檢查')
    parser.add_argument(
        '--check',
        choices=['glm4-metrics', 'param-impact', 'scoring-consistency', 'api-stability', 'all'],
        default='all',
        help='指定檢查項目（默認: all）'
    )

    args = parser.parse_args()

    # 獲取 API Key
    import os
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("SILICONFLOW_API_KEY")

    if not api_key:
        logger.error("❌ 找不到 SILICONFLOW_API_KEY 環境變量")
        return

    # 創建檢查器
    checker = SystemHealthChecker(api_key)

    # 執行檢查
    if args.check == 'all':
        checker.run_all_checks()
    elif args.check == 'glm4-metrics':
        result = checker.check_glm4_metrics()
        checker.report['checks']['glm4_metrics'] = result
    elif args.check == 'param-impact':
        result = checker.check_param_impact()
        checker.report['checks']['param_impact'] = result
    elif args.check == 'scoring-consistency':
        result = checker.check_scoring_consistency()
        checker.report['checks']['scoring_consistency'] = result
    elif args.check == 'api-stability':
        result = checker.check_api_stability()
        checker.report['checks']['api_stability'] = result


if __name__ == "__main__":
    main()
