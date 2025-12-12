# Borrowed from vision-agent
import json
import logging
import re
from typing import Any, Dict, List, Tuple

from json_repair import repair_json

from baicai_base.utils.constants import JSON_FORMAT_ERROR, JSON_RETRY_TOO_MANY, RETRY_JSON

logger = logging.getLogger(__name__)


def _preprocess_latex(json_str: str) -> str:
    """
    Preprocess LaTeX expressions in the JSON string by escaping backslashes.
    Handles both inline ($...$) and display ($$...$$) LaTeX expressions.
    """
    # Find all LaTeX expressions (both inline and display)
    latex_pattern = r"\$\$.*?\$\$|\$.*?\$"
    matches = list(re.finditer(latex_pattern, json_str))

    # Process matches in reverse order to avoid overlapping replacements
    result = json_str
    for match in reversed(matches):
        latex_expr = match.group()
        # Only replace single backslashes, not already escaped ones
        escaped_expr = re.sub(r"(?<!\\)\\(?!\\)", r"\\\\", latex_expr)
        result = result[: match.start()] + escaped_expr + result[match.end() :]

    return result


def extract_json(
    json_str: str, strict: bool = False, raise_error: bool = True, start_tag: str = "```json", end_tag: str = "```"
) -> Dict[str, Any]:
    """
    Extract the JSON from the given string.
    """
    try:
        # Preprocess LaTeX expressions before parsing
        json_str = _preprocess_latex(json_str)
        extracted_json = json.loads(json_str)
    except json.JSONDecodeError as e:
        if start_tag in json_str:
            json_str = json_str[json_str.find(start_tag) + len(start_tag) :].strip()
            json_str = json_str[: json_str.find(end_tag)].strip()
        elif not strict:
            if "```" in json_str:
                json_str = json_str[json_str.find("```") + len("```") :].strip()
                json_str = json_str[: json_str.find("```")].strip()
            elif "{" in json_str and "}" in json_str:
                start_index = json_str.find("{")
                end_index = json_str.rfind("}")
                if end_index != -1:
                    json_str = json_str[start_index : end_index + 1].strip()
                else:
                    json_str = json_str[start_index:].strip()

        # Preprocess LaTeX expressions before parsing
        json_str = _preprocess_latex(json_str)
        extracted_json = repair_json(json_str, return_objects=True)
        if extracted_json == "":  # Handle empty string return from json_repair
            if raise_error:
                raise ValueError(f"Could not extract JSON from the given str: \n{json_str}") from e
            return {}

    # Only handle top-level lists
    if isinstance(extracted_json, list):
        # Remove empty string items
        extracted_json = [item for item in extracted_json if item != ""]
        # If list has only one item, use that item directly
        if len(extracted_json) == 1:
            extracted_json = extracted_json[0]
        if len(extracted_json) == 0:
            extracted_json = {}

    return extracted_json


def safe_extract_json(
    runnable, invoke_kwargs: dict, max_iter: int = 3, start_tag: str = "```json", end_tag: str = "```"
) -> Tuple[Any, Dict[str, Any], List[Tuple[str, str]], bool]:
    """
    Extract the JSON from the given string with max_iter retries.

    Args:
        runnable: The runnable to invoke.
        invoke_kwargs: The kwargs to invoke the runnable.
        max_iter: The maximum number of retries.
        start_tag: The start tag of the JSON.
        end_tag: The end tag of the JSON.
    Returns:
        Tuple containing:
        - The original solution by LLM
        - The extracted JSON dictionary
        - The reflections list
        - A boolean indicating if the extraction failed
    """
    reflections = []
    i = 0
    while True:
        if i > max_iter:
            logger.error(JSON_RETRY_TOO_MANY)
            return None, None, reflections, True
        i += 1

        try:
            logger.debug(f"Attempt {i}: Invoking runnable with kwargs: {invoke_kwargs}")
            solution = runnable.invoke(invoke_kwargs)
            logger.debug(f"Solution received: {solution}")

            if isinstance(solution, dict) and "messages" in solution:
                solution = solution["messages"][-1]
                logger.debug(f"Extracted message from solution: {solution}")

            if not hasattr(solution, "content"):
                logger.error(f"Solution does not have content attribute: {solution}")
                raise ValueError("Solution must have a content attribute")

            try:
                json_dict = extract_json(solution.content, start_tag=start_tag, end_tag=end_tag)
                if json_dict:  # Only return if we got a valid JSON
                    logger.debug(f"Successfully extracted JSON: {json_dict}")
                    return solution, json_dict, reflections, False
                else:
                    raise ValueError("Empty JSON result")
            except ValueError:
                # If JSON extraction fails, continue to next iteration
                logger.error(f"Error extracting JSON from content: {solution.content}")
                logger.info(JSON_FORMAT_ERROR)
                reflections = [("user", RETRY_JSON)]
                # Add reflection to the "message" key in invoke_kwargs
                if "message" in invoke_kwargs:
                    invoke_kwargs["message"] += reflections
                else:
                    invoke_kwargs["message"] = reflections
                continue

        except Exception as e:
            logger.error(f"Error extracting JSON: {e}")
            logger.info(JSON_FORMAT_ERROR)

            reflections = [("user", RETRY_JSON)]
            # Add reflection to the "message" key in invoke_kwargs
            if "message" in invoke_kwargs:
                invoke_kwargs["message"] += reflections
            else:
                invoke_kwargs["message"] = reflections


def extract_code(code: str, strict: bool = False) -> str:
    """
    Extract the code from the given string.
    """
    if "\n```python" in code:
        start = "\n```python"
    elif "```python" in code:
        start = "```python"
    else:
        if not strict:
            return code
        else:
            return ""

    code = code[code.find(start) + len(start) :]
    code = code[: code.find("```")]
    if code.startswith("python\n"):
        code = code[len("python\n") :]
    return code
