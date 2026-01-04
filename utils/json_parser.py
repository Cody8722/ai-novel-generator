# -*- coding: utf-8 -*-
"""
AI 小說生成器 - JSON 解析器
強健的 JSON 解析，處理 AI 輸出的各種異常格式
"""

import json
import re


class RobustJSONParser:
    """
    強健的 JSON 解析器
    支援多種容錯策略，確保能解析 AI 生成的不規範 JSON
    """

    def __init__(self):
        """初始化解析器"""
        pass

    def parse(self, response_text):
        """
        嘗試所有可能的解析方式

        Args:
            response_text: AI 回應文本

        Returns:
            解析後的字典或列表

        Raises:
            ValueError: 所有策略都失敗時
        """
        # 策略 1：直接解析
        try:
            return json.loads(response_text)
        except:
            pass

        # 策略 2：提取 ```json``` 包裹的內容
        match = re.search(r'```json\s*\n(.*?)\n```', response_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except:
                pass

        # 策略 3：提取任何 ``` 包裹的內容
        match = re.search(r'```\s*\n(.*?)\n```', response_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except:
                pass

        # 策略 4：找第一個 { 和最後一個 }
        try:
            first = response_text.index('{')
            last = response_text.rindex('}')
            json_str = response_text[first:last+1]
            return json.loads(json_str)
        except:
            pass

        # 策略 5：找第一個 [ 和最後一個 ]
        try:
            first = response_text.index('[')
            last = response_text.rindex(']')
            json_str = response_text[first:last+1]
            return json.loads(json_str)
        except:
            pass

        # 全部失敗
        raise ValueError(f"無法解析 JSON，嘗試了所有策略\n內容預覽:\n{response_text[:200]}...")

    def parse_with_key_mapping(self, response_text, key_map):
        """
        解析並修正 key 名稱

        Args:
            response_text: AI 回應文本
            key_map: key 映射字典 (中文 key → 英文 key)

        Returns:
            修正後的字典或列表
        """
        # 先解析
        data = self.parse(response_text)

        # 遞歸修正 key
        return self._fix_keys(data, key_map)

    def _fix_keys(self, data, key_map):
        """
        遞歸修正 key 名稱（支援中英文混用）

        Args:
            data: 要修正的數據
            key_map: key 映射字典

        Returns:
            修正後的數據
        """
        if isinstance(data, dict):
            fixed = {}
            for k, v in data.items():
                # 找標準 key
                standard_key = key_map.get(k, k)
                fixed[standard_key] = self._fix_keys(v, key_map)
            return fixed

        elif isinstance(data, list):
            return [self._fix_keys(item, key_map) for item in data]

        else:
            return data

    def parse_with_retry(self, response_text, max_attempts=3):
        """
        帶重試的解析

        Args:
            response_text: AI 回應文本
            max_attempts: 最大嘗試次數

        Returns:
            解析後的數據

        Raises:
            ValueError: 多次嘗試後仍失敗
        """
        for attempt in range(max_attempts):
            try:
                return self.parse(response_text)
            except Exception as e:
                if attempt == max_attempts - 1:
                    raise ValueError(f"多次嘗試後仍無法解析 JSON: {e}")
                # 可以在這裡添加清洗邏輯
                continue

        raise ValueError("解析失敗")


# 常用的 key 映射表
COMMON_KEY_MAPPINGS = {
    # 中文 → 英文
    '標題': 'title',
    '卷名': 'title',
    '章節': 'chapter',
    '內容': 'content',
    '摘要': 'summary',
    '角色': 'character',
    '角色名': 'name',
    '性格': 'personality',
    '外貌': 'appearance',

    # 其他可能的變體
    'vol_num': 'volume_number',
    'volume': 'volume_number',
    'name': 'title',
}


if __name__ == '__main__':
    # 測試
    parser = RobustJSONParser()

    # 測試 1：標準 JSON
    test1 = '{"title": "測試", "content": "內容"}'
    print("測試 1:", parser.parse(test1))

    # 測試 2：markdown 包裹
    test2 = '''
    好的，這是 JSON:

    ```json
    {
        "title": "測試",
        "content": "內容"
    }
    ```

    希望對您有幫助！
    '''
    print("測試 2:", parser.parse(test2))

    # 測試 3：中文 key
    test3 = '{"標題": "測試小說", "內容": "這是內容"}'
    print("測試 3:", parser.parse_with_key_mapping(test3, COMMON_KEY_MAPPINGS))
