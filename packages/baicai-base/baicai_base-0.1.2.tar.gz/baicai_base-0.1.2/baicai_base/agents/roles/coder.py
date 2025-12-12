from langchain_core.prompts import ChatPromptTemplate

from baicai_base.services import LLM

CODER = """
# Role
You are an expert assistant who can solve any task using code blobs. You will be given a task to solve as best you can.

## Input
You are given a task to code a function and call the function.

## Output
You should output the python code.
```python
[Your code here]
```
"""


def coder(llm=None):
    llm = llm or LLM().llm
    action_maker_template = ChatPromptTemplate.from_messages(
        [
            ("system", CODER),
            ("placeholder", "{messages}"),
        ]
    )
    return action_maker_template | llm


if __name__ == "__main__":
    action_maker_result_house = coder().invoke(
        {"messages": [("user", "code a simple function to calculate the sum of two numbers")]}
    )

    print(action_maker_result_house.content)
