# -*- coding: utf-8 -*-
"""
AI 小說生成器 - API 客戶端
封裝矽基流動 API，提供穩定的調用介面
"""

import requests
import time
import logging
from typing import Dict, Optional

from config import API_CONFIG, MODELS


# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SiliconFlowClient:
    """
    矽基流動 API 客戶端
    提供穩定的 API 調用，包含錯誤處理、重試機制和成本追蹤
    """

    def __init__(self, api_key: str, model: str = None):
        """
        初始化 API 客戶端

        Args:
            api_key: 矽基流動 API Key
            model: 模型名稱，默認使用 config 中的配置
        """
        self.api_key = api_key
        self.model = model or API_CONFIG['default_model']
        self.base_url = API_CONFIG['base_url']
        self.timeout = API_CONFIG['timeout']
        self.max_retries = API_CONFIG['max_retries']

        # 統計信息
        self.total_tokens_input = 0
        self.total_tokens_output = 0
        self.total_cost = 0.0
        self.request_count = 0

        # 驗證模型是否存在
        if self.model not in MODELS:
            logger.warning(f"模型 {self.model} 不在已知列表中，可能無法計算成本")

        logger.info(f"API 客戶端初始化完成，模型: {self.model}")

    def generate(self, prompt: str, temperature: float = 0.8, max_tokens: int = 5000) -> Dict:
        """
        生成文本

        Args:
            prompt: 提示詞
            temperature: 溫度參數（0-1），越高越隨機
            max_tokens: 最大生成 token 數

        Returns:
            包含生成結果的字典:
            {
                'content': str,      # 生成的文本
                'tokens_input': int, # 輸入 token 數
                'tokens_output': int,# 輸出 token 數
                'cost': float        # 本次成本（人民幣）
            }

        Raises:
            Exception: API 調用失敗
        """
        # 構建請求
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        data = {
            'model': self.model,
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'temperature': temperature,
            'max_tokens': max_tokens
        }

        # 重試邏輯
        last_error = None
        for attempt in range(self.max_retries):
            try:
                logger.info(f"發送 API 請求（第 {attempt + 1}/{self.max_retries} 次）")
                logger.debug(f"提示詞長度: {len(prompt)} 字符")

                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=data,
                    timeout=self.timeout
                )

                # 檢查 HTTP 狀態碼
                if response.status_code != 200:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    logger.error(error_msg)
                    raise Exception(error_msg)

                # 解析回應
                result = response.json()

                # 提取內容
                if 'choices' not in result or len(result['choices']) == 0:
                    raise Exception(f"API 回應格式異常: {result}")

                content = result['choices'][0]['message']['content']

                # 提取 token 使用情況
                usage = result.get('usage', {})
                tokens_input = usage.get('prompt_tokens', 0)
                tokens_output = usage.get('completion_tokens', 0)

                # 計算成本
                cost = self._calculate_cost(tokens_input, tokens_output)

                # 更新統計
                self.total_tokens_input += tokens_input
                self.total_tokens_output += tokens_output
                self.total_cost += cost
                self.request_count += 1

                logger.info(f"API 請求成功")
                logger.info(f"Token 使用: 輸入 {tokens_input}, 輸出 {tokens_output}")
                logger.info(f"本次成本: ¥{cost:.4f}")

                return {
                    'content': content,
                    'tokens_input': tokens_input,
                    'tokens_output': tokens_output,
                    'cost': cost
                }

            except requests.exceptions.Timeout:
                last_error = "請求超時"
                logger.warning(f"請求超時（第 {attempt + 1} 次）")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # 指數退避
                    continue

            except requests.exceptions.ConnectionError:
                last_error = "網路連接失敗"
                logger.warning(f"網路連接失敗（第 {attempt + 1} 次）")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue

            except Exception as e:
                last_error = str(e)
                logger.error(f"API 調用失敗: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue

        # 所有重試都失敗
        error_msg = f"API 調用失敗（已重試 {self.max_retries} 次）: {last_error}"
        logger.error(error_msg)
        raise Exception(error_msg)

    def _calculate_cost(self, tokens_input: int, tokens_output: int) -> float:
        """
        計算成本

        Args:
            tokens_input: 輸入 token 數
            tokens_output: 輸出 token 數

        Returns:
            成本（人民幣）
        """
        if self.model not in MODELS:
            logger.warning(f"未知模型 {self.model}，無法計算成本")
            return 0.0

        model_info = MODELS[self.model]
        price_input = model_info['price_input']
        price_output = model_info['price_output']

        cost_input = (tokens_input / 1000) * price_input
        cost_output = (tokens_output / 1000) * price_output

        return cost_input + cost_output

    def get_statistics(self) -> Dict:
        """
        獲取統計信息

        Returns:
            統計信息字典
        """
        return {
            'model': self.model,
            'request_count': self.request_count,
            'total_tokens_input': self.total_tokens_input,
            'total_tokens_output': self.total_tokens_output,
            'total_tokens': self.total_tokens_input + self.total_tokens_output,
            'total_cost': self.total_cost,
            'avg_tokens_per_request': (
                (self.total_tokens_input + self.total_tokens_output) / self.request_count
                if self.request_count > 0 else 0
            ),
            'avg_cost_per_request': (
                self.total_cost / self.request_count
                if self.request_count > 0 else 0
            )
        }

    def print_statistics(self):
        """打印統計信息"""
        stats = self.get_statistics()

        print("\n" + "="*60)
        print("📊 API 調用統計")
        print("="*60)
        print(f"模型.................... {stats['model']}")
        print(f"請求次數................ {stats['request_count']}")
        print(f"總 Token 使用........... {stats['total_tokens']:,}")
        print(f"  ├─ 輸入............... {stats['total_tokens_input']:,}")
        print(f"  └─ 輸出............... {stats['total_tokens_output']:,}")
        print(f"總成本.................. ¥{stats['total_cost']:.4f}")
        print(f"平均每次請求............ {stats['avg_tokens_per_request']:.0f} tokens")
        print(f"平均每次成本............ ¥{stats['avg_cost_per_request']:.4f}")
        print("="*60 + "\n")


if __name__ == '__main__':
    # 測試（需要有效的 API Key）
    import os
    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv('SILICONFLOW_API_KEY')

    if api_key:
        client = SiliconFlowClient(api_key)

        # 測試請求
        result = client.generate("請用一句話介紹自己。", max_tokens=100)
        print("生成結果:", result['content'])

        # 打印統計
        client.print_statistics()
    else:
        print("請設定 SILICONFLOW_API_KEY 環境變數")
