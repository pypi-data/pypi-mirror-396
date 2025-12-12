from typing import Any, Dict

from baicai_base.agents.graphs.nodes import DebuggerNode
from baicai_base.utils.data import extract_code
from langchain_core.runnables import RunnableConfig

from baicai_dev.agents.roles.dl import debugger


class DLDebuggerNode(DebuggerNode):
    """Node for debugging deep learning code."""

    def __init__(self, llm=None, logger=None, graph_name="DL", role=debugger, one_pass_graph=True):
        super().__init__(llm=llm, logger=logger, graph_name=graph_name, role=role, one_pass_graph=one_pass_graph)

    def __call__(self, state: Dict[str, Any], config: RunnableConfig) -> Dict[str, Any]:
        """Execute debugging logic for DL code."""
        messages = state["messages"]
        codes = state.get("dl_codes", [])
        feedbacks = state.get("dl_feedbacks", [])
        self.feedbacks = feedbacks[-1] if feedbacks else ""

        self.logger.info("## Debugging DL Code...")

        self.solution = self.runnable.invoke(
            {
                "feedbacks": self.feedbacks,
                "messages": messages,
            }
        )

        codes.append({"code": extract_code(self.solution.content)})

        return {
            "dl_codes": codes,
            "fail_fast": False,
            "error_message": "",
        }
