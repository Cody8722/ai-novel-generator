#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GLM-4 超大規模參數測試系統

特性：
- 支持 600+ 組參數測試
- 分批執行（避免 API 過載）
- 斷點續傳（支持中斷恢復）
- 實時進度保存
- 詳細分析報告

使用方法：
    # 執行單個批次
    python tests/test_glm4_params_mega.py --batch 0

    # 執行所有批次
    python tests/test_glm4_params_mega.py --run-all

    # 從檢查點恢復
    python tests/test_glm4_params_mega.py --resume

    # 快速模式（僅生成大綱）
    python tests/test_glm4_params_mega.py --run-all --quick
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import time
import random
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Tuple
from tests.test_glm4_params import GLM4ParamsTester

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MegaParamsTester:
    """超大規模參數測試器"""

    def __init__(self, api_key: str, quick_mode: bool = False, batch_size: int = 50):
        """
        初始化超大規模測試器

        Args:
            api_key: API 金鑰
            quick_mode: 快速模式（僅生成大綱）
            batch_size: 每批測試數量
        """
        self.api_key = api_key
        self.quick_mode = quick_mode
        self.batch_size = batch_size
        # 批次數量會在生成參數網格後自動計算

        # 創建輸出目錄
        self.output_dir = Path(__file__).parent.parent / "test_results" / "mega_test"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 檢查點文件
        self.checkpoint_file = self.output_dir / "checkpoint.json"

        # 生成參數網格
        logger.info("🔧 生成參數網格...")
        self.param_grid = self.generate_param_grid()

        # 自動計算批次數量
        import math
        self.total_batches = math.ceil(len(self.param_grid) / self.batch_size)

        logger.info(f"✅ 參數網格生成完成：{len(self.param_grid)} 組參數")
        logger.info(f"   批次設置：{self.total_batches} 批 x {self.batch_size} 組/批")

    def generate_param_grid(self) -> List[Dict]:
        """
        生成參數網格（智能採樣）

        Returns:
            參數列表
        """
        param_grid = []

        # 階段 1: 粗略採樣（55 組）- 快速找出大致區間
        param_grid.extend(self._coarse_sampling())

        # 階段 2: 精細採樣（175 組）- 在最佳區間內細化
        param_grid.extend(self._fine_sampling())

        # 階段 3: 驗證採樣（75 組）- 驗證假設
        param_grid.extend(self._validation_sampling())

        logger.info(f"  階段 1 (粗略採樣): {len([p for p in param_grid if p.get('stage') == 'coarse'])} 組")
        logger.info(f"  階段 2 (精細採樣): {len([p for p in param_grid if p.get('stage') == 'fine'])} 組")
        logger.info(f"  階段 3 (驗證採樣): {len([p for p in param_grid if p.get('stage') == 'validation'])} 組")

        return param_grid

    def _coarse_sampling(self) -> List[Dict]:
        """
        粗略採樣：快速找出大致區間

        Returns:
            粗略採樣參數列表
        """
        params_list = []

        # Temperature 主導測試
        logger.info("  生成 Temperature 主導測試...")
        for temp in [0.4, 0.5, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95]:
            params_list.append({
                'temperature': temp,
                'top_p': 0.9,
                'repetition_penalty': 1.05,
                'max_tokens': 4000,
                'stage': 'coarse',
                'focus': 'temperature'
            })

        # Top_P 主導測試
        logger.info("  生成 Top_P 主導測試...")
        for top_p in [0.8, 0.82, 0.85, 0.88, 0.9, 0.92, 0.95, 0.98]:
            params_list.append({
                'temperature': 0.7,
                'top_p': top_p,
                'repetition_penalty': 1.05,
                'max_tokens': 4000,
                'stage': 'coarse',
                'focus': 'top_p'
            })

        # Repetition Penalty 主導測試
        logger.info("  生成 Repetition Penalty 主導測試...")
        for penalty in [0.95, 1.0, 1.03, 1.05, 1.08, 1.1, 1.15, 1.2]:
            params_list.append({
                'temperature': 0.7,
                'top_p': 0.9,
                'repetition_penalty': penalty,
                'max_tokens': 4000,
                'stage': 'coarse',
                'focus': 'penalty'
            })

        # Max Tokens 主導測試
        logger.info("  生成 Max Tokens 主導測試...")
        for tokens in [3000, 3500, 4000, 4500, 5000, 5500, 6000]:
            params_list.append({
                'temperature': 0.7,
                'top_p': 0.9,
                'repetition_penalty': 1.05,
                'max_tokens': tokens,
                'stage': 'coarse',
                'focus': 'max_tokens'
            })

        # 組合測試 - Temperature x Top_P
        logger.info("  生成組合測試（Temperature x Top_P）...")
        for temp in [0.6, 0.7, 0.8]:
            for top_p in [0.85, 0.9, 0.95]:
                params_list.append({
                    'temperature': temp,
                    'top_p': top_p,
                    'repetition_penalty': 1.05,
                    'max_tokens': 4000,
                    'stage': 'coarse',
                    'focus': 'temp_x_topp'
                })

        # 組合測試 - Temperature x Penalty
        logger.info("  生成組合測試（Temperature x Penalty）...")
        for temp in [0.6, 0.7, 0.8]:
            for penalty in [1.0, 1.05, 1.1]:
                params_list.append({
                    'temperature': temp,
                    'top_p': 0.9,
                    'repetition_penalty': penalty,
                    'max_tokens': 4000,
                    'stage': 'coarse',
                    'focus': 'temp_x_penalty'
                })

        # 極端值測試
        logger.info("  生成極端值測試...")
        extreme_params = [
            # 超保守
            {'temperature': 0.3, 'top_p': 0.8, 'repetition_penalty': 0.9, 'max_tokens': 3000},
            # 超激進
            {'temperature': 1.0, 'top_p': 0.99, 'repetition_penalty': 1.3, 'max_tokens': 7000},
            # 極低創意
            {'temperature': 0.4, 'top_p': 0.8, 'repetition_penalty': 1.2, 'max_tokens': 4000},
            # 極高創意
            {'temperature': 0.95, 'top_p': 0.98, 'repetition_penalty': 0.95, 'max_tokens': 5000},
        ]

        for params in extreme_params:
            params['stage'] = 'coarse'
            params['focus'] = 'extreme'
            params_list.append(params)

        return params_list

    def _fine_sampling(self) -> List[Dict]:
        """
        精細採樣：在最佳區間內細化

        Returns:
            精細採樣參數列表
        """
        params_list = []

        # 基於初步結果，假設最佳區間為：
        # Temperature: 0.65-0.75
        # Top_P: 0.88-0.92
        # Penalty: 1.03-1.08
        # Max_Tokens: 4000-5000

        logger.info("  生成精細採樣（Temperature 細化）...")
        for temp in [0.65, 0.67, 0.69, 0.71, 0.73, 0.75]:
            for top_p in [0.88, 0.9, 0.92]:
                for penalty in [1.03, 1.05, 1.08]:
                    params_list.append({
                        'temperature': temp,
                        'top_p': top_p,
                        'repetition_penalty': penalty,
                        'max_tokens': 4000,
                        'stage': 'fine',
                        'focus': 'optimal_range'
                    })

        logger.info("  生成精細採樣（Top_P 細化）...")
        for top_p in [0.86, 0.87, 0.88, 0.89, 0.9, 0.91, 0.92, 0.93]:
            for penalty in [1.03, 1.05, 1.08]:
                params_list.append({
                    'temperature': 0.7,
                    'top_p': top_p,
                    'repetition_penalty': penalty,
                    'max_tokens': 4000,
                    'stage': 'fine',
                    'focus': 'topp_refined'
                })

        logger.info("  生成精細採樣（Penalty 細化）...")
        for penalty in [1.01, 1.02, 1.03, 1.04, 1.05, 1.06, 1.07, 1.08, 1.09]:
            params_list.append({
                'temperature': 0.7,
                'top_p': 0.9,
                'repetition_penalty': penalty,
                'max_tokens': 4000,
                'stage': 'fine',
                'focus': 'penalty_refined'
            })

        logger.info("  生成精細採樣（Max_Tokens 細化）...")
        for tokens in [3800, 4000, 4200, 4400, 4600, 4800, 5000]:
            params_list.append({
                'temperature': 0.7,
                'top_p': 0.9,
                'repetition_penalty': 1.05,
                'max_tokens': tokens,
                'stage': 'fine',
                'focus': 'tokens_refined'
            })

        # 四維組合（最佳區間內的全組合）
        logger.info("  生成精細採樣（四維組合）...")
        for temp in [0.67, 0.7, 0.73]:
            for top_p in [0.88, 0.9, 0.92]:
                for penalty in [1.03, 1.05, 1.08]:
                    for tokens in [4000, 4500, 5000]:
                        params_list.append({
                            'temperature': temp,
                            'top_p': top_p,
                            'repetition_penalty': penalty,
                            'max_tokens': tokens,
                            'stage': 'fine',
                            'focus': '4d_combination'
                        })

        return params_list

    def _validation_sampling(self) -> List[Dict]:
        """
        驗證採樣：驗證假設

        Returns:
            驗證採樣參數列表
        """
        params_list = []

        # 假設 1：最佳參數附近重複測試（驗證穩定性）
        logger.info("  生成驗證採樣（穩定性測試）...")
        best_params = {
            'temperature': 0.7,
            'top_p': 0.9,
            'repetition_penalty': 1.05,
            'max_tokens': 4000
        }

        for i in range(20):  # 重複 20 次
            params = best_params.copy()
            params['stage'] = 'validation'
            params['focus'] = 'stability'
            params['repeat_id'] = i
            params_list.append(params)

        # 假設 2：微調測試（最佳參數周圍的微小變化）
        logger.info("  生成驗證採樣（微調測試）...")
        for temp_delta in [-0.02, -0.01, 0, 0.01, 0.02]:
            for topp_delta in [-0.01, 0, 0.01]:
                for penalty_delta in [-0.01, 0, 0.01]:
                    params_list.append({
                        'temperature': 0.7 + temp_delta,
                        'top_p': 0.9 + topp_delta,
                        'repetition_penalty': 1.05 + penalty_delta,
                        'max_tokens': 4000,
                        'stage': 'validation',
                        'focus': 'fine_tuning'
                    })

        # 假設 3：對比測試（與 R1 最佳參數對比）
        logger.info("  生成驗證採樣（R1 對比）...")
        r1_style_params = [
            {'temperature': 0.6, 'top_p': 0.95, 'repetition_penalty': 1.0, 'max_tokens': 3500},
            {'temperature': 0.65, 'top_p': 0.92, 'repetition_penalty': 1.02, 'max_tokens': 4000},
        ]

        for params in r1_style_params:
            for i in range(5):  # 每組重複 5 次
                test_params = params.copy()
                test_params['stage'] = 'validation'
                test_params['focus'] = 'r1_comparison'
                test_params['repeat_id'] = i
                params_list.append(test_params)

        return params_list

    def load_checkpoint(self) -> Dict:
        """
        加載檢查點

        Returns:
            檢查點數據
        """
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'completed_batches': [],
            'current_batch': None,
            'batch_results': {},
            'start_time': datetime.now().isoformat()
        }

    def save_checkpoint(self, checkpoint_data: Dict):
        """
        保存檢查點

        Args:
            checkpoint_data: 檢查點數據
        """
        with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)

    def test_single_param(self, params: Dict) -> Dict:
        """
        測試單組參數

        Args:
            params: 參數配置

        Returns:
            測試結果
        """
        # 提取測試參數
        test_params = {
            'temperature': params['temperature'],
            'top_p': params['top_p'],
            'repetition_penalty': params['repetition_penalty'],
            'max_tokens': params['max_tokens']
        }

        # 創建測試器
        tester = GLM4ParamsTester(
            self.api_key,
            quick_mode=self.quick_mode,
            enable_ai_review=False,
            debug_mode=False
        )

        try:
            # 執行測試
            outline, cost, score = tester.test_params(test_params)

            # 返回結果
            result = {
                'params': test_params,
                'stage': params.get('stage', 'unknown'),
                'focus': params.get('focus', 'unknown'),
                'score': score,
                'cost': cost,
                'outline_length': len(outline) if outline else 0,
                'timestamp': datetime.now().isoformat(),
                'success': True
            }

            # 添加重複 ID（如果有）
            if 'repeat_id' in params:
                result['repeat_id'] = params['repeat_id']

            return result

        except Exception as e:
            logger.error(f"測試失敗: {e}")
            return {
                'params': test_params,
                'stage': params.get('stage', 'unknown'),
                'focus': params.get('focus', 'unknown'),
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'success': False
            }

    def run_batch(self, batch_num: int) -> List[Dict]:
        """
        執行單批測試

        Args:
            batch_num: 批次編號

        Returns:
            批次結果列表
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"🚀 開始批次 {batch_num + 1}/{self.total_batches}")
        logger.info(f"{'='*60}\n")

        # 加載檢查點
        checkpoint = self.load_checkpoint()

        # 檢查是否已完成
        if batch_num in checkpoint.get('completed_batches', []):
            logger.info(f"✅ 批次 {batch_num + 1} 已完成，跳過")
            return checkpoint['batch_results'].get(str(batch_num), [])

        # 獲取當前批次的參數
        start_idx = batch_num * self.batch_size
        end_idx = min(start_idx + self.batch_size, len(self.param_grid))
        batch_params = self.param_grid[start_idx:end_idx]

        logger.info(f"📋 批次參數數量: {len(batch_params)}")
        logger.info(f"📍 參數索引範圍: {start_idx} - {end_idx - 1}\n")

        results = []
        for i, params in enumerate(batch_params):
            logger.info(f"🔬 測試 {i + 1}/{len(batch_params)} (總進度: {start_idx + i + 1}/{len(self.param_grid)})")
            logger.info(f"   參數: T={params['temperature']}, P={params['top_p']}, Pen={params['repetition_penalty']}, Tok={params['max_tokens']}")
            logger.info(f"   階段: {params.get('stage', 'unknown')}, 焦點: {params.get('focus', 'unknown')}")

            try:
                result = self.test_single_param(params)
                results.append(result)

                if result['success']:
                    logger.info(f"   ✅ 成功 - 總分: {result['score']['total_score']:.0f}/120")
                else:
                    logger.info(f"   ❌ 失敗 - {result.get('error', 'Unknown error')}")

                # 每 10 個測試保存一次檢查點
                if (i + 1) % 10 == 0:
                    checkpoint['current_batch'] = batch_num
                    checkpoint['batch_results'][str(batch_num)] = results
                    self.save_checkpoint(checkpoint)
                    logger.info(f"   💾 檢查點已保存 ({i + 1}/{len(batch_params)})")

                # API 延遲（避免過載）
                delay = random.uniform(3, 5)
                logger.info(f"   ⏳ 等待 {delay:.1f} 秒...\n")
                time.sleep(delay)

            except Exception as e:
                logger.error(f"   ❌ 測試異常: {e}\n")
                continue

        # 保存批次結果
        batch_file = self.output_dir / f"batch_{batch_num:02d}_results.json"
        with open(batch_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        # 更新檢查點
        checkpoint['completed_batches'].append(batch_num)
        checkpoint['batch_results'][str(batch_num)] = results
        checkpoint['current_batch'] = None
        self.save_checkpoint(checkpoint)

        # 計算批次統計
        successful = sum(1 for r in results if r.get('success', False))
        failed = len(results) - successful

        logger.info(f"\n{'='*60}")
        logger.info(f"✅ 批次 {batch_num + 1} 完成")
        logger.info(f"{'='*60}")
        logger.info(f"成功: {successful}/{len(results)}")
        logger.info(f"失敗: {failed}/{len(results)}")
        logger.info(f"結果已保存: {batch_file}\n")

        return results

    def run_all_batches(self):
        """執行所有批次"""
        logger.info("\n" + "="*60)
        logger.info("🎯 開始超大規模參數測試")
        logger.info("="*60)
        logger.info(f"總參數組數: {len(self.param_grid)}")
        logger.info(f"批次數量: {self.total_batches}")
        logger.info(f"每批大小: {self.batch_size}")
        logger.info(f"快速模式: {'是' if self.quick_mode else '否'}")
        logger.info(f"輸出目錄: {self.output_dir}")
        logger.info("="*60 + "\n")

        start_time = time.time()

        for batch_num in range(self.total_batches):
            self.run_batch(batch_num)

            # 批次間休息（最後一批除外）
            if batch_num < self.total_batches - 1:
                rest_time = 300  # 5 分鐘
                logger.info(f"⏸️  批次間休息 {rest_time // 60} 分鐘...")
                logger.info(f"   下一批次將於 {datetime.now().strftime('%H:%M:%S')} 後開始\n")
                time.sleep(rest_time)

        # 計算總耗時
        total_time = time.time() - start_time
        hours = int(total_time // 3600)
        minutes = int((total_time % 3600) // 60)
        seconds = int(total_time % 60)

        logger.info("\n" + "="*60)
        logger.info("🎉 所有批次執行完成！")
        logger.info("="*60)
        logger.info(f"總耗時: {hours}小時 {minutes}分鐘 {seconds}秒")
        logger.info(f"結果目錄: {self.output_dir}")
        logger.info("="*60 + "\n")

        # 生成快速摘要
        self.generate_quick_summary()

    def generate_quick_summary(self):
        """生成快速摘要"""
        logger.info("📊 生成測試摘要...")

        # 加載所有批次結果
        all_results = []
        for batch_num in range(self.total_batches):
            batch_file = self.output_dir / f"batch_{batch_num:02d}_results.json"
            if batch_file.exists():
                with open(batch_file, 'r', encoding='utf-8') as f:
                    all_results.extend(json.load(f))

        # 計算統計
        total_tests = len(all_results)
        successful = sum(1 for r in all_results if r.get('success', False))
        failed = total_tests - successful

        if successful > 0:
            avg_score = sum(r['score']['total_score'] for r in all_results if r.get('success', False)) / successful
            max_score = max(r['score']['total_score'] for r in all_results if r.get('success', False))
            min_score = min(r['score']['total_score'] for r in all_results if r.get('success', False))
        else:
            avg_score = max_score = min_score = 0

        # 保存摘要
        summary = {
            'total_tests': total_tests,
            'successful': successful,
            'failed': failed,
            'success_rate': successful / total_tests if total_tests > 0 else 0,
            'avg_score': avg_score,
            'max_score': max_score,
            'min_score': min_score,
            'timestamp': datetime.now().isoformat()
        }

        summary_file = self.output_dir / "quick_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        logger.info(f"\n{'='*60}")
        logger.info("📈 測試摘要")
        logger.info(f"{'='*60}")
        logger.info(f"總測試數: {total_tests}")
        logger.info(f"成功: {successful} ({successful/total_tests*100:.1f}%)")
        logger.info(f"失敗: {failed} ({failed/total_tests*100:.1f}%)")
        logger.info(f"平均分數: {avg_score:.1f}/120")
        logger.info(f"最高分數: {max_score:.1f}/120")
        logger.info(f"最低分數: {min_score:.1f}/120")
        logger.info(f"{'='*60}\n")
        logger.info(f"摘要已保存: {summary_file}")
        logger.info(f"\n💡 提示: 運行 'python tests/analyze_mega_results.py' 生成詳細分析報告\n")


def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='GLM-4 超大規模參數測試')

    parser.add_argument('--batch', type=int, help='執行指定批次（0-11）')
    parser.add_argument('--run-all', action='store_true', help='執行所有批次')
    parser.add_argument('--resume', action='store_true', help='從檢查點恢復')
    parser.add_argument('--quick', action='store_true', help='快速模式（僅生成大綱）')
    parser.add_argument('--batch-size', type=int, default=50, help='每批測試數量（默認 50）')

    args = parser.parse_args()

    # 獲取 API Key
    import os
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("SILICONFLOW_API_KEY")

    if not api_key:
        logger.error("❌ 找不到 SILICONFLOW_API_KEY 環境變量")
        return

    # 創建測試器
    tester = MegaParamsTester(api_key, quick_mode=args.quick, batch_size=args.batch_size)

    if args.run_all:
        # 執行所有批次
        tester.run_all_batches()
    elif args.resume:
        # 從檢查點恢復
        checkpoint = tester.load_checkpoint()
        completed = checkpoint.get('completed_batches', [])
        logger.info(f"已完成批次: {completed}")

        for batch_num in range(tester.total_batches):
            if batch_num not in completed:
                logger.info(f"從批次 {batch_num + 1} 恢復...")
                tester.run_batch(batch_num)
    elif args.batch is not None:
        # 執行指定批次
        if 0 <= args.batch < tester.total_batches:
            tester.run_batch(args.batch)
        else:
            logger.error(f"❌ 批次編號無效: {args.batch}（有效範圍: 0-{tester.total_batches - 1}）")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
