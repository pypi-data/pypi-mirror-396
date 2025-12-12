from typing import Dict, List, Optional, TypedDict

from baicai_base.utils.data import CodeStore


class WorkflowState(TypedDict):
    """State management for the workflow builder graph.

    Attributes:
        baseline_codes: Storage for baseline code versions and their results.
        messages: List of tuples containing user-assistant message history.
            Format: [("user", "request"), ("assistant", "response")]
        workflow_feedbacks: List of feedback messages from iterations.
            Format: [("user", "feedback")]
        workflow_codes: Storage for workflow code versions and their results.
        error_message: Error message if any occurs during execution.
        actions: List of accepted actions from action builder.
            Format: [{"id": int, "step_name": str, "sub_steps": List[str]}]
        workflow_success: Indicates if the workflow execution was successful.
        fail_fast: Flag to terminate execution on critical errors.
        workflow_iter: Counter for workflow code iterations.
        workflow_builder_iter: Counter for overall builder iterations.
    """

    baseline_codes: CodeStore
    messages: List[tuple[str, str]]
    workflow_feedbacks: List[tuple[str, str]]
    workflow_codes: CodeStore
    error_message: Optional[str]
    actions: List[Dict]
    workflow_success: bool
    fail_fast: bool
    workflow_iter: int
    workflow_builder_iter: int
