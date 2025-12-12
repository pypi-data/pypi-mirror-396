import inspect
from typing import Union


def code_to_str(target: Union[type, callable], escape_braces: bool = True) -> str:
    """
    直接支持传递类/函数对象的代码提取工具

    Args:
        target: 类或函数对象
        escape_braces: 是否转义花括号（默认开启）
    Returns:
        str: 代码字符串

    功能：
    1. 接受类或函数对象作为参数
    2. 自动获取对象定义所在的模块
    3. 包含模块级别的导入语句
    4. 转义花括号（默认开启）

    使用示例：
    code_str = code_to_str(EfficientHFPipeline)
    """
    # 获取对象源代码
    try:
        source = inspect.getsource(target)
    except TypeError:
        raise ValueError("不支持的参数类型，请传入类或函数对象")

    # 获取定义模块的导入语句
    module = inspect.getmodule(target)
    if not module:
        return source

    imports = []
    module_source = inspect.getsource(module)
    for line in module_source.split("\n"):
        if line.startswith(("import ", "from ")):
            imports.append(line)

    # 组合结果
    combined = "\n".join(sorted(set(imports))) + "\n\n" + source

    # 花括号转义处理
    if escape_braces:
        combined = combined.replace("{", "{{").replace("}", "}}")

    return combined


if __name__ == "__main__":
    # 使用示例
    class ExampleClass:
        def __init__(self, name: str):
            self.name = name

        def method(self):
            return f"Hello, World, {self.name}!"

    def example_func():
        pass

    # 直接传递类对象
    print(code_to_str(ExampleClass))

    # 直接传递函数对象
    print(code_to_str(example_func))

    # 测试转义功能
    print(code_to_str(ExampleClass))  # 默认转义
    print(code_to_str(example_func, escape_braces=False))  # 关闭转义
