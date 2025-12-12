import logging
from typing import Any, Dict, List

from baicai_base.agents.graphs.nodes import BaseCoderNode
from baicai_base.utils.data import get_saved_pickle_path
from langchain_core.runnables import RunnableConfig

from baicai_dev.agents.roles.ml import workflow_coder
from baicai_dev.utils.setups import ACTIONS_WITH_CODE_IRIS, BASELINE_CODES_IRIS


class WorkflowCoderNode(BaseCoderNode):
    def __init__(
        self,
        llm: Any,
        logger: logging.Logger = None,
        actions: List[Dict[str, Any]] = ACTIONS_WITH_CODE_IRIS,
        baseline_codes: List[Dict[str, Any]] = BASELINE_CODES_IRIS,
    ) -> None:
        super().__init__(llm=llm, logger=logger, graph_name="Workflow", node_name="Workflow Coder")
        self.runnable = workflow_coder(self.llm)
        self.actions = actions
        self.baseline_codes = baseline_codes

    def _get_invoke_params(self, state: Dict, config: RunnableConfig) -> Dict:
        actions = self.get_state(state, "actions", self.actions)

        name = config["configurable"]["name"]
        clean_data_path = get_saved_pickle_path(folder=None, name=name, file_prefix="baseline", type="data")

        accepted_actions = [
            {key: action[key] for key in ["id", "code"]} for action in actions if action["accepted"] == "true"
        ]
        time_series = config["configurable"]["time_series"]
        avg_param = config["configurable"]["avg_param"]
        selected_metric = config["configurable"]["selected_metric"]
        classification = config["configurable"]["classification"]

        return {
            "actions": accepted_actions,
            "clean_data_path": clean_data_path,
            "messages": state["messages"],
            "name": name,
            "time_series": time_series,
            "avg_param": avg_param,
            "selected_metric": selected_metric,
            "classification": classification,
        }

    def _get_state_updates(self, state: Dict, code: str) -> Dict:
        workflow_codes = state.get("workflow_codes", [])
        workflow_iter = state.get("workflow_iter", 0)
        workflow_builder_iter = state.get("workflow_builder_iter", 1)
        workflow_success = state.get("workflow_success", True)

        workflow_codes.append({"code": code})

        return {
            "workflow_codes": workflow_codes,
            "workflow_success": workflow_success,
            "workflow_iter": workflow_iter,
            "workflow_builder_iter": workflow_builder_iter,
        }
