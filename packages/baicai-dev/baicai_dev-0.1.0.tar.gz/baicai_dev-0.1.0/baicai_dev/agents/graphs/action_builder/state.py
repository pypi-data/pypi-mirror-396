from typing import Dict, List, Optional, TypedDict

from baicai_base.utils.data import CodeStore


class ActionState(TypedDict):
    """State management for the action builder graph.

    Attributes:
        messages: List of tuples containing user-assistant message history.
            Format: [("user", "request"), ("assistant", "response")]
        baseline_codes: Storage for baseline code versions and their results.
        error_message: Error message if any occurs during execution.
        actions: Generated actions about the model and data.
            Format: [{"id": int, "action": str}]
        load_data_code: Code block for data loading and preprocessing.
            Format: [{"code": str}]
        action_success: Indicates if all actions were successfully executed.
        fail_fast: Flag to terminate execution on critical errors.
        go_with_error: Flag to continue execution despite non-critical errors.
        action_iter: Counter for action iterations.
        action_codes: Storage for action code versions and their results.
            Format: [{"code": str}]
    """

    messages: List[tuple[str, str]]
    baseline_codes: CodeStore
    error_message: Optional[str]
    actions: List[Dict]
    load_data_code: Dict
    action_success: bool
    fail_fast: bool
    go_with_error: bool
    action_iter: int
    action_codes: List[str]
