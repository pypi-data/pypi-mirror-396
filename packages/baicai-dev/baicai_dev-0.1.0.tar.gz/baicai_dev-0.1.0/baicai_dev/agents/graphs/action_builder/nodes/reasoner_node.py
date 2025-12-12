import logging
from typing import Any, Dict

from baicai_base.agents.graphs.nodes import BaseNode
from baicai_base.utils.constants import JSON_RETRY_TOO_MANY, PREV_FAIL_FAST
from baicai_base.utils.data import CodeStore, get_saved_pickle_path, preview_data, safe_extract_json
from langchain_core.runnables import RunnableConfig

from baicai_dev.agents.graphs.action_builder.state import ActionState
from baicai_dev.agents.roles.ml import reasoner
from baicai_dev.utils.constants import NUM_ACTIONS
from baicai_dev.utils.setups import BASELINE_CODES_IRIS


class ReasonerNode(BaseNode):
    """
    Node for handling action maker iterations using an LLM.
    """

    def __init__(
        self, llm: Any, logger: logging.Logger = None, baseline_codes: CodeStore = BASELINE_CODES_IRIS
    ) -> None:
        """
        Initialize the ActionMakerNode with an LLM and an optional logger.

        Args:
            llm: The language model for code generation.
            logger: Optional logger for logging information.
        """
        super().__init__(llm=llm, logger=logger)
        self.runnable = reasoner(self.llm)
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
        if state.get("fail_fast", False):
            return {"fail_fast": True, "error_message": PREV_FAIL_FAST}

        messages = state.get("messages", [])
        actions = state.get("actions", "")
        baseline_codes = self.get_state(state, "baseline_codes", self.baseline_codes)

        # Extract configuration details for code generation
        domain = config["configurable"]["domain"]
        domain_context = config["configurable"]["domain_context"]
        target = config["configurable"]["target"]
        name = config["configurable"]["name"]
        clean_data_path = get_saved_pickle_path(folder=None, name=name, file_prefix="baseline", type="data")
        requirements = config["configurable"]["requirements"]
        try:
            cleaned_data_info = preview_data(clean_data_path, target=target, brief=False)["data_info"]
        except (KeyError, FileNotFoundError) as e:
            cleaned_data_info = config["configurable"]["full_data_info"]
            self.logger.warning(f"### Warning: No cleaned data info found. Using full data info instead. {e}")

        self.logger.info("""
# Action Builder
## Reasoner
""")
        self.solution, expert_insight, self.feedbacks, failed = safe_extract_json(
            self.runnable,
            {
                "num": NUM_ACTIONS,
                "domain": domain,
                "model_info": baseline_codes[0]["result"],
                "domain_context": domain_context,
                "messages": messages,
                "target": target,
                "cleaned_data_info": cleaned_data_info,
                "requirements": requirements,
            },
        )

        if failed:
            return {"fail_fast": True, "error_message": JSON_RETRY_TOO_MANY}

        actions = expert_insight["actions"]

        self.logger.info(f"### Action generated: \n{self.solution.content}")

        return {
            "actions": actions,
            "fail_fast": False,
        }
