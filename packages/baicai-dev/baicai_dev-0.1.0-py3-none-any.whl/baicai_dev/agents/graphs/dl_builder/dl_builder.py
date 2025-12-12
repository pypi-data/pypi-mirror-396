from baicai_base.agents.graphs import ReActCoder

from baicai_dev.agents.graphs.dl_builder.nodes import DLCoderNode
from baicai_dev.agents.graphs.dl_builder.state import DLBuilderState
from baicai_dev.agents.roles.dl import debugger
from baicai_dev.agents.roles.helper import helper


class DLBuilder(ReActCoder):
    """Deep Learning workflow builder using fastai."""

    def __init__(self, llm=None, config=None, memory=None, logger=None, code_interpreter=None, need_helper=False):
        super().__init__(
            graph_name="DL",
            state_class=DLBuilderState,
            coder_node_class=DLCoderNode,
            debugger_role=debugger,
            helper_role=helper,
            llm=llm,
            config=config,
            memory=memory,
            logger=logger,
            code_interpreter=code_interpreter,
            need_helper=need_helper,
        )
