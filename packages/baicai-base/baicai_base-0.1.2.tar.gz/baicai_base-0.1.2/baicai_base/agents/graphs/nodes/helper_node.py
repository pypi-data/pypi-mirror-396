import asyncio
import logging
from typing import Any, AsyncGenerator, Dict, List

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig

from baicai_base.agents.graphs.nodes import BaseNode
from baicai_base.agents.roles import helper
from baicai_base.utils.data import extract_code
from baicai_base.utils.setups import setup_code_interpreter


class HelperNode(BaseNode):
    """
    Node responsible for generating helper responses in real-time.
    """

    def __init__(
        self,
        llm,
        logger: logging.Logger = None,
        graph_name: str = None,
        role=helper,
        code_interpreter=None,
        one_pass_graph: bool = True,
        by_pass: bool = False,
        extra_config_keys: List[str] = None,
    ):
        """
        Initialize the HelperNode.

        Args:
            llm: The language model for generating helps.
            logger (logging.Logger): Optional logger for logging information.
            role: The role for generating helps.
            graph_name (str): Name of the graph.
        """
        super().__init__(llm=llm, logger=logger, graph_name=graph_name)
        self.code_interpreter = code_interpreter or setup_code_interpreter()
        self.runnable = role(self.llm, self.code_interpreter)
        self.one_pass_graph = one_pass_graph
        self.error_message = ""
        self.by_pass = by_pass
        self.first_in = True
        self.extra_config_keys = extra_config_keys

    async def __call__(self, state: Dict[str, Any], config: RunnableConfig) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute the node logic asynchronously.

        Args:
            state (dict): The current state of the process.
            config (RunnableConfig): Configuration details for the node.

        Yields:
            dict: Updated state after each interaction.
        """
        if self.by_pass:
            return

        messages = state.get("messages", [])
        codes = state.get(f"{self.graph_name}_codes", [])
        last_code = codes[-1] if codes else None
        from_web_ui = config["configurable"].get("from_web_ui", False)
        config_dict = {}
        if self.extra_config_keys is not None:
            for key in self.extra_config_keys:
                config_dict[key] = config["configurable"][key]
        re_try = False
        last_input = ""

        if from_web_ui:
            # Get the last user message
            if not messages:
                yield {"messages": messages}
                return

            # 第一次进入时，整个图已经运行过了，理论上最后一个消息是AI消息，直接返回
            last_response = messages[-1]
            if self.first_in and isinstance(last_response, AIMessage):
                self.first_in = False
                yield {"messages": messages}
                return

            # 不是第一次进入，且最后一个消息不是HumanMessage，则报错
            elif not isinstance(last_response, HumanMessage):
                error_msg = "Invalid message format: expected HumanMessage"
                yield {"chunk": f"❌ {error_msg}", "messages": messages}
                return

            # Add context code if available
            if last_code:
                context_code = f"""
## Context_Code
```python
{last_code}
```

If you need to use the data, you MUST refer to the following information:
```python
{config_dict}
```
"""
                content = last_response.content + "\n" + context_code  # 这时候的last_message肯定是HumanMessage
                input_message = HumanMessage(content=content)
            else:  # 如果context_code不存在，则直接使用last_message
                input_message = last_response

            # Deepseek 不会自己停下来，所以需要一个标志位来判断是否已经输出最终答案
            is_final_answer = False
            try:
                # Indicate thinking state before every thing begins
                yield {"chunk": "🤔 思考中...", "messages": messages}

                async for response in self.runnable.astream(
                    {
                        "messages": input_message,  # NOTE：这里没有使用历史消息，只是用了当前输入
                    },
                    stream_mode="values",
                ):
                    last_response = response["messages"][-1]

                    if isinstance(last_response, AIMessage):
                        generated_code = ""
                        answer = last_response.content
                        if is_final_answer and answer:  # 提取最终答案
                            assistant_message = AIMessage(content=answer)
                            messages.append(assistant_message)
                            yield {"chunk": f"✅ {answer}", "messages": messages}
                            break

                        # 中间大量对话不放在历史记录里面
                        if answer:
                            yield {"chunk": answer, "messages": messages}
                            generated_code = extract_code(answer, strict=True)

                            # If there's code to execute, show execution status
                            if generated_code:
                                yield {"code": generated_code, "messages": messages}

                        elif last_response.tool_calls:
                            for tool_call in last_response.tool_calls:
                                if "code" in tool_call["args"]:
                                    generated_code = tool_call["args"]["code"]
                                    if generated_code:
                                        yield {"code": generated_code, "messages": messages}

                        if "# Final Answer is below:" in generated_code:
                            is_final_answer = True

                # Final state update
                yield {"messages": messages}

            except Exception as e:
                error_msg = f"❌ 生成回答时出错: {str(e)}"
                yield {"chunk": error_msg, "messages": messages}
            return

        # Terminal interface logic
        while True:
            try:
                generated_code = ""

                user_input, should_break, should_continue = await self._get_user_input(re_try, last_input)

                if should_break:
                    yield {"messages": messages}
                    break
                if should_continue:
                    continue

                context_code = f"""
