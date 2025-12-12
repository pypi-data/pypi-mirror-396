_IMPORT = """
from typing import Any, Dict, List, Optional, Tuple, Union

import torch
from sentence_transformers import SentenceTransformer, util
from transformers import Pipeline, pipeline
"""
_BASE_PIPELINE = """
class BasePipeline:
    def __init__(self, model: str):
        self.model = model
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.pipeline: Optional[Pipeline] = None

    def load_pipeline(self) -> None:
        raise NotImplementedError("子类必须实现 load_pipeline 方法")

    def preprocess(self, input_text: str) -> str:
        return input_text

    def postprocess(self, output: Any) -> Any:
        return output

    def __call__(self, input_text: str) -> Any:
        if self.pipeline is None:
            self.load_pipeline()

        processed_input = self.preprocess(input_text)
        result = self.pipeline(processed_input)
        return self.postprocess(result)
"""

_TEXT_CLASSIFICATION_PIPELINE = """
class TextClassificationPipeline(BasePipeline):

    def __init__(self, model: str = None):
        if model is None:
            model = "uer/roberta-base-finetuned-dianping-chinese"
        super().__init__(model)

    def load_pipeline(self) -> None:
        self.pipeline = pipeline("text-classification", model=self.model, device=self.device)

    def postprocess(self, output: List[Dict[str, Any]]) -> Union[Dict[str, float], List[Dict[str, float]]]:
        # 如果是单个结果
        if len(output) == 1:
            return {{"label": output[0]["label"], "score": output[0]["score"]}}

        # 如果是多个结果
        return [{{"label": item["label"], "score": item["score"]}} for item in output]

    def __call__(self, texts: Union[str, List[str]]) -> Union[Dict[str, float], List[Dict[str, float]]]:
        if self.pipeline is None:
            self.load_pipeline()

        # 确保输入格式正确
        if isinstance(texts, str):
            texts = [texts]

        # 获取预测结果
        results = self.pipeline(texts)
        return self.postprocess(results)
"""

_TOKEN_CLASSIFICATION_PIPELINE = """
class TokenClassificationPipeline(BasePipeline):

    def __init__(self, model: str = None, aggregation_strategy: str = "average"):
        if model is None:
            model = "xiaxy/elastic-bert-chinese-ner"
        super().__init__(model)
        self.aggregation_strategy = aggregation_strategy

    def load_pipeline(self) -> None:
        self.pipeline = pipeline(
            "token-classification", model=self.model, device=self.device, aggregation_strategy=self.aggregation_strategy
        )

    def preprocess(self, input_text: str) -> str:
        # 可以添加中文分词等预处理步骤
        return input_text

    def postprocess(self, output: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # 过滤低置信度的预测
        threshold = 0.8
        filtered_results = [entity for entity in output if entity["score"] >= threshold]

        # 合并重叠的实体（如果需要）
        # 添加自定义的实体验证规则
        return filtered_results
"""

_SEMANTIC_MATCHER_PIPELINE = """
class SemanticMatcherPipeline(BasePipeline):

    def __init__(self, model: str = None, threshold: float = 0.85):
        if model is None:
            model = "moka-ai/m3e-base"
        super().__init__(model)
        self.threshold = threshold

    def load_pipeline(self) -> None:
        self.pipeline = SentenceTransformer(self.model, device=self.device)

    def compute_similarity(self, text1: str, text2: str) -> float:
        if self.pipeline is None:
            self.load_pipeline()

        # 编码文本
        embeddings = self.pipeline.encode([text1, text2], convert_to_tensor=True, show_progress_bar=False)

        # 计算相似度
        similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1])
        return float(similarity[0][0])

    def is_similar(self, text1: str, text2: str) -> bool:
        score = self.compute_similarity(text1, text2)
        return score >= self.threshold

    def __call__(self, text1: str, text2: str, return_score: bool = True) -> Union[bool, Tuple[bool, float]]:
        score = self.compute_similarity(text1, text2)
        is_similar = score >= self.threshold

        if return_score:
            return is_similar, score
        return is_similar

    def batch_compare(self, texts1: List[str], texts2: List[str], return_scores: bool = True) -> Union[List[bool], List[Tuple[bool, float]]]:
        if len(texts1) != len(texts2):
            raise ValueError("两组文本的长度必须相同")

        if self.pipeline is None:
            self.load_pipeline()

        # 批量编码
        embeddings1 = self.pipeline.encode(texts1, convert_to_tensor=True)
        embeddings2 = self.pipeline.encode(texts2, convert_to_tensor=True)

        # 计算相似度
        similarities = util.pytorch_cos_sim(embeddings1, embeddings2)

        results = []
        for i in range(len(texts1)):
            score = float(similarities[i][i])
            is_similar = score >= self.threshold

            if return_scores:
                results.append((is_similar, score))
            else:
                results.append(is_similar)

        return results
"""

_RUN_TEXT_CLASSIFICATION = """
classifier = TextClassificationPipeline()
result = classifier("{input}")
print(result)
"""

_RUN_TOKEN_CLASSIFICATION = """
ner = TokenClassificationPipeline()
result = ner("{input}")
print(result)
"""

_RUN_SEMANTIC_MATCHER = """
matcher = SemanticMatcherPipeline()
text1 = "{input1}"
text2 = "{input2}"
is_similar, score = matcher(text1, text2)
print(f"基本比较:")
print(f"句子1: {{text1}}")
print(f"句子2: {{text2}}")
print(f"是否相似: {{is_similar}}")
print(f"相似度分数: {{score:.4f}}")
"""


SENTIMENT_INFERENCE_CODE = "```python\n" + _IMPORT + _BASE_PIPELINE + _TEXT_CLASSIFICATION_PIPELINE + _RUN_TEXT_CLASSIFICATION + "\n```"
NER_INFERENCE_CODE = "```python\n" + _IMPORT + _BASE_PIPELINE + _TOKEN_CLASSIFICATION_PIPELINE + _RUN_TOKEN_CLASSIFICATION + "\n```"
SEMANTIC_MATCH_INFERENCE_CODE = "```python\n" + _IMPORT + _BASE_PIPELINE + _SEMANTIC_MATCHER_PIPELINE + _RUN_SEMANTIC_MATCHER + "\n```"
