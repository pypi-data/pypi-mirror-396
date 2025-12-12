from baicai_base.agents.graphs import ReActCoder

from baicai_dev.agents.graphs.baseline_builder.nodes import BaselineCoderNode
from baicai_dev.agents.graphs.baseline_builder.state import BaselineState
from baicai_dev.agents.roles.helper import helper
from baicai_dev.agents.roles.ml import debugger


class BaselineBuilder(ReActCoder):
    def __init__(
        self, llm=None, config=None, memory=None, logger=None, code_interpreter=None, need_helper=True
    ) -> None:
        super().__init__(
            graph_name="Baseline",
            state_class=BaselineState,
            coder_node_class=BaselineCoderNode,
            debugger_role=debugger,
            helper_role=helper,
            need_helper=need_helper,
            llm=llm,
            config=config,
            memory=memory,
            logger=logger,
            code_interpreter=code_interpreter,
            debugger_extra_config_keys=["path", "ignored_features", "target"],
            helper_extra_config_keys=["target", "cols"],
        )
