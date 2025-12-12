import logging
from typing import List

from langchain_core.runnables import RunnableConfig

from baicai_base.agents.graphs.nodes import BaseNode
from baicai_base.agents.roles import debugger
from baicai_base.utils.data import extract_code


class DebuggerNode(BaseNode):
    """
    Node responsible for generating debug suggestions.
    """

    def __init__(
        self,
        llm,
        logger: logging.Logger = None,
        graph_name: str = None,
        role=debugger,
        one_pass_graph: bool = True,
        extra_config_keys: List[str] = None,
    ):
        """
        Initialize the DebuggerNode.

        Args:
            llm: The language model for generating debug suggestions.
            logger (logging.Logger): Optional logger for logging information.
            graph_name (str): Name of the graph.
            extra_config_keys (List[str]): List of extra config keys to be used for code generation.
        """
        super().__init__(llm=llm, logger=logger, graph_name=graph_name)
        self.runnable = role(self.llm)
        self.one_pass_graph = one_pass_graph
        self.error_message = ""
        self.extra_config_keys = extra_config_keys

    def __call__(self, state, config: RunnableConfig):
        """
        Execute the node logic.

        Args:
            state (dict): The current state of the process.
            config (RunnableConfig): Configuration details for the node.

        Returns:
            dict: Updated state after execution.
        """
        messages = state["messages"]
        codes = state.get(f"{self.graph_name}_codes", [])
        feedbacks = state.get(f"{self.graph_name}_feedbacks", [])
        self.feedbacks = feedbacks[-1]

        # Extract configuration details for code generation
        config_dict = {}
        if self.extra_config_keys is not None:
            for key in self.extra_config_keys:
                config_dict[key] = config["configurable"][key]

        self.logger.info("## Debugging ...")

        self.solution = self.runnable.invoke(
            {
                "feedbacks": self.feedbacks,
                "messages": messages,
                **config_dict,
            }
        )

        try:
            code = extract_code(self.solution.content)
            codes.append({"code": code})
        except Exception as e:
            self.error_message = f"Error extracting code: {e}"
            self.logger.error(self.error_message)
            return {"fail_fast": True, "error_message": self.error_message}

        self.logger.info(self.solution.content)

        return {
            f"{self.graph_name}_codes": codes,
            "fail_fast": False,
            "error_message": self.error_message,
        }
