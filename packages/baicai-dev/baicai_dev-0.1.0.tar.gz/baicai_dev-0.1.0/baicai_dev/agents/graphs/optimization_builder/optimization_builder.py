from baicai_base.agents.graphs import ReActCoder

from baicai_dev.agents.graphs.optimization_builder.nodes import HyperparamTunerNode
from baicai_dev.agents.graphs.optimization_builder.state import OptimizationState
from baicai_dev.agents.roles.helper import helper
from baicai_dev.agents.roles.ml import debugger
from baicai_dev.utils.setups import WORKFLOW_CODE_IRIS


class OptimizationBuilder(ReActCoder):
    def __init__(
        self,
        llm=None,
        config=None,
        memory=None,
        logger=None,
        code_interpreter=None,
        workflow_codes=WORKFLOW_CODE_IRIS,
        need_helper=True,
    ) -> None:
        super().__init__(
            graph_name="Optimization",
            state_class=OptimizationState,
            coder_node_class=HyperparamTunerNode,
            llm=llm,
            debugger_role=debugger,
            helper_role=helper,
            need_helper=need_helper,
            config=config,
            memory=memory,
            logger=logger,
            code_interpreter=code_interpreter,
            workflow_codes=workflow_codes,
            debugger_extra_config_keys=["path", "ignored_features", "target"],
            helper_extra_config_keys=["cols", "target"],
        )
