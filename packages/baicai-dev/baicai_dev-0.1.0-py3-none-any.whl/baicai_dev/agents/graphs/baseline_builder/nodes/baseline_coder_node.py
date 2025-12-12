from typing import Dict

from baicai_base.agents.graphs.nodes import BaseCoderNode
from langchain_core.runnables import RunnableConfig

from baicai_dev.agents.roles.ml import baseline_coder


class BaselineCoderNode(BaseCoderNode):
    def __init__(self, llm, logger=None) -> None:
        super().__init__(llm=llm, logger=logger, graph_name="Baseline", node_name="Baseline Coder")
        self.runnable = baseline_coder(self.llm)

    def _get_invoke_params(self, state: Dict, config: RunnableConfig) -> Dict:
        return {
            "path": config["configurable"]["path"],
            "target": config["configurable"]["target"],
            "classification": config["configurable"]["classification"],
            "ignored_features": config["configurable"]["ignored_features"],
            "messages": state["messages"],
            "name": config["configurable"]["name"],
            "date_feature": config["configurable"]["date_feature"],
            "need_time": config["configurable"]["need_time"],
            "ordinal_features": config["configurable"]["ordinal_features"],
            "time_series": config["configurable"]["time_series"],
            "threshold": config["configurable"]["threshold"],
            "delimiter": config["configurable"]["delimiter"],
            "avg_param": config["configurable"]["avg_param"],
        }

    def _get_state_updates(self, state: Dict, code: str) -> Dict:
        baseline_codes = state.get("baseline_codes", [])
        baseline_iter = state.get("baseline_iter", 0)
        baseline_builder_iter = state.get("baseline_builder_iter", 1)

        baseline_codes.append({"code": code})

        return {
            "baseline_builder_iter": baseline_builder_iter,
            "baseline_iter": baseline_iter,
            "baseline_codes": baseline_codes,
        }
