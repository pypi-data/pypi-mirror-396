import io
from pathlib import Path

from baicai_base.utils.data.loaders import load_data
from baicai_base.utils.data.types import DataDict


def preview_data(
    path: Path = None,
    target: str = None,
    classification: bool = True,
    brief: bool = True,
    ignored_features: list | None = None,
) -> DataDict:
    """
    Preview data for LLM to analyze.

    Args:
        path (Path): Path to the data source.
        target (str): Target column name.
        classification (bool): Whether the data is for classification or regression.
        simple (bool): Whether to return simple data info.

    Returns:
        DataDict: A dictionary containing data info and column names.
    """

    if ignored_features is None:
        ignored_features = []

    data = load_data(path=path)

    # if data is a fastai TabularDataLoaders
    if hasattr(data, "train"):
        data = data.items

    # Drop ignored features
    data = data.drop(columns=ignored_features)

    # Capture the output of data.info() into a string buffer
    buffer = io.StringIO()
    data.info(buf=buffer, memory_usage=False)
    info = buffer.getvalue()

    # Convert column names to a comma-separated string
    cols = ", ".join(data.columns)

    if brief:
        return {"data_info": info, "cols": cols, "data_size": data.shape[0]}

    data_info = [f"Data info:\n{info}"]

    # Append additional information for detailed preview
    data_info.append(f"Data stats:\n{data.describe()}")

    if classification:
        data_info.append(f"Data head:\n{data.head()}")
    else:
        data_info.append(f"Sorting by {target} (Descending):\n{data.sort_values(target, ascending=False).head()}")
        data_info.append(f"Sorting by {target} (Ascending):\n{data.sort_values(target, ascending=True).head()}")


    # 根据任务类型选择评估指标和模型
    avg_param = "weighted"
    class_counts = data[target].value_counts()
    if classification:
        if len(class_counts) == 2:
            avg_param = "binary"
            print("二分类问题，使用 binary 评估参数")
        else:
            avg_param = "weighted"
            print("多分类问题，使用 weighted 评估参数")

    return {
        "data_info": "\n\n".join(data_info),
        "cols": cols,
        "data_size": data.shape[0],
        "avg_param": avg_param,
        "class_counts": class_counts,
    }
