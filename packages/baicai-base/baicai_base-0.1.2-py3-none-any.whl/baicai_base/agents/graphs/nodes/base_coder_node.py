import logging
from typing import Any, Dict

from langchain_core.runnables import RunnableConfig

from baicai_base.agents.graphs.nodes.base_node import BaseNode
from baicai_base.agents.roles import coder
from baicai_base.utils.constants import PREV_FAIL_FAST
from baicai_base.utils.data import extract_code


class BaseCoderNode(BaseNode):
    """
    Base class for coder nodes that generate code using an LLM.
    """

    def __init__(
        self,
        llm: Any,
        logger: logging.Logger = None,
        graph_name: str = "ReActCoder",
        runnable: Any = coder,
        node_name: str = "BaseCoderNode",
    ) -> None:
        """
        Initialize the BaseCoderNode with a code template and an optional logger.

        Args:
            llm: The language model to be used for code generation.
            logger: Optional logger for logging information.
            graph_name: Name of the graph this node belongs to
            node_name: Name of this node
            runnable: The runnable to be used for code generation.
        """
        super().__init__(llm=llm, logger=logger)
        self.runnable = runnable() if callable(runnable) else None
        self.runnables = {}  # override by child class
        self.graph_name = graph_name
        self.node_name = node_name

    def _get_invoke_params(self, state: Dict, config: RunnableConfig) -> Dict:
        """
        Get parameters for the runnable invocation. Should be overridden by child classes.

        Args:
            state: The current state
            config: The runnable configuration

        Returns:
            Dict of parameters for runnable invocation
        """
        return {"messages": state["messages"]}

    def _get_state_updates(self, state: Dict, code: str) -> Dict:
        """
        Get state updates after code generation. Should be overridden by child classes.

        Args:
            state: The current state
            code: The generated code

        Returns:
            Dict of state updates
        """

        react_coder_codes = state.get("reactcoder_codes", [])
        react_coder_iter = state.get("reactcoder_iter", 0)
        react_coder_builder_iter = state.get("reactcoder_builder_iter", 1)

        react_coder_codes.append({"code": code})

        return {
            "reactcoder_iter": react_coder_iter,
            "reactcoder_builder_iter": react_coder_builder_iter,
            "reactcoder_codes": react_coder_codes,
        }

    def __call__(self, state: Dict, config: RunnableConfig) -> Dict:
        """
        Execute the coder node logic.

        Args:
            state: The current state
            config: Configuration for the runnable

        Returns:
            Updated state
        """
        fail_fast = state.get("fail_fast", False)
        if fail_fast:
            return {"fail_fast": True, "error_message": PREV_FAIL_FAST}

        # If runnable is not set, it is determined by task type
        if self.runnable is None:
            try:
                task_type = config["configurable"]["task_type"]
            except KeyError as err:
                raise ValueError("Task type is required for code generation") from err

            # Update runnable based on task type, if there is no task type, use the default runnable
            self.runnable = self.runnables.get(task_type, self.runnable)

        # Log graph and node names
        self.logger.info(f"""
# {self.graph_name or "Unknown Graph"}
## {self.node_name or "Unknown Node"}
""")

        # Get parameters for invocation
        invoke_params = self._get_invoke_params(state, config)

        self.logger.debug(f"- Invoking runnable with params: {invoke_params}")

        # Generate code using the runnable
        self.solution = self.runnable.invoke(invoke_params)

        # Extract code from the solution
        code = extract_code(self.solution.content)

        # Log the generated code
        self.logger.info(f"### Code generated: \n{self.solution.content}")

        # Get state updates from child class
        state_updates = self._get_state_updates(state, code)
        state_updates["fail_fast"] = False

        return state_updates