## Context_Code
```python
{last_code}
```

MUST use the following information for your analysis:
```python
{config_dict}
```
"""

                input_message = HumanMessage(user_input + "\n" + context_code)

                # Store messages in a serializable format (dictionary instead of Message objects)
                messages.append(input_message)
                self.logger.info(f"User input: {user_input}")

                # 生成助手回答
                self.logger.info("\nHelper is thinking...")

                # Stream the response chunks
                # because the stream_mode="values", each chunk is the whole response
                is_final_answer = False  #  deepseek 不会自己停下来，所以需要一个标志位来判断是否已经输出最终答案
                async for response in self.runnable.astream(
                    {
                        "messages": input_message,
                    },
                    stream_mode="values",
                ):
                    # Print each chunk as it arrives
                    self.logger.debug(f"current chunk: {response}")

                    last_response = response["messages"][-1]

                    if isinstance(last_response, AIMessage):
                        if is_final_answer:
                            answer = last_response.content
                            self.logger.info(answer)
                            break

                        if last_response.content:
                            self.logger.info(f"last message: {last_response.content}")
                            generated_code = extract_code(last_response.content) or ""
                        elif last_response.tool_calls:
                            for tool_call in last_response.tool_calls:
                                if "code" in tool_call["args"]:
                                    generated_code = tool_call["args"]["code"]
                                    self.logger.info(f"last message: \n```python\n{generated_code}\n```")
                                break  # only one code now
                        else:
                            re_try = True

                        if "# Final Answer is below:" in generated_code:
                            is_final_answer = True

                ##############################################################################
                # Print newline after streaming completes
                print("\n")

                # Store assistant response in serializable format
                messages = response["messages"]

                # 产生更新后的状态
                yield {"messages": messages}

            except Exception as e:
                self.logger.error(f"\nError generating helper response: {e}")
                yield {"messages": messages}

    async def _get_user_input(self, re_try, last_input):
        """
        Get user input with retry handling.

        Args:
            re_try (bool): Whether to retry
            last_input (str): The previous user input for retry cases

        Returns:
            tuple[str, bool, bool]: (user_input, should_break, should_continue)
            - user_input is the user input
            - should_break is True if the user wants to quit
            - should_continue is True if the user wants to continue
        """

        retry_message = "There is no response from the helper, please try again."

        should_break = False
        should_continue = False
        if re_try:
            user_input = f"""
The user asks: {last_input}
However, {retry_message}
"""
            re_try = False
        else:
            # 获取用户输入
            self.logger.info("\nEnter your question (or 'q' to quit):")
            # 使用异步输入
            user_input = await self._async_input("User: ")
            user_input = user_input.strip()
            last_input = user_input

            if user_input.lower() == "q":
                self.logger.info("\nExiting helper mode...")
                should_break = True

            if not user_input:
                self.logger.info("\nNo input provided, please try again.")
                should_continue = True
        return user_input, should_break, should_continue

    async def _async_input(self, prompt: str) -> str:
        """
        异步获取用户输入。

        Args:
            prompt (str): 提示信息

        Returns:
            str: 用户输入
        """
        # 创建一个事件循环
        loop = asyncio.get_event_loop()
        # 在线程池中运行同步的 input 函数
        return await loop.run_in_executor(None, input, prompt)


if __name__ == "__main__":

    async def main():
        code_interpreter = setup_code_interpreter()

        last_code = "a = 123; b = 456"

        await code_interpreter.run(last_code)

        async for chunk in HelperNode(llm=None, graph_name="Baseline", code_interpreter=code_interpreter)(
            {"messages": [], "baseline_codes": [last_code]}, config={"configurable": {"from_web_ui": False}}
        ):
            print(f"chunk from helper node: {chunk}")

    asyncio.run(main())
