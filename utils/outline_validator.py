# -*- coding: utf-8 -*-
"""
AI 小說生成器 - 大綱驗證器
使用語義相似度檢測、不可逆事件分析、衝突強度評估等技術驗證章節大綱品質
"""

import logging
import re
from typing import Dict, List, Tuple, Optional

# 嘗試導入 sentence-transformers，優雅降級
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    logging.warning(
        "sentence-transformers 未安裝，相似度檢測將使用基礎方法。"
        "安裝方法: pip install sentence-transformers"
    )


logger = logging.getLogger(__name__)


class OutlineValidator:
    """
    章節大綱驗證器

    功能:
    - 相似度檢測：避免重複劇情
    - 不可逆事件檢測：確保重大事件合理性
    - 衝突強度評估：量化劇情張力
    - 成長指標檢測：追蹤角色發展
    """

    # 不可逆事件關鍵詞（這些事件無法回退）
    IRREVERSIBLE_KEYWORDS = [
        '死亡', '身亡', '喪命', '殺死', '犧牲',
        '摧毀', '毀滅', '崩潰', '覆滅',
        '背叛', '決裂', '訣別',
        '重傷', '殘廢', '失明', '失憶',
        '曝光', '揭露', '公開',
        '突破', '頓悟', '覺醒',
    ]

    # 衝突強度關鍵詞分級
    CONFLICT_KEYWORDS = {
        'low': ['遇見', '對話', '思考', '計劃', '準備', '觀察', '發現'],
        'medium': ['爭執', '質疑', '懷疑', '挑戰', '對抗', '抵抗'],
        'high': ['戰鬥', '決戰', '生死', '危機', '絕境', '崩潰', '背叛'],
    }

    # 成長指標關鍵詞
    GROWTH_KEYWORDS = [
        '領悟', '覺醒', '突破', '掌握', '理解',
        '成長', '進步', '提升', '變強',
        '決心', '覺悟', '改變',
    ]

    def __init__(
        self,
        similarity_threshold: float = 0.85,  # V0.3.1: 0.75 → 0.85 (重試率 -55%)
        use_embeddings: bool = True,
        model_name: str = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
    ):
        """
        初始化驗證器

        Args:
            similarity_threshold: 相似度閾值（0-1），超過視為重複
            use_embeddings: 是否使用語義嵌入（需要 sentence-transformers）
            model_name: 語義模型名稱
        """
        self.similarity_threshold = similarity_threshold
        self.use_embeddings = use_embeddings and EMBEDDINGS_AVAILABLE

        # 載入語義模型
        self.model = None
        if self.use_embeddings:
            try:
                logger.info(f"載入語義模型: {model_name}")
                self.model = SentenceTransformer(model_name)
                logger.info("語義模型載入成功")
            except Exception as e:
                logger.error(f"語義模型載入失敗: {e}")
                self.use_embeddings = False

        logger.info(
            f"大綱驗證器初始化完成 (相似度閾值: {similarity_threshold}, "
            f"使用嵌入: {self.use_embeddings})"
        )

    def validate_chapter_outline(
        self,
        outline: str,
        previous_outlines: List[str],
        chapter_num: int = 1,
        strict_mode: bool = False
    ) -> Dict:
        """
        驗證章節大綱

        Args:
            outline: 當前章節大綱
            previous_outlines: 之前所有章節大綱列表
            chapter_num: 當前章節號
            strict_mode: 嚴格模式（要求更高標準）

        Returns:
            驗證結果字典:
            {
                'is_valid': bool,           # 是否通過驗證
                'similarity_score': float,  # 最高相似度分數
                'similar_chapters': list,   # 相似章節編號列表
                'has_irreversible': bool,   # 是否包含不可逆事件
                'irreversible_events': list,# 不可逆事件列表
                'conflict_intensity': float,# 衝突強度（0-1）
                'has_growth': bool,         # 是否包含成長元素
                'growth_indicators': list,  # 成長指標列表
                'warnings': list,           # 警告訊息
                'errors': list,             # 錯誤訊息
            }
        """
        result = {
            'is_valid': True,
            'similarity_score': 0.0,
            'similar_chapters': [],
            'has_irreversible': False,
            'irreversible_events': [],
            'conflict_intensity': 0.0,
            'has_growth': False,
            'growth_indicators': [],
            'warnings': [],
            'errors': [],
        }

        # 1. 相似度檢測
        if previous_outlines:
            max_similarity = 0.0
            similar_chapters = []

            for i, prev_outline in enumerate(previous_outlines):
                similarity = self._calculate_similarity(outline, prev_outline)

                if similarity > max_similarity:
                    max_similarity = similarity

                # 記錄高相似度章節
                threshold = self.similarity_threshold if not strict_mode else 0.65
                if similarity > threshold:
                    similar_chapters.append(i + 1)

            result['similarity_score'] = max_similarity
            result['similar_chapters'] = similar_chapters

            # 判斷是否過於相似
            if similar_chapters:
                result['warnings'].append(
                    f"大綱與第 {', '.join(map(str, similar_chapters))} 章相似度過高 "
                    f"({max_similarity:.2f})"
                )
                if strict_mode:
                    result['is_valid'] = False
                    result['errors'].append("嚴格模式: 不允許高相似度大綱")

        # 2. 不可逆事件檢測
        has_irreversible, events = self._detect_irreversible_events(outline)
        result['has_irreversible'] = has_irreversible
        result['irreversible_events'] = events

        if has_irreversible:
            result['warnings'].append(
                f"檢測到不可逆事件: {', '.join(events)}，請確保後續章節考慮此影響"
            )

        # 3. 衝突強度評估
        intensity = self._assess_conflict_intensity(outline)
        result['conflict_intensity'] = intensity

        # 衝突強度過低警告（第3章後開始檢查）
        if chapter_num > 3 and intensity < 0.2:
            result['warnings'].append(
                f"衝突強度較低 ({intensity:.2f})，故事可能缺乏張力"
            )

        # 4. 成長指標檢測
        has_growth, indicators = self._detect_growth_indicators(outline)
        result['has_growth'] = has_growth
        result['growth_indicators'] = indicators

        # 長期無成長警告（每5章至少要有1次成長）
        if chapter_num > 5 and chapter_num % 5 == 0 and not has_growth:
            result['warnings'].append(
                "建議加入角色成長或突破元素，避免故事停滯"
            )

        # 5. 長度檢查
        if len(outline) < 50:
            result['warnings'].append("大綱過短，可能缺少細節")

        logger.info(
            f"第 {chapter_num} 章大綱驗證: "
            f"相似度={result['similarity_score']:.2f}, "
            f"衝突強度={intensity:.2f}, "
            f"不可逆事件={len(events)}, "
            f"成長指標={len(indicators)}"
        )

        return result

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        計算兩段文本的相似度

        Args:
            text1: 文本1
            text2: 文本2

        Returns:
            相似度分數（0-1）
        """
        if self.use_embeddings and self.model:
            try:
                # 使用語義嵌入計算相似度
                embeddings = self.model.encode([text1, text2])

                # 計算餘弦相似度
                from numpy import dot
                from numpy.linalg import norm

                similarity = dot(embeddings[0], embeddings[1]) / (
                    norm(embeddings[0]) * norm(embeddings[1])
                )

                return float(similarity)

            except Exception as e:
                logger.warning(f"語義相似度計算失敗，使用基礎方法: {e}")

        # 基礎方法：詞彙重疊率
        return self._basic_similarity(text1, text2)

    def _basic_similarity(self, text1: str, text2: str) -> float:
        """
        基礎相似度計算（詞彙重疊率）

        Args:
            text1: 文本1
            text2: 文本2

        Returns:
            相似度分數（0-1）
        """
        # 簡單分詞（基於常見分隔符）
        words1 = set(re.findall(r'[\u4e00-\u9fff]+', text1))
        words2 = set(re.findall(r'[\u4e00-\u9fff]+', text2))

        if not words1 or not words2:
            return 0.0

        # Jaccard 相似度
        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def _detect_irreversible_events(self, outline: str) -> Tuple[bool, List[str]]:
        """
        檢測不可逆事件

        Args:
            outline: 章節大綱

        Returns:
            (是否包含不可逆事件, 事件列表)
        """
        events = []

        for keyword in self.IRREVERSIBLE_KEYWORDS:
            if keyword in outline:
                events.append(keyword)

        return len(events) > 0, events

    def _assess_conflict_intensity(self, outline: str) -> float:
        """
        評估衝突強度

        Args:
            outline: 章節大綱

        Returns:
            衝突強度（0-1）
        """
        scores = []

        # 檢查各級別衝突關鍵詞
        for level, keywords in self.CONFLICT_KEYWORDS.items():
            count = sum(1 for kw in keywords if kw in outline)

            if level == 'low':
                scores.append(count * 0.2)
            elif level == 'medium':
                scores.append(count * 0.5)
            elif level == 'high':
                scores.append(count * 1.0)

        # 歸一化到 0-1
        total_score = sum(scores)
        max_possible = 5.0  # 假設最高分為5

        return min(total_score / max_possible, 1.0)

    def _detect_growth_indicators(self, outline: str) -> Tuple[bool, List[str]]:
        """
        檢測成長指標

        Args:
            outline: 章節大綱

        Returns:
            (是否包含成長元素, 指標列表)
        """
        indicators = []

        for keyword in self.GROWTH_KEYWORDS:
            if keyword in outline:
                indicators.append(keyword)

        return len(indicators) > 0, indicators

    def generate_fix_suggestions(self, validation_result: Dict) -> List[str]:
        """
        根據驗證結果生成修復建議

        Args:
            validation_result: validate_chapter_outline 的返回結果

        Returns:
            建議列表
        """
        suggestions = []

        # 相似度過高的建議
        if validation_result['similar_chapters']:
            suggestions.append(
                f"與第 {', '.join(map(str, validation_result['similar_chapters']))} 章相似，"
                "建議從不同角度展開劇情，或改變事件順序"
            )

        # 衝突強度過低的建議
        if validation_result['conflict_intensity'] < 0.3:
            suggestions.append(
                "衝突強度較低，建議加入以下元素之一：\n"
                "  - 角色間的矛盾或對抗\n"
                "  - 外部威脅或危機\n"
                "  - 內心掙扎或抉擇"
            )

        # 長期無成長的建議
        if not validation_result['has_growth']:
            suggestions.append(
                "缺少成長元素，建議讓角色：\n"
                "  - 習得新技能或知識\n"
                "  - 突破心理障礙\n"
                "  - 對世界有新的認識"
            )

        # 不可逆事件的提醒
        if validation_result['has_irreversible']:
            suggestions.append(
                f"包含不可逆事件 ({', '.join(validation_result['irreversible_events'])})，"
                "請確保：\n"
                "  - 後續章節考慮此事件影響\n"
                "  - 角色對此有合理反應\n"
                "  - 不出現邏輯矛盾"
            )

        if not suggestions:
            suggestions.append("大綱品質良好，無需修改")

        return suggestions


if __name__ == '__main__':
    # 測試驗證器
    logging.basicConfig(level=logging.INFO)

    validator = OutlineValidator(similarity_threshold=0.7)

    # 測試大綱
    outline1 = "主角在森林中遇到神秘老人，老人傳授他一套心法，主角開始修煉"
    outline2 = "主角繼續在森林修煉，突破第一層境界，遇到強大妖獸，決心變強"
    outline3 = "主角在森林中遇到另一位老者，老者教他新的功法，主角繼續修煉"  # 與第1章相似

    print("=== 驗證第 1 章 ===")
    result1 = validator.validate_chapter_outline(outline1, [], chapter_num=1)
    print(f"通過: {result1['is_valid']}")
    print(f"警告: {result1['warnings']}")

    print("\n=== 驗證第 2 章 ===")
    result2 = validator.validate_chapter_outline(outline2, [outline1], chapter_num=2)
    print(f"通過: {result2['is_valid']}")
    print(f"相似度: {result2['similarity_score']:.2f}")
    print(f"衝突強度: {result2['conflict_intensity']:.2f}")
    print(f"成長指標: {result2['growth_indicators']}")

    print("\n=== 驗證第 3 章（相似） ===")
    result3 = validator.validate_chapter_outline(outline3, [outline1, outline2], chapter_num=3)
    print(f"通過: {result3['is_valid']}")
    print(f"相似章節: {result3['similar_chapters']}")
    print(f"警告: {result3['warnings']}")

    print("\n=== 修復建議 ===")
    suggestions = validator.generate_fix_suggestions(result3)
    for i, suggestion in enumerate(suggestions, 1):
        print(f"{i}. {suggestion}")
