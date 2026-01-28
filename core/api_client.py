# -*- coding: utf-8 -*-
"""
AI 小說生成器 - API 客戶端
"""

import requests
import time
import logging
import re
from typing import Dict, Optional
from config import API_CONFIG, MODELS

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SiliconFlowClient:
    def __init__(self, api_key: str, model: str = None):
        self.api_key = api_key
        self.model = model or API_CONFIG['default_model']
        self.base_url = API_CONFIG['base_url']
        self.timeout = API_CONFIG['timeout']
        self.max_retries = API_CONFIG['max_retries']

        # 動態參數（可通過 update_params 更新）
        self._dynamic_params = {
            'temperature': None,
            'top_p': None,
            'repetition_penalty': None,
            'max_tokens': None
        }
        self._dynamic_params_enabled = False

        # 統計
        self.total_tokens_input = 0
        self.total_tokens_output = 0
        self.total_cost = 0.0
        self.request_count = 0
        self._param_change_count = 0

    def update_params(
        self,
        new_params: Dict,
        log_change: bool = True
    ) -> Dict:
        """
        動態更新生成參數

        支持更新的參數：
        - temperature: 溫度參數（控制隨機性）
        - top_p: 核採樣參數（控制詞彙多樣性）
        - repetition_penalty: 重複懲罰（避免重複內容）
        - max_tokens: 最大生成 token 數

        Args:
            new_params: 新參數字典
            log_change: 是否記錄參數變更日誌

        Returns:
            更新後的參數字典

        Example:
            client.update_params({
                'temperature': 0.68,
                'top_p': 0.91,
                'repetition_penalty': 1.06
            })
        """
        old_params = self._dynamic_params.copy()
        changed = []

        for key in ['temperature', 'top_p', 'repetition_penalty', 'max_tokens']:
            if key in new_params and new_params[key] is not None:
                old_value = self._dynamic_params.get(key)
                new_value = new_params[key]

                if old_value != new_value:
                    self._dynamic_params[key] = new_value
                    changed.append(f"{key}: {old_value} -> {new_value}")

        if changed:
            self._dynamic_params_enabled = True
            self._param_change_count += 1

            if log_change:
                logger.info(f"參數更新 [#{self._param_change_count}]: {', '.join(changed)}")

        return self._dynamic_params.copy()

    def get_current_params(self) -> Dict:
        """
        獲取當前動態參數

        Returns:
            當前參數字典
        """
        return {k: v for k, v in self._dynamic_params.items() if v is not None}

    def reset_params(self) -> None:
        """重置動態參數為默認值"""
        self._dynamic_params = {
            'temperature': None,
            'top_p': None,
            'repetition_penalty': None,
            'max_tokens': None
        }
        self._dynamic_params_enabled = False
        logger.info("動態參數已重置")

    def enable_dynamic_params(self) -> None:
        """啟用動態參數"""
        self._dynamic_params_enabled = True
        logger.info("動態參數已啟用")

    def disable_dynamic_params(self) -> None:
        """禁用動態參數（使用默認參數）"""
        self._dynamic_params_enabled = False
        logger.info("動態參數已禁用")

    def is_dynamic_params_enabled(self) -> bool:
        """檢查動態參數是否啟用"""
        return self._dynamic_params_enabled

    def _merge_params(self, kwargs: Dict) -> Dict:
        """
        合併動態參數和調用時參數

        優先級：調用時參數 > 動態參數 > 默認值

        Args:
            kwargs: 調用時傳入的參數

        Returns:
            合併後的參數字典
        """
        merged = kwargs.copy()

        if self._dynamic_params_enabled:
            for key, value in self._dynamic_params.items():
                if value is not None and key not in kwargs:
                    merged[key] = value

        return merged

    def generate(self, prompt: str, model: str = None, **kwargs) -> str:
        """
        生成文本（簡化版，直接返回字符串）

        Args:
            prompt: 提示詞
            model: 指定模型（可選）
            **kwargs: 其他參數（temperature, max_tokens 等）

        Returns:
            生成的文本內容
        """
        target_model = model or self.model
        messages = [{"role": "user", "content": prompt}]

        # 合併動態參數
        merged_kwargs = self._merge_params(kwargs)

        payload = {
            "model": target_model,
            "messages": messages,
            "stream": False,
            **merged_kwargs
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.base_url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout
                )
                response.raise_for_status()

                content = response.json()['choices'][0]['message']['content']

                # 🔥 DeepSeek R1 專用濾網：移除 <think> 標籤
                if '<think>' in content:
                    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()

                # 更新統計
                usage = response.json().get('usage', {})
                self.total_tokens_input += usage.get('prompt_tokens', 0)
                self.total_tokens_output += usage.get('completion_tokens', 0)
                self.request_count += 1

                return content

            except Exception as e:
                logger.warning(f"請求失敗 ({attempt+1}/{self.max_retries}): {e}")
                time.sleep(2)

        raise Exception("API 調用多次失敗")

    def generate_with_details(self, prompt: str, temperature: float = 0.8, max_tokens: int = 5000,
                             model: str = None, top_p: float = None, repetition_penalty: float = None) -> Dict:
        """
        生成文本（詳細版，返回完整信息）

        Args:
            prompt: 提示詞
            temperature: 溫度參數
            max_tokens: 最大 token 數
            model: 指定模型（可選，默認使用初始化時的模型）
            top_p: 核採樣參數（可選）
            repetition_penalty: 重複懲罰參數（可選）

        Returns:
            包含生成結果的字典
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        target_model = model or self.model

        data = {
            'model': target_model,
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'temperature': temperature,
            'max_tokens': max_tokens
        }

        # 添加可選參數
        if top_p is not None:
            data['top_p'] = top_p
        if repetition_penalty is not None:
            data['repetition_penalty'] = repetition_penalty

        last_error = None
        for attempt in range(self.max_retries):
            try:
                logger.info(f"發送 API 請求（第 {attempt + 1}/{self.max_retries} 次）")

                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=data,
                    timeout=self.timeout
                )

                if response.status_code != 200:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    logger.error(error_msg)
                    raise Exception(error_msg)

                result = response.json()

                if 'choices' not in result or len(result['choices']) == 0:
                    raise Exception(f"API 回應格式異常: {result}")

                content = result['choices'][0]['message']['content']

                # 🔥 DeepSeek R1 專用濾網：移除 <think> 標籤
                if '<think>' in content:
                    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()

                usage = result.get('usage', {})
                tokens_input = usage.get('prompt_tokens', 0)
                tokens_output = usage.get('completion_tokens', 0)

                cost = self._calculate_cost(tokens_input, tokens_output)

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
                    time.sleep(2 ** attempt)
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

        error_msg = f"API 調用失敗（已重試 {self.max_retries} 次）: {last_error}"
        logger.error(error_msg)
        raise Exception(error_msg)

    def _calculate_cost(self, tokens_input: int, tokens_output: int) -> float:
        """計算成本"""
        if self.model not in MODELS:
            logger.warning(f"未知模型 {self.model}，無法計算成本")
            return 0.0

        model_info = MODELS[self.model]
        price_input = model_info['price_input']
        price_output = model_info['price_output']

        cost_input = (tokens_input / 1000) * price_input
        cost_output = (tokens_output / 1000) * price_output

        return cost_input + cost_output

    def get_statistics(self):
        """獲取統計信息"""
        return {
            'model': self.model,
            'request_count': self.request_count,
            'total_tokens': self.total_tokens_input + self.total_tokens_output,
            'total_cost': 0.0,  # 免費模型，成本為 0
            'param_change_count': self._param_change_count,
            'dynamic_params_enabled': self._dynamic_params_enabled,
            'current_params': self.get_current_params()
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
        print(f"  ├─ 輸入............... {self.total_tokens_input:,}")
        print(f"  └─ 輸出............... {self.total_tokens_output:,}")
        print(f"總成本.................. ¥{stats['total_cost']:.4f} (免費)")
        print("-"*60)
        print(f"動態參數................ {'✅ 啟用' if stats['dynamic_params_enabled'] else '❌ 禁用'}")
        print(f"參數變更次數............ {stats['param_change_count']}")
        if stats['current_params']:
            print("當前參數:")
            for key, value in stats['current_params'].items():
                print(f"  └─ {key}: {value}")
        print("="*60 + "\n")


if __name__ == '__main__':
    # 測試
    import os
    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv('SILICONFLOW_API_KEY')

    if api_key:
        client = SiliconFlowClient(api_key)

        # 測試請求
        result = client.generate("請用一句話介紹自己。", max_tokens=100)
        print("生成結果:", result)

        # 打印統計
        client.print_statistics()
    else:
        print("請設定 SILICONFLOW_API_KEY 環境變數")
