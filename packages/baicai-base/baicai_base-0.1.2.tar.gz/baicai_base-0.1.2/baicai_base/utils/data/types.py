from typing import TypedDict


class DataDict(TypedDict):
    """Dictionary containing data information for preview."""

    data_info: str
    cols: str
    data_size: int
