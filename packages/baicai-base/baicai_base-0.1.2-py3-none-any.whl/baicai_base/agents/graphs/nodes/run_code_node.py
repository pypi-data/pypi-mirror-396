import difflib
import logging

from langchain_core.runnables import RunnableConfig

from baicai_base.agents.graphs.nodes import BaseNode
from baicai_base.utils.constants import (
    EXTRA_PACKAGE_NEEDED,
    MAX_ITER_EXCEEDED,
    MAX_ITER_EXCEEDED_NO_GRAPH_SUCCESS,
)


class RunCodeNode(BaseNode):
    """
    Node for running code and handling iterations.

    Attributes:
        logger (logging.Logger): Logger for logging messages. Defaults to None.
        code_interpreter: Instance for interpreting code. Defaults to class attribute.
        name (str): Name of the node. Defaults to None.
        graph_name (str): Name of the graph. Defaults to None.
        fail_fast (bool): Whether to fail fast. Defaults to False.
        save (bool): Whether to save the results. Defaults to False.
        max_iter (int): Maximum number of iterations for running code. Defaults to MAX_ITER.
        max_graph_iter (int): Maximum number of iterations for the graph. Defaults to MAX_ITER.
        one_pass_graph (bool): Whether to run the graph in one pass. Defaults to True.
    """

    code_interpreter = None  # Class attribute for code interpreter

    def __init__(
        self,
        logger: logging.Logger = None,
        code_interpreter=None,
        name: str = None,
        graph_name: str = None,
        save: bool = False,
        max_iter: int = 3,
        max_graph_iter: int = 3,
        one_pass_graph: bool = True,
    ):
        """
        Initialize the RunCodeNode with a logger, code interpreter, and other parameters.
        """
        super().__init__(logger=logger, name=name, graph_name=graph_name)

        if RunCodeNode.code_interpreter is None:
            from baicai_base.utils.setups import setup_code_interpreter

            RunCodeNode.code_interpreter = setup_code_interpreter()
        self.code_interpreter = code_interpreter or RunCodeNode.code_interpreter
        self.fail_fast = False
        self.save = save
        self.max_iter = max_iter
        self.max_graph_iter = max_graph_iter
        self.one_pass_graph = one_pass_graph

    async def __call__(self, state, config: RunnableConfig):
        """
        Execute the node logic.

        Args:
            state (dict): The current state of the process.
            config (RunnableConfig): Configuration details for the node.

        Returns:
            dict: Updated state after execution.
        """
        self._initialize_state(state)

        self._log_initial_info()

        self.solution, self.success = await self._execute_code()

        self._log_run_result()

        self._update_codes()

        if self.success:
            self._handle_success()
        else:
            self._handle_error()
        self._set_re_run()

        return self._finalize_result()

    def _initialize_state(self, state):
        """
        Initialize the state for code execution.

        Args:
            state (dict): The current state of the process.
        """
        self.success = state.get(f"{self.graph_name}_success", True)
        self.messages = state.get("messages", [])
        self.iter = state.get(f"{self.name}_iter", 0) + 1
        self.error_message = state.get("error_message", "")
        self.codes = state.get(f"{self.graph_name}_codes", [])
        self.feedbacks = state.get(f"{self.graph_name}_feedbacks", [])
        self.code_to_run = self.codes[-1] if self.codes else {}
        self.graph_iter = state.get(f"{self.graph_name}_builder_iter", 1)
        self.re_run = state.get("re_run", True)

    def _log_initial_info(self):
        """
        Log initial information about the code execution.
        """
        name = self.name.capitalize()
        self.logger.info(f"## Running {name} Code")
        self.logger.info(f"### {name} Iteration: {self.iter}")

    def _handle_success(self):
        """
        Handle successful code execution.
        """
        self.iter = 0
        self.code_to_run["error"] = ""
        if self.save:
            self._save()

    def _save(self):
        """
        Save the results. To be implemented in subclasses.
        """
        raise NotImplementedError("This method should be implemented in the subclass")

    async def _execute_code(self):
        """
        Execute the code using the code interpreter.

        Returns:
            tuple: The solution and success status.
        """
        try:
            if not self.code_to_run["code"].strip():
                return "You generated nothing, please try again.", False
            return await self.code_interpreter.run(self.code_to_run["code"])
        except Exception as e:
            self.logger.error(f"Error: {str(e)}")
            return f"An error occurred: {str(e)}", False

    def _log_run_result(self):
        """
        Log the result of the code execution.
        """
        status = "Success" if self.success else "Failed"
        self.logger.info(f"- Run Code {status}")
        self.logger.info(f"- Code run result: \n```sh\n{self.solution}\n```")

    def _update_codes(self):
        """
        Update the codes with the result of the execution.
        """
        self.code_to_run.update({"success": self.success, "result": self.solution})

    def _handle_error(self):
        """
        Handle errors during code execution.
        """
        if self.iter >= self.max_iter:
            # if only allow one pass graph or the first graph iteration failed for multi run graph
            if self.one_pass_graph or (not self.one_pass_graph and self.graph_iter == 1):
                self.error_message = MAX_ITER_EXCEEDED if self.one_pass_graph else MAX_ITER_EXCEEDED_NO_GRAPH_SUCCESS
                self.fail_fast = True
                return

        self.code_to_run["error"] = self.code_to_run["result"]

        # If the error is a ModuleNotFoundError, fail fast
        if "ModuleNotFoundError: No module named" in self.code_to_run["error"]:
            self.logger.error(self.code_to_run["error"])
            self.error_message = EXTRA_PACKAGE_NEEDED
            self.fail_fast = True
            return

        error_message = (
            f"You got some mistake in your previous code. Please re-complete the code to fix the error.\n"
            f"Here is the previous version:\n```python\n{self.code_to_run['code']}\n```\n"
            f"When we run the above code, it raises this error:\n```sh\n{self.code_to_run['error']}\n```"
        )

        error_message = self._edit_error_message(error_message)

        self.feedbacks.append(("user", error_message))

    def _set_re_run(self):
        """
        Set the re-run flag.
        """
        if self.one_pass_graph:
            self.re_run = False
        elif not self.success and self.graph_iter < self.max_graph_iter and self.iter == self.max_iter:
            self.re_run = True
        else:
            self.re_run = False

    def _get_diff(self, before: str, after: str) -> str:
        """
        Get the diff between two versions of code.

        Args:
            before (str): The previous version of the code.
            after (str): The current version of the code.

        Returns:
            str: The diff between the two versions.
        """
        return "".join(difflib.unified_diff(before.splitlines(keepends=True), after.splitlines(keepends=True)))

    def _edit_error_message(self, error_message):
        """
        Handle cases where the iteration count exceeds 2.

        Args:
            error_message (str): The error message to be logged.
        """
        try:
            if self.iter >= 2:
                diff = self._get_diff(self.codes[-2]["code"], self.code_to_run["code"])
                self.code_to_run["edits"] = diff
                error_message += (
                    f"\nHere is the diff between the previous version and the current version:\n```python\n{diff}\n```"
                )
        except Exception as e:
            self.logger.error(f"Error: {str(e)}. Ignore if you are testing.")

        return error_message

    def _finalize_result(self):
        """
        Finalize the result after code execution.

        Returns:
            dict: The final result.
        """
        if self.fail_fast:
            return {"fail_fast": self.fail_fast, "error_message": self.error_message}

        return {
            "messages": self.messages,
            f"{self.graph_name}_success": self.success,
            f"{self.name}_iter": self.iter,
            f"{self.name}_codes": self.codes,
            f"{self.graph_name}_feedbacks": self.feedbacks,
            "fail_fast": self.fail_fast,
            "error_message": self.error_message,
            "re_run": self.re_run,
        }
