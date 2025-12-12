from typing import Annotated, List, TypedDict

from baicai_base.utils.data import CodeStore, ModelStore
from langgraph.graph.message import add_messages

from baicai_dev.configs import ConfigData


class DLBuilderState(TypedDict):
    """State management for the DL builder graph.

    Attributes:
        messages: List of message history
        task_type: Selected task type (e.g., 'tabular', 'vision', 'nlp')
        data_config: Data configuration settings following ConfigData structure
        dl_iter: Iteration number
        dl_codes: List of generated code versions following CodeStore structure
        dl_models: List of trained models following ModelStore structure
        dl_feedbacks: List of feedback messages
        dl_success: Execution success status
        error_message: Error message if any
        fail_fast: Flag to terminate on critical errors
    """

    messages: Annotated[list, add_messages]
    task_type: str  # TaskType 枚举的值
    data_config: ConfigData
    dl_iter: int
    dl_codes: CodeStore
    dl_models: ModelStore
    dl_feedbacks: List[tuple[str, str]]
    dl_success: bool
    error_message: str
    fail_fast: bool
