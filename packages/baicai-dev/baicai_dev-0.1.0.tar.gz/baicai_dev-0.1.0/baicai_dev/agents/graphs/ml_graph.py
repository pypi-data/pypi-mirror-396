from typing import Dict, List, TypedDict

from baicai_base.services import LLM
from baicai_base.utils.data import CodeStore, ModelStore
from baicai_base.utils.setups import setup_memory
from langgraph.graph import END, START, StateGraph

from baicai_dev.agents.graphs.action_builder import ActionBuilder
from baicai_dev.agents.graphs.baseline_builder import BaselineBuilder
from baicai_dev.agents.graphs.optimization_builder import OptimizationBuilder
from baicai_dev.agents.graphs.workflow_builder import WorkflowBuilder
from baicai_dev.utils.setups import setup_ml_graph_config


class State(TypedDict):
    messages: List
    fail_fast: bool
    baseline_codes: CodeStore
    baseline_success: bool
    final_baseline_codes: CodeStore
    actions: List[Dict]
    action_success: bool
    workflow_codes: CodeStore
    workflow_success: bool
    optimization_codes: ModelStore
    optimization_success: bool


class MLGraph(StateGraph):
    """
    Main graph that orchestrates the ML workflow by connecting different builder components.

    The workflow follows this sequence:
    1. BaselineBuilder: Establishes baseline models and performance benchmarks
    2. ActionBuilder: Handles generating and validating hypotheses for model improvements
    3. WorkflowBuilder: Manages the creation of ML workflows
    4. OptimizationBuilder: Implements optimization strategies and hyperparameter tuning

    Attributes:
        config: Configuration for the graph
        baseline_builder: Instance of BaselineBuilder
        action_builder: Instance of ActionBuilder
        workflow_builder: Instance of WorkflowBuilder
        optimization_builder: Instance of OptimizationBuilder
        app: The compiled state graph
    """

    def __init__(
        self,
        config=None,
        memory=None,
        start_builder="baseline_builder",
        baseline_codes=None,
        actions=None,
        workflow_codes=None,
        need_helper=False,
        code_interpreter=None,
        llm=None,
    ):
        """
        Initialize the MLGraph with configuration and memory.

        Args:
            config: Configuration for the graph. Defaults to setup_ml_graph_config().
            memory: Memory for state persistence. Defaults to setup_memory().
            start_builder: The builder to start from. Can be "baseline_builder", "action_builder",
                         "workflow_builder", or "optimization_builder". Defaults to "baseline_builder".
            baseline_codes: Required if starting from action_builder or workflow_builder.
            actions: Required if starting from workflow_builder.
            workflow_codes: Required if starting from optimization_builder.
            need_helper: Whether to enable helper functionality. Defaults to False.
            code_interpreter: Code interpreter instance. Defaults to None.
            llm: Language model instance. Defaults to None (uses LLM().llm).
        """
        # Initialize configuration
        self.config = config or setup_ml_graph_config()
        self.memory = memory or setup_memory()
        self.llm = llm or LLM().llm
        self.start_builder = start_builder

        # Validate dependencies based on start_builder
        self._validate_dependencies(
            start_builder=start_builder, baseline_codes=baseline_codes, actions=actions, workflow_codes=workflow_codes
        )

        # Initialize builder components with appropriate dependencies
        self.baseline_builder = BaselineBuilder(
            llm=self.llm,
            config=self.config,
            memory=self.memory,
            need_helper=need_helper,
            code_interpreter=code_interpreter,
        )

        self.action_builder = ActionBuilder(
            llm=self.llm,
            config=self.config,
            memory=self.memory,
            baseline_codes=baseline_codes if start_builder in ["action_builder", "workflow_builder"] else None,
            need_helper=need_helper,
            code_interpreter=code_interpreter,
        )

        self.workflow_builder = WorkflowBuilder(
            llm=self.llm,
            config=self.config,
            memory=self.memory,
            baseline_codes=baseline_codes if start_builder == "workflow_builder" else None,
            actions=actions if start_builder == "workflow_builder" else None,
            need_helper=need_helper,
            code_interpreter=code_interpreter,
        )

        self.optimization_builder = OptimizationBuilder(
            llm=self.llm,
            config=self.config,
            memory=self.memory,
            workflow_codes=workflow_codes if start_builder == "optimization_builder" else None,
            need_helper=need_helper,
            code_interpreter=code_interpreter,
        )

        self.helper_node = self.optimization_builder.helper_node

        # Initialize the state graph
        super().__init__(State)

        # Add nodes to the graph
        self.add_node("baseline_builder", self.baseline_builder.app)
        self.add_node("action_builder", self.action_builder.app)
        self.add_node("workflow_builder", self.workflow_builder.app)
        self.add_node("optimization_builder", self.optimization_builder.app)

        # Build the graph based on start_builder
        self._build_graph()

        # Compile the graph
        self._app = self.compile(checkpointer=self.memory)

    def _validate_dependencies(self, start_builder, baseline_codes, actions, workflow_codes):
        """
        Validate that all required dependencies are provided based on the start_builder.

        Args:
            start_builder: The builder to start from
            baseline_codes: Baseline codes for action and workflow builders
            actions: Actions for workflow builder
            workflow_codes: Workflow codes for optimization builder

        Raises:
            ValueError: If required dependencies are missing
        """
        if start_builder == "action_builder":
            if baseline_codes is None:
                raise ValueError("baseline_codes is required when starting from action_builder")

        elif start_builder == "workflow_builder":
            if baseline_codes is None:
                raise ValueError("baseline_codes is required when starting from workflow_builder")
            if actions is None:
                raise ValueError("actions is required when starting from workflow_builder")

        elif start_builder == "optimization_builder":
            if workflow_codes is None:
                raise ValueError("workflow_codes is required when starting from optimization_builder")

    def _initialize_state(self):
        """
        Initialize the state based on the start_builder and provided dependencies.
        """
        initial_state = {"messages": [], "fail_fast": False}

        # Add necessary state based on start_builder
        if self.start_builder in ["action_builder", "workflow_builder"]:
            initial_state.update({"baseline_codes": self.baseline_codes, "baseline_success": True})

        if self.start_builder == "workflow_builder":
            initial_state.update({"actions": self.actions, "action_success": True})

        if self.start_builder == "optimization_builder":
            initial_state.update({"workflow_codes": self.workflow_codes, "workflow_success": True})

        return initial_state

    def _build_graph(self):
        """
        Build the graph connections based on start_builder.
        """
        # Define the builder sequence
        builder_sequence = ["baseline_builder", "action_builder", "workflow_builder", "optimization_builder"]

        # Find the starting point in the sequence
        try:
            start_index = builder_sequence.index(self.start_builder)
        except ValueError:
            raise ValueError(f"Invalid start_builder: {self.start_builder}. Must be one of {builder_sequence}")

        # Connect only the builders from the starting point
        remaining_builders = builder_sequence[start_index:]

        # Connect START to first builder
        self.add_edge(START, remaining_builders[0])

        # Connect remaining builders in sequence
        for i in range(len(remaining_builders) - 1):
            self.add_edge(remaining_builders[i], remaining_builders[i + 1])

        # Always connect the last builder to END
        self.add_edge(remaining_builders[-1], END)

    def __call__(self, inputs=None):
        """
        Execute the graph with proper initial state.

        Args:
            inputs: Optional additional inputs for the graph

        Returns:
            The result of graph execution
        """
        # Initialize state with dependencies
        initial_state = self._initialize_state()

        # Merge with any additional inputs
        if inputs:
            initial_state.update(inputs)

        return self.app(initial_state)

    @property
    def app(self):
        """
        Returns the compiled graph application.
        """
        return self._app
