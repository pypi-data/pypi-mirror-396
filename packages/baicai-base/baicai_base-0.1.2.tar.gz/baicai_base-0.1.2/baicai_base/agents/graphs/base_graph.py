import logging
import uuid
from abc import abstractmethod
from typing import Any, Dict

from IPython.display import Image, display
from langchain_core.runnables import RunnableConfig

from baicai_base.agents.graphs.nodes import BaseNode
from baicai_base.utils.setups import setup_memory


class BaseGraph(BaseNode):
    """
    Base class for graphs, inheriting from BaseNode.

    Attributes:
        llm: An instance of the LLM for code generation. Defaults to None.
        config: Custom configuration for the graph. Defaults to a setup configuration.
        memory: Memory for the baseline builder. Defaults to a setup_memory().
        logger: Logger for logging messages. Defaults to None.
        graph: LangGraph StateGraph object.
        app: The compiled state graph.
    """

    def __init__(
        self, llm: Any = None, config: Dict[str, Any] = None, memory: Any = None, logger: logging.Logger = None
    ) -> None:
        """
        Initialize the graph with configuration, memory, and other parameters.
        """
        super().__init__(llm=llm, logger=logger)

        if config is None:
            self.logger.warning("Using default configuration")

            self.config = {
                "configurable": {
                    "thread_id": str(uuid.uuid4()),
                },
            }
        else:
            self.config = config

        self.memory = memory or setup_memory()
        self.graph = None

    @property
    def app(self):
        if not hasattr(self, "_app"):
            self._app = self.build()
        return self._app

    @abstractmethod
    def build(self):
        """
        Abstract method to build the graph. Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses should implement this method.")

    def draw(self):
        """
        Display the graph using Mermaid.js.
        """
        display(Image(self.app.get_graph(xray=True).draw_mermaid_png()))

    def get_graph(self, xray=False):
        """
        Retrieve the graph.

        Args:
            xray (bool): Whether to include xray details. Defaults to False.

        Returns:
            Graph: The graph object.
        """
        return self.app.get_graph(xray=xray)

    def route_fail_fast_or_forward(self, state: Dict[str, Any], success_node: str, fail_node: str = "end"):
        """
        Fail fast if fail_fast is True, otherwise go forward.

        Parameters:
            state (State): The current state.
            success_node (str): The node to transition to if fail_fast is False.
            fail_node (str): The node to transition to if fail_fast is True. Defaults to "end".

        Returns:
            str: The next node to transition to.
        """
        fail_fast = state.get("fail_fast", False)
        error_message = state.get("error_message", None)
        if fail_fast:
            self.logger.warning(f"#### <font color='red'>Failed because: {error_message}</font>")
            return fail_node
        return success_node

    def route_fail_fast_or_forward_with_retry(
        self, state: Dict[str, Any], success_node: str, retry_node: str, success_key: str, fail_node: str = "end"
    ):
        """
        Fail fast if fail_fast is True, otherwise go forward if success or retry if not success.

        Args:
            state: The current state of the graph.
            success_node: The node to transition to if success.
            retry_node: The node to transition to if not success but not fail_fast.
            success_key: The key to check for success.
            fail_node: The node to transition to if fail_fast is True.

        Returns:
            str: The next node to transition to.
        """
        success = state.get(success_key, False)
        fail_fast = state.get("fail_fast", False)
        error_message = state.get("error_message", None)

        if fail_fast:
            self.logger.warning(f"#### <font color='red'>Failed because: {error_message}</font>")
            return fail_node
        if success:
            self.logger.info(f"#### <font color='green'>Successfully run and go to {success_node}</font>")
            return success_node
        else:
            self.logger.info(f"#### <font color='blue'>Go around to {retry_node}</font>")
            return retry_node

    def __call__(self, state: Dict[str, Any], config: RunnableConfig):
        """
        Execute the graph logic.

        Args:
            state: The current state of the graph process.
            config (RunnableConfig): Configuration details for the graph.

        Returns:
            App: The application instance.
        """
        return self.app
