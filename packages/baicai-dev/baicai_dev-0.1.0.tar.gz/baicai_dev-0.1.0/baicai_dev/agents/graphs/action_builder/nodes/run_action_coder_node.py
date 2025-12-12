import logging
from dataclasses import dataclass
from typing import Any, Dict

from baicai_base.agents.graphs.nodes import BaseNode
from baicai_base.utils.constants import CONTINUE_AFTER_MAX_ITER, MAX_ITER_EXCEEDED
from langchain_core.runnables import RunnableConfig

from baicai_dev.agents.graphs.action_builder.state import ActionState
from baicai_dev.utils.constants import MAX_ITER


@dataclass
class CodeExecutionResult:
    success: bool
    message: str


class RunActionCoderNode(BaseNode):
    """
    Node for running code and handling iterations.

    Attributes:
        logger (logging.Logger): Logger for logging messages. Defaults to None.
        code_interpreter: Instance for interpreting code. Defaults to class attribute.
        fail_fast (bool): Whether to fail fast. Defaults to False.
        max_iter (int): Maximum number of iterations for running code. Defaults to MAX_ITER.
        max_graph_iter (int): Maximum number of iterations for the graph. Defaults to MAX_ITER.
    """

    code_interpreter = None  # Class attribute for code interpreter

    def __init__(self, logger: logging.Logger = None, code_interpreter=None, max_iter: int = MAX_ITER):
        """
        Initialize the RunCodeNode with a logger, code interpreter, and other parameters.
        """
        super().__init__(logger=logger)

        if RunActionCoderNode.code_interpreter is None:
            from baicai_base.utils.setups import setup_code_interpreter

            RunActionCoderNode.code_interpreter = setup_code_interpreter()
        self.code_interpreter = code_interpreter or RunActionCoderNode.code_interpreter
        self.fail_fast = False
        self.max_iter = max_iter
        self.successes = []
        self.solutions = []
        self.success = True

    async def __call__(self, state: ActionState, config: RunnableConfig) -> Dict[str, Any]:
        """
        Execute the node logic.

        Args:
            state (dict): The current state of the process.
            config (RunnableConfig): Configuration details for the node.

        Returns:
            dict: Updated state after execution.
        """
        self._initialize_state(state)

        self._log_initial_info()

        await self._execute_codes()

        if self.success:
            self._handle_success()
        else:
            self._handle_error()

        return self._finalize_result()

    def _initialize_state(self, state: Dict[str, Any]):
        """
        Initialize the state for code execution.

        Args:
            state (dict): The current state of the process.
        """
        self.success = state.get("action_success", True)
        self.error_message = state.get("error_message", "")
        self.messages = state.get("messages", [])
        self.iter = state.get("action_iter", 0)
        self.actions = state.get("actions", [])
        self.load_data_code = state.get("load_data_code", {})
        self.load_data_code["success"] = self.load_data_code.get("success", False) if self.load_data_code else False
        self.go_with_error = state.get("go_with_error", False)

        self.iter += 1

    def _log_initial_info(self):
        """
        Log initial information about the code execution.
        """
        self.logger.info("## Running Action Code")
        self.logger.info(f"### Action Iteration: {self.iter}")

    async def _execute_codes(self):
        """Execute the load data code and actions."""
        if not self.load_data_code.get("success", False):
            self.load_data_code["success"] = await self._execute_load_data()

        if not self.load_data_code.get("success", False):
            return

        await self._execute_actions()
        self.success = all(self.successes)

    async def _execute_load_data(self) -> bool:
        """Execute the data loading code."""
        self.logger.info("#### Load data code")
        try:
            result = await self._run_code_safely(self.load_data_code["code"])
            if result.success:
                self.logger.info(f"- {result.message or 'Success'}")
                self.successes = [True]
                return True

            self._handle_load_data_error(result.message)
            return False

        except Exception as e:
            self._handle_load_data_error(str(e))
            return False

    async def _execute_actions(self):
        """Execute each action's code."""
        self.successes = [] if self.iter == 1 else [any(self.successes)]
        for action in self.actions:
            if action.get("ignore") or action.get("success"):
                continue

            await self._process_single_action(action)

    async def _process_single_action(self, action: Dict[str, Any]):
        """Process a single action's code."""
        code_content = action["code"].strip()
        if not code_content:
            self._log_and_update_code(action, "You generated nothing, please try again.", False)
            return

        try:
            result = await self._run_code_safely(code_content)
            self._log_and_update_code(action, result.message, result.success)
        except Exception as e:
            self._log_and_update_code(action, f"An error occurred: {str(e)}", False)

    async def _run_code_safely(self, code: str) -> CodeExecutionResult:
        """Safely execute code and return a standardized result."""
        run_result = await self.code_interpreter.run(code)
        return CodeExecutionResult(success=run_result[1], message=run_result[0] if run_result[0] else "Success")

    def _handle_load_data_error(self, error_msg: str):
        """Handle errors during data loading."""
        self.error_message = f"An error occurred during loading data: {error_msg}"
        self.load_data_code["error"] = error_msg
        self.success = False
        self.solutions = [error_msg]
        self.successes = [False]

    def _handle_error(self):
        """Handle errors during code execution."""
        self.success = False

        if self._should_fail_fast():
            return

        self._process_action_errors()
        self._check_max_iterations()

    def _should_fail_fast(self) -> bool:
        """Check if execution should fail fast."""
        if self.iter >= self.max_iter and not any(self.successes):
            self.error_message = MAX_ITER_EXCEEDED
            self.fail_fast = True
            return True
        return False

    def _process_action_errors(self):
        """Process errors for each action."""
        for action in self.actions:
            if action.get("success") or action.get("ignore"):
                continue

            # Ensure error is a string before checking containment
            error_str = action.get("error") or ""
            if "ModuleNotFoundError: No module named" in error_str:
                action["ignore"] = True
                continue

            action["error"] = self._format_error_message(action)

    def _format_error_message(self, action: Dict[str, Any]) -> str:
        """Format the error message for an action."""
        return (
            f"You got some mistake in your previous code. Please re-complete the code to fix the error.\n"
            f"Here is the previous version:\n```python\n{action['code']}\n```\n"
            f"When we run the above code, it raises this error:\n```sh\n{action.get('error', '')}\n```"
        )

    def _log_and_update_code(self, code: Dict[str, Any], message: str, success: bool):
        """
        Log the message and update the code dictionary.

        Args:
            code (dict): The code dictionary to update.
            message (str): The message to log and append to solutions.
            success (bool): The success status to set for the code.
        """
        result = "Success" if success else "Failed"
        self.logger.info(f"#### Run Code {result}")
        # Safely log the first line if it exists
        first_line = code["code"].splitlines()[0] if code["code"].splitlines() else "[no code]"
        self.logger.info(f"```python\n{first_line}\n```")

        self.logger.error(f"```sh\n{message}\n```") if not success else self.logger.info(f"```sh\n{message}\n```")
        self.solutions.append(message)
        self.successes.append(success)
        code.update(
            {
                "success": success,
                "result": message if success else "",
                "ignore": False,
                "error": "" if success else message,
            }
        )

    def _handle_success(self):
        """
        Handle successful code execution.
        """
        self.iter = 0
        self.success = True
        for action in self.actions:
            action["error"] = ""

    def _check_max_iterations(self):
        """
        Check if the maximum number of iterations has been exceeded.
        """
        if self.iter >= self.max_iter and any(self.successes) and not all(self.successes):
            self.error_message = CONTINUE_AFTER_MAX_ITER
            self.go_with_error = True

    def _finalize_result(self):
        """
        Finalize the result after code execution.

        Returns:
            dict: The final result.
        """
        if self.fail_fast:
            return {"fail_fast": self.fail_fast, "error_message": self.error_message}

        return {
            "messages": self.messages,
            "action_success": self.success,
            "action_iter": self.iter,
            "actions": self.actions,
            "fail_fast": self.fail_fast,
            "error_message": self.error_message,
            "load_data_code": self.load_data_code,
            "go_with_error": self.go_with_error,
        }


if __name__ == "__main__":
    import asyncio

    from baicai_dev.utils.setups import ACTIONS_WITH_CODE_IRIS

    async def main():
        node = RunActionCoderNode()
        node.load_data_code = {}
        node.load_data_code["code"] = """
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler

# Load the dataframe
df = pd.read_csv('examples/data/iris.csv')
"""
        node.actions = ACTIONS_WITH_CODE_IRIS
        node.iter = 1
        await node._execute_codes()
        print("solutions: \n", node.solutions)
        print("successes: \n", node.successes)

        print("Actions: \n", node.actions)

    asyncio.run(main())
