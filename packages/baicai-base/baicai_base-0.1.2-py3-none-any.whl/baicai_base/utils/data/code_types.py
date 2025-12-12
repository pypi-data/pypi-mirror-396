from typing import List, TypedDict


class Code(TypedDict):
    """Represents a code generation result.

    This type is used to store information about generated code, including:
    - The actual code content
    - Execution results
    - Any modifications made
    - Error information
    - Success status
    - Feedback and evaluation

    Attributes:
        code: The generated code string
        result: The execution result
        edits: Any modifications made to the code
        error: Error message if execution failed
        success: Whether the code execution was successful
        ignore: Whether to ignore this code version
        feedbacks: Feedback messages about the code
    """

    code: str
    result: str
    edits: str
    error: str
    success: bool
    ignore: bool
    feedbacks: str


class Model(Code):
    """Represents a trained model and its associated code.

    Extends Code with model-specific attributes for tracking trained models.
    This type is used to manage model versions, their code, and performance.

    Attributes:
        model_path: Path to the saved model file
        best_model: Whether this is the best performing model
    """

    model_path: str
    best_model: bool


CodeStore = List[Code]
"""A collection of code generation results."""

ModelStore = List[Model]
"""A collection of trained models and their associated code."""
