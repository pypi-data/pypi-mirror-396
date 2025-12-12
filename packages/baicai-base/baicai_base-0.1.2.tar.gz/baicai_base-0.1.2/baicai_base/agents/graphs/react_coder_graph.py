import logging
from typing import Any, Dict, List, Type

from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph

from baicai_base.agents.graphs.base_graph import BaseGraph
from baicai_base.agents.graphs.nodes import BaseCoderNode, DebuggerNode, HelperNode, RunCodeNode
from baicai_base.agents.graphs.state import ReActCoderState
from baicai_base.agents.roles import debugger, helper
from baicai_base.services import LLM


class ReActCoder(BaseGraph):
    """
    ReActCoder base class for graphs that share similar graph structure.
                                +-----------+
                                | __start__ |
                                +-----------+
                                       *
                                       *
                                       *
                                +-------------+
                                |  some_coder |
                                +-------------+
                            ...                 .....
                            .                         ....
                        ..                              .....
                    +----------+                          ...
                    | run_code |                            .
                    +----------+                            .
                  ...            ...                            .
               ..                  ..                           .
             ..                      ..                         .
    +---------------+                 .                      ...
    | code_debugger |                 .                   .....
    +---------------+                 .               ....
                       ....            .           .....
                           .....       .      .....
                                ...    .   ...
                                 +---------+
                                 |  helper |
                                 +---------+
                                      *
                                      *
                                      *
                                 +---------+
                                 | __end__ |
                                 +---------+

    """

    def __init__(
        self,
        graph_name: str = "ReActCoder",
        state_class: Type = None,
        coder_node_class: Type = None,
        debugger_role: Type = debugger,
        helper_role: Type = helper,
        need_helper: bool = False,
        llm: Any = None,
        config: Dict[str, Any] = None,
        memory: Any = None,
        logger: logging.Logger = None,
        code_interpreter: Any = None,
        debugger_extra_config_keys: List[str] = None,
        helper_extra_config_keys: List[str] = None,
        **kwargs,
    ) -> None:
        """
        Initialize the ReActCoder with shared configuration and components.

        Args:
            graph_name: Name of the graph (e.g. "Workflow", "Baseline")
            state_class: State class to use for the graph
            coder_node_class: Coder node class to use
            debugger_role: Debugger role to use, default is ML.debugger
            helper_role: Helper role to use, default is ML.helper
            llm: Language model instance
            config: Graph configuration
            memory: Memory configuration
            logger: Logger instance
            code_interpreter: Code interpreter instance
            **kwargs: Additional arguments passed to coder node
        """
        super().__init__(llm=llm, config=config, memory=memory, logger=logger)

        self.llm = llm or LLM().llm
        self.graph_name = graph_name
        self.state_class = state_class or ReActCoderState
        self.coder_node_class = coder_node_class or BaseCoderNode
        self.debugger_role = debugger_role or debugger
        self.helper_role = helper_role or helper
        self.need_helper = need_helper
        # Setup code interpreter
        if code_interpreter is None:
            from baicai_base.utils.setups import setup_code_interpreter

            self.code_interpreter = setup_code_interpreter()
        else:
            self.code_interpreter = code_interpreter

        # Initialize nodes
        self.coder_node = self.coder_node_class(llm=self.llm, **kwargs)
        self.run_node = RunCodeNode(
            code_interpreter=self.code_interpreter,
            name=self.graph_name,
            graph_name=self.graph_name,
            one_pass_graph=True,
        )
        self.debugger_node = DebuggerNode(
            llm=self.llm,
            graph_name=self.graph_name,
            role=self.debugger_role,
            one_pass_graph=True,
            extra_config_keys=debugger_extra_config_keys,
        )
        self.helper_node = HelperNode(
            llm=self.llm,
            graph_name=self.graph_name,
            role=self.helper_role,
            code_interpreter=self.code_interpreter,
            one_pass_graph=True,
            by_pass=not self.need_helper,
            extra_config_keys=helper_extra_config_keys,
        )
        # Initialize graph
        self.graph = StateGraph(self.state_class)

    def route_coder(self, state):
        """Route logic for coder node."""
        return self.route_fail_fast_or_forward(state, f"run_{self.graph_name.lower()}")

    def route_run(self, state):
        """Route logic for run node."""
        return self.route_fail_fast_or_forward_with_retry(
            state, "helper", f"{self.graph_name.lower()}_debugger", f"{self.graph_name.lower()}_success"
        )

    def route_debugger(self, state):
        """Route logic for debugger node."""
        return self.route_fail_fast_or_forward(state, f"run_{self.graph_name.lower()}")

    def build(self):
        """Build the graph with nodes and edges."""
        # Add nodes
        coder = f"{self.graph_name.lower()}_coder"
        runner = f"run_{self.graph_name.lower()}"
        debugger = f"{self.graph_name.lower()}_debugger"
        helper = f"{self.graph_name.lower()}_helper"

        self.graph.add_node(coder, self.coder_node)
        self.graph.add_node(runner, self.run_node)
        self.graph.add_node(debugger, self.debugger_node)
        self.graph.add_node(helper, self.helper_node)
        # Add edges
        self.graph.add_edge(START, coder)

        self.graph.add_conditional_edges(
            coder,
            self.route_coder,
            {
                runner: runner,
                "helper": helper,
            },
        )

        self.graph.add_conditional_edges(
            runner,
            self.route_run,
            {
                debugger: debugger,
                "helper": helper,
            },
        )

        self.graph.add_conditional_edges(
            debugger,
            self.route_debugger,
            {
                runner: runner,
                "helper": helper,
            },
        )

        self.graph.add_edge(helper, END)

        return self.graph.compile(checkpointer=self.memory)

    def __call__(self, state: Dict[str, Any], config: RunnableConfig) -> dict:
        """Execute the graph logic."""
        try:
            return self.app
        finally:
            self.code_interpreter.terminate()
