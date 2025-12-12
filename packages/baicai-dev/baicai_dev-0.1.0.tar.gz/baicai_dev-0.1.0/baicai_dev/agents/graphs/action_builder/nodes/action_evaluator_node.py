import logging
from typing import Any, Dict

from baicai_base.agents.graphs.nodes import BaseNode
from baicai_base.utils.constants import JSON_RETRY_TOO_MANY
from baicai_base.utils.data import CodeStore, safe_extract_json
from langchain_core.runnables import RunnableConfig

from baicai_dev.agents.graphs.action_builder.state import ActionState
from baicai_dev.agents.roles.ml import action_evaluator
from baicai_dev.utils.setups import BASELINE_CODES_IRIS


class ActionEvaluatorNode(BaseNode):
    """
    Node for handling action evaluator iterations using an LLM.
    """

    def __init__(
        self, llm: Any, logger: logging.Logger = None, baseline_codes: CodeStore = BASELINE_CODES_IRIS
    ) -> None:
        """
        Initialize the ActionEvaluatorNode with a language model and an optional logger.

        Args:
            llm: The language model to be used for action evaluation.
            logger: Optional logger for logging information.
        """
        super().__init__(llm=llm, logger=logger)
        self.runnable = action_evaluator(self.llm)
        self.baseline_codes = baseline_codes

    def __call__(self, state: ActionState, config: RunnableConfig) -> Dict[str, Any]:
        """
        Execute the node logic.

        Args:
            state (ActionState): The current state of the action process.
            config (RunnableConfig): Configuration details for the node.

        Returns:
            dict: Updated state after execution.
        """
        self.logger.info("## Action Evaluator")

        # Extract and initialize state components with defaults for potential None values
        actions = state.get("actions", [])
        baseline_codes = self.get_state(state, "baseline_codes", self.baseline_codes)

        baseline_result = baseline_codes[-1]["result"]

        metrics = config["configurable"]["selected_metric"]

        used_actions = [
            {
                "id": a["id"],
                "result": a["result"],
            }
            for a in actions
        ]

        self.solution, extracted_actions, self.feedbacks, failed = safe_extract_json(
            self.runnable,
            {
                "model_info": used_actions,
                "metrics": metrics,
                "baseline_result": baseline_result,
            },
        )

        if failed:
            return {"fail_fast": True, "error_message": JSON_RETRY_TOO_MANY}

        for action, conclusion in zip(actions, extracted_actions["actions"], strict=False):
            action["accepted"] = conclusion["accepted"]
            action["rejected"] = "true" if conclusion["accepted"] == "false" else "false"

        self.logger.info(f"### Action Evaluator Result: \n{self.solution.content}")

        action_codes = ""
        for action in actions:
            action_codes += action["code"] + "\n"

        self.logger.debug(f"### All Actions: \n{actions}")

        return {"actions": actions, "action_codes": [action_codes]}
