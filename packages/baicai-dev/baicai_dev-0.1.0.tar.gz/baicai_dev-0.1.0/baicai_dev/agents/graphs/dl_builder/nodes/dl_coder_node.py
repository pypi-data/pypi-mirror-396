from typing import Any, Dict, Set

from baicai_base.agents.graphs.nodes import BaseCoderNode
from langchain_core.runnables import RunnableConfig

from baicai_dev.agents.roles.dl import (
    collab_recommender,
    from_csv_classifier,
    from_func_classifier,
    from_re_classifier,
    multi_label_classifier,
    single_label_classifier,
)
from baicai_dev.agents.roles.dl.hf_coder import (
    ner_inference_coder,
    semantic_match_inference_coder,
    sentiment_classifier_trainer,
    sentiment_inference_coder,
)
from baicai_dev.utils.data import TaskType


class DLCoderNode(BaseCoderNode):
    """Node for training deep learning models."""

    def __init__(self, llm=None, logger=None):
        super().__init__(llm=llm, logger=logger, graph_name="DL", node_name="Fastai Coder")
        self.runnable = None
        # Initialize task-specific experts
        self.runnables = {
            TaskType.VISION_CSV.value: from_csv_classifier(),
            TaskType.VISION_FUNC.value: from_func_classifier(),
            TaskType.VISION_RE.value: from_re_classifier(),
            TaskType.VISION_MULTI_LABEL.value: multi_label_classifier(),
            TaskType.VISION_SINGLE_LABEL.value: single_label_classifier(),
            TaskType.COLLABORATIVE.value: collab_recommender(),
            TaskType.NLP_SENTIMENT_TRAINER.value: sentiment_classifier_trainer(),
            TaskType.NLP_NER_INFERENCE.value: ner_inference_coder(),
            TaskType.NLP_SEMANTIC_MATCH_INFERENCE.value: semantic_match_inference_coder(),
            TaskType.NLP_SENTIMENT_INFERENCE.value: sentiment_inference_coder(),
        }

        # Common parameters shared across multiple task types
        self._common_vision_params = {"path", "batch_size", "model", "valid_pct", "device", "num_workers", "size"}

        # CSV-based vision parameters
        self._csv_vision_params = {
            "folder",
            "csv_file",
            "image_col",
            "label_col",
            "valid_col",
            "delimiter",
            "label_delim",
        }

        # Define parameter maps for each task type
        self._param_maps = {
            TaskType.VISION_CSV.value: self._get_vision_csv_param_map(),
            TaskType.VISION_FUNC.value: self._get_vision_func_param_map(),
            TaskType.VISION_RE.value: self._get_vision_re_param_map(),
            TaskType.VISION_MULTI_LABEL.value: self._get_vision_multi_label_param_map(),
            TaskType.VISION_SINGLE_LABEL.value: self._get_vision_single_label_param_map(),
            TaskType.COLLABORATIVE.value: self._get_collab_recommender_param_map(),
            TaskType.NLP_SENTIMENT_TRAINER.value: self._get_sentiment_classifier_trainer_param_map(),
            TaskType.NLP_NER_INFERENCE.value: self._get_ner_inference_param_map(),
            TaskType.NLP_SEMANTIC_MATCH_INFERENCE.value: self._get_semantic_match_inference_param_map(),
            TaskType.NLP_SENTIMENT_INFERENCE.value: self._get_sentiment_inference_param_map(),
        }

    def _get_vision_csv_param_map(self) -> Set[str]:
        """Get parameter names for vision CSV tasks."""
        return self._common_vision_params.union(self._csv_vision_params)

    def _get_vision_func_param_map(self) -> Set[str]:
        """Get parameter names for vision function-based tasks."""
        return self._common_vision_params.union({"label_func"})

    def _get_vision_re_param_map(self) -> Set[str]:
        """Get parameter names for vision regex-based tasks."""
        return self._common_vision_params.union({"pat"})

    def _get_vision_multi_label_param_map(self) -> Set[str]:
        """Get parameter names for vision multi-label tasks."""
        return self._common_vision_params.union(self._csv_vision_params)

    def _get_vision_single_label_param_map(self) -> Set[str]:
        """Get parameter names for vision single-label tasks."""
        return self._common_vision_params.union(self._csv_vision_params)

    def _get_collab_recommender_param_map(self) -> Set[str]:
        """Get parameter names for collaborative filtering tasks."""
        return {"path", "user_name", "item_name", "rating_name", "y_range_min", "y_range_max", "valid_pct"}

    def _get_sentiment_classifier_trainer_param_map(self) -> Set[str]:
        """Get parameter names for sentiment classifier trainer tasks."""
        return {
            "num_labels",
            "label_mapping",
            "path",
            "text_column",
            "label_column",
            "num_epochs",
            "texts",
        }

    def _get_ner_inference_param_map(self) -> Set[str]:
        """Get parameter names for NER inference tasks."""
        return {"model", "input"}

    def _get_semantic_match_inference_param_map(self) -> Set[str]:
        """Get parameter names for semantic match inference tasks."""
        return {"model", "input1", "input2"}

    def _get_sentiment_inference_param_map(self) -> Set[str]:
        """Get parameter names for sentiment inference tasks."""
        return {"model", "input"}

    def _get_params_from_config(self, param_names: Set[str], config: RunnableConfig) -> Dict[str, Any]:
        """Extract parameters from baicai_base.configs based on parameter names.

        Args:
            param_names: Set of parameter names to extract
            config: Configuration containing the parameters

        Returns:
            Dictionary of parameter name-value pairs
        """
        return {param: config["configurable"][param] for param in param_names if param in config["configurable"]}

    def _get_invoke_params(self, state: Dict[str, Any], config: RunnableConfig) -> Dict[str, Any]:
        """Get parameters for the runnable invocation.

        Args:
            state: Current state containing task type and configurations
            config: Configuration for the runnable

        Returns:
            Parameters for runnable invocation
        """
        task_type = config["configurable"]["task_type"]
        if task_type in self._param_maps:
            return self._get_params_from_config(self._param_maps[task_type], config)
        return {}

    def _get_state_updates(self, state: Dict[str, Any], code: str) -> Dict[str, Any]:
        """Get state updates after code generation.

        Args:
            state: Current state
            code: Generated code

        Returns:
            State updates
        """
        dl_codes = state.get("dl_codes", [])
        dl_codes.append({"code": code})

        return {
            "dl_codes": dl_codes,
            "dl_success": True,
        }
