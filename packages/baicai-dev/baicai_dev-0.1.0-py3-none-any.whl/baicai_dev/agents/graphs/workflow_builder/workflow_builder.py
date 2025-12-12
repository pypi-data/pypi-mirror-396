from typing import Any, Dict, List

from baicai_base.agents.graphs import ReActCoder

from baicai_dev.agents.graphs.workflow_builder.nodes import WorkflowCoderNode
from baicai_dev.agents.graphs.workflow_builder.state import WorkflowState
from baicai_dev.agents.roles.helper import helper
from baicai_dev.agents.roles.ml import debugger
from baicai_dev.utils.setups import ACTIONS_WITH_CODE_IRIS, BASELINE_CODES_IRIS


class WorkflowBuilder(ReActCoder):
    def __init__(
        self,
        llm=None,
        config=None,
        memory=None,
        logger=None,
        code_interpreter=None,
        actions: List[Dict[str, Any]] = ACTIONS_WITH_CODE_IRIS,
        baseline_codes: List[Dict[str, Any]] = BASELINE_CODES_IRIS,
        need_helper: bool = False,
    ) -> None:
        super().__init__(
            graph_name="Workflow",
            state_class=WorkflowState,
            coder_node_class=WorkflowCoderNode,
            debugger_role=debugger,
            helper_role=helper,
            need_helper=need_helper,
            llm=llm,
            config=config,
            memory=memory,
            logger=logger,
            code_interpreter=code_interpreter,
            actions=actions,
            baseline_codes=baseline_codes,
            debugger_extra_config_keys=["path", "ignored_features", "target"],
            helper_extra_config_keys=["target", "cols"],
        )
