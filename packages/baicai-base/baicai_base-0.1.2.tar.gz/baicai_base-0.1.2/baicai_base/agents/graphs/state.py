from typing import List, Optional, TypedDict

from baicai_base.utils.data import CodeStore


class ReActCoderState(TypedDict):
    """State management for the react coder graph.

    Attributes:
        messages: List of tuples containing user-assistant message history.
            Format: [("user", "request"), ("assistant", "response")]
        react_coder_feedbacks: List of feedback messages from iterations.
            Format: [("user", "feedback")]
        react_coder_codes: Storage for code versions and their execution results.
        error_message: Error message if any occurs during execution.
        react_coder_success: Indicates if the react coder execution was successful.
        fail_fast: Flag to terminate execution on critical errors.
        react_coder_builder_iter: Counter for overall builder iterations.
        react_coder_iter: Counter for react coder model iterations.
    """

    messages: List[tuple[str, str]]
    reactcoder_feedbacks: List[tuple[str, str]]
    reactcoder_codes: CodeStore
    error_message: Optional[str]
    reactcoder_success: bool
    fail_fast: bool
    reactcoder_builder_iter: int
    reactcoder_iter: int
