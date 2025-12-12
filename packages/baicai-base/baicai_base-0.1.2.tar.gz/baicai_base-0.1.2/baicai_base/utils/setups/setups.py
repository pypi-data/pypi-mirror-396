from langgraph.checkpoint.memory import MemorySaver


class Memory:
    """
    Memory class for graphs.
    """

    def __init__(self):
        # self.sqlite_memory = AsyncSqliteSaver.from_conn_string(
        #     "checkpoints.sqlite")
        self.memory = MemorySaver()


def setup_code_interpreter():
    """
    Setup the code interpreter. Defaults to LocalPythonInterpreter.
    """
    # This import is very slow, so we need to do it here.
    from baicai_base.utils.code import LocalPythonInterpreter

    return LocalPythonInterpreter()


def setup_memory():
    """
    Setup the memory. Defaults to Memory().memory.
    """
    return Memory().memory
