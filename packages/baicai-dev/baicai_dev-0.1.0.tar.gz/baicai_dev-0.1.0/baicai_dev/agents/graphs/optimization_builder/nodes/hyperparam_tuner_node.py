import logging
from typing import Any, Dict

from baicai_base.agents.graphs.nodes import BaseCoderNode
from langchain_core.runnables import RunnableConfig

from baicai_dev.agents.roles.ml import hyperparam_tuner
from baicai_dev.utils.setups import WORKFLOW_CODE_IRIS


class HyperparamTunerNode(BaseCoderNode):
    def __init__(self, llm: Any, logger: logging.Logger = None, workflow_codes=WORKFLOW_CODE_IRIS) -> None:
        super().__init__(llm=llm, logger=logger, graph_name="Optimization", node_name="Hyperparam Tuner")
        self.runnable = hyperparam_tuner(self.llm)
        self.workflow_codes = workflow_codes

    def _get_invoke_params(self, state: Dict, config: RunnableConfig) -> Dict:
        workflow_codes = self.get_state(state, "workflow_codes", self.workflow_codes)
        workflow_code = workflow_codes[-1]["code"]
        metric = config["configurable"]["selected_metric"]

        data_size = config["configurable"]["data_size"]
        time_series = config["configurable"]["time_series"]

        return {
            "code": workflow_code,
            "data_size": data_size,
            "messages": state["messages"],
            "metric": metric,
            "time_series": time_series,
        }

    def _get_state_updates(self, state: Dict, code: str) -> Dict:
        optimization_codes = state.get("optimization_codes", [])
        optimization_iter = state.get("optimization_iter", 0)
        optimization_builder_iter = state.get("optimization_builder_iter", 0)
        optimization_success = state.get("optimization_success", True)

        optimization_codes.append({"code": code})

        return {
            "optimization_builder_iter": optimization_builder_iter,
            "optimization_iter": optimization_iter,
            "optimization_codes": optimization_codes,
            "optimization_success": optimization_success,
        }
