from baicai_base.agents.graphs.base_graph import BaseGraph
from baicai_base.agents.graphs.nodes import HelperNode
from baicai_base.services import LLM
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph

from baicai_dev.agents.graphs.action_builder.nodes import (
    ActionCoderNode,
    ActionDebuggerNode,
    ActionEvaluatorNode,
    ReasonerNode,
    RunActionCoderNode,
)
from baicai_dev.agents.graphs.action_builder.state import ActionState
from baicai_dev.agents.roles.helper import helper
from baicai_dev.utils.setups import BASELINE_CODES_IRIS


class ActionBuilder(BaseGraph):
    """
    Graph for building and evaluating actions.
    """

    def __init__(
        self,
        llm=None,
        config=None,
        memory=None,
        logger=None,
        code_interpreter=None,
        baseline_codes=BASELINE_CODES_IRIS,
        need_helper=False,
    ) -> None:
        """
        Initialize the ActionBuilder with configuration, memory, and other parameters.

        Args:
            llm: An instance of the LLM for code generation. Defaults to None.
            config: Custom configuration for the graph. Defaults to None.
            memory: Memory setup for the action builder. Defaults to None.
            logger: Logger for logging messages. Defaults to None.
            code_interpreter: Instance for interpreting code. Defaults to None.
            baseline_codes: Baseline codes for the action builder. Defaults to BASELINE_CODES_IRIS.
        """
        super().__init__(llm=llm, config=config, memory=memory, logger=logger)
        self.llm = llm or LLM().llm
        self.graph_name = "Action"
        self.need_helper = need_helper

        # setup code interpreter is too slow to import, use lazy import
        # also make sure the code interpreter is the same for all nodes
        if code_interpreter is None:
            from baicai_base.utils.setups import setup_code_interpreter

            self.code_interpreter = setup_code_interpreter()
        else:
            self.code_interpreter = code_interpreter

        # nodes
        self.reasoner_node = ReasonerNode(llm=self.llm, baseline_codes=baseline_codes)
        self.action_coder_node = ActionCoderNode(llm=self.llm)
        self.action_evaluator_node = ActionEvaluatorNode(llm=self.llm, baseline_codes=baseline_codes)
        self.run_action_node = RunActionCoderNode(code_interpreter=self.code_interpreter)
        self.action_debugger_node = ActionDebuggerNode(llm=self.llm)
        self.helper_node = HelperNode(
            llm=self.llm,
            graph_name=self.graph_name,
            role=helper,
            by_pass=not self.need_helper,
            extra_config_keys=["target", "cols"],
        )

        # Graph
        self.graph = StateGraph(ActionState)

    def route_reasoner(self, state: ActionState):
        """
        Route logic for the reasoner node.
        """
        return self.route_fail_fast_or_forward(state, "action_coder")

    def route_run_action(self, state: ActionState):
        """
        Route logic for running the action.

        Args:
            state (ActionState): The current state of the action process.

        Returns:
            str: The next node to transition to.
        """
        action_success = state["action_success"]
        fail_fast = state.get("fail_fast", False)
        error_message = state.get("error_message", None)
        go_with_error = state.get("go_with_error", False)

        if fail_fast:
            self.logger.warning(f"#### <font color='red'>Failed in RunActionCoder: {error_message}</font>")
            return "end"

        if action_success:
            self.logger.info("#### <font color='green'>Go forward to Action Evaluator</font>")
            return "action_evaluator"
        else:
            if go_with_error:
                self.logger.info(f"#### <font color='red'>{error_message}</font>")
                return "action_evaluator"
            else:
                self.logger.info("#### <font color='blue'>Go around to Action Debugger</font>")
                return "action_debugger"

    def route_action_debugger(self, state: ActionState):
        """
        Route logic for action debugger.
        """
        return self.route_fail_fast_or_forward(state, "run_action")

    def route_action_evaluator(self, state: ActionState):
        """
        Route logic for the action evaluator node.
        """
        return self.route_fail_fast_or_forward(state, "helper", "end_with_failure")

    def build(self):
        """
        Build the graph by adding nodes and edges.

        Returns:
            StateGraph: The compiled state graph.
        """
        # Nodes
        self.graph.add_node("reasoner", self.reasoner_node)
        self.graph.add_node("action_coder", self.action_coder_node)
        self.graph.add_node("run_action", self.run_action_node)
        self.graph.add_node("action_evaluator", self.action_evaluator_node)
        self.graph.add_node("action_debugger", self.action_debugger_node)
        self.graph.add_node("helper", self.helper_node)

        # Edges
        self.graph.add_edge(START, "reasoner")
        self.graph.add_conditional_edges(
            "reasoner",
            self.route_reasoner,
            {
                "action_coder": "action_coder",
                "end": END,
            },
        )
        self.graph.add_edge("action_coder", "run_action")

        self.graph.add_edge("action_coder", "run_action")
        self.graph.add_conditional_edges(
            "run_action",
            self.route_run_action,
            {
                "action_debugger": "action_debugger",
                "action_evaluator": "action_evaluator",
                "end": END,
            },
        )
        self.graph.add_conditional_edges(
            "action_debugger",
            self.route_action_debugger,
            {
                "run_action": "run_action",
                "end": END,
            },
        )
        self.graph.add_conditional_edges(
            "action_evaluator",
            self.route_action_evaluator,
            {
                "helper": "helper",
                "end_with_failure": END,
            },
        )

        self.graph.add_edge("helper", END)

        return self.graph.compile(checkpointer=self.memory)

    def __call__(self, state: ActionState, config: RunnableConfig) -> dict:
        """
        Execute the graph logic.

        Args:
            state (ActionState): The current state of the action process.
            config (RunnableConfig): Configuration details for the graph.

        Returns:
            dict: The result of the graph execution.
        """
        try:
            return self.app
        finally:
            # release the code interpreter
            self.code_interpreter.terminate()
