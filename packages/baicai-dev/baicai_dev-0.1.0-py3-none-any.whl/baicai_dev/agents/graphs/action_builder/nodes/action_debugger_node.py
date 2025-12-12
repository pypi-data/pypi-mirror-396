import logging
from typing import Any, Dict

from baicai_base.agents.graphs.nodes import BaseNode
from baicai_base.utils.data import extract_code, get_saved_pickle_path
from langchain_core.runnables import RunnableConfig

from baicai_dev.agents.graphs.action_builder.state import ActionState
from baicai_dev.agents.roles.ml import debugger
from baicai_dev.utils.constants import DATA_ALREADY_LOADED


class ActionDebuggerNode(BaseNode):
    """
    Node responsible for generating debug actions.
    """

    def __init__(self, llm: Any, logger: logging.Logger = None) -> None:
        """
        Initialize the ActionDebuggerNode.

        Args:
            llm: The language model for generating debug actions.
            logger (logging.Logger): Optional logger for logging information.
        """
        super().__init__(llm=llm, logger=logger)
        self.runnable = debugger(self.llm)

    def __call__(self, state: ActionState, config: RunnableConfig) -> Dict[str, Any]:
        """
        Execute the node logic.

        Args:
            state (dict): The current state of the process.
            config (RunnableConfig): Configuration details for the node.

        Returns:
            dict: Updated state after execution.
        """
        messages = state.get("messages", [])
        actions = state.get("actions", [])
        load_data_code = state.get("load_data_code", {})
        name = config["configurable"]["name"]

        # Extract configuration details for code generation
        target = config["configurable"]["target"]
        clean_data_path = get_saved_pickle_path(folder=None, name=name, file_prefix="baseline", type="data")

        target = config["configurable"]["target"]

        self.logger.info("## Debugging ...")

        if load_data_code.get("error", None):
            self.solution = self.runnable.invoke(
                {
                    "feedbacks": load_data_code["error"],
                    "messages": messages,
                    "path": clean_data_path,
                    "target": target,
                    "ignored_features": "",
                }
            )

            try:
                code = extract_code(self.solution.content)
                load_data_code.update({"code": code})
            except Exception as e:
                self.error_message = f"Error extracting code: {e}"
                self.logger.error(self.error_message)
                return {"fail_fast": True, "error_message": self.error_message}

            self.logger.info(f"# Fix Step:\n{self.solution.content}")

        else:
            for action in actions:
                if action["ignore"] or action["success"]:
                    continue

                self.solution = self.runnable.invoke(
                    {
                        "feedbacks": action["error"] + DATA_ALREADY_LOADED,
                        "messages": messages,
                        "path": clean_data_path,
                        "target": target,
                        "ignored_features": "",
                    }
                )

                try:
                    code = extract_code(self.solution.content)
                    action.update({"code": code})
                except Exception as e:
                    self.error_message = f"Error extracting code: {e}"
                    self.logger.error(self.error_message)
                    return {"fail_fast": True, "error_message": self.error_message}

                self.logger.info(f"# Fix Step:\n{self.solution.content}")

        return {
            "actions": actions,
            "load_data_code": load_data_code,
        }
