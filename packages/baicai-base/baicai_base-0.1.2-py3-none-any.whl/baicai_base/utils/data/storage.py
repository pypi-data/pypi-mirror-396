import os
import time
from pathlib import Path

from baicai_base.utils.data.constants import TMP_FOLDER_TYPES


def get_tmp_folder(type: str = "data") -> Path:
    """
    Get the path of the tmp folder.

    Args:
        type (str): The type of the tmp folder. "data" for data, "model" for models, "log" for logs.
    """
    if type not in TMP_FOLDER_TYPES:
        raise ValueError(f"Unsupported type: {type}. Supported types are: {', '.join(TMP_FOLDER_TYPES.keys())}")

    # Use BAICAI_HOME if set, otherwise use home directory
    base_path = Path(os.environ.get("BAICAI_HOME", str(Path.home())))
    return base_path / ".baicai" / "tmp" / TMP_FOLDER_TYPES[type]


def clear_tmp_files(type: str = "data", days: int = 7):
    """
    Clear the tmp files.

    Args:
        type (str): The type of the tmp files. "data" for data, "model" for models, "log" for logs.
        days (int): The number of days to keep the tmp files.
    """
    tmp_folder = get_tmp_folder(type)
    if type == "user_info":
        for file in tmp_folder.glob("*"):
            file.unlink()
    else:
        for file in tmp_folder.glob("*"):
            if file.stat().st_mtime < time.time() - days * 86400:
                file.unlink()


def clear_all_tmp_files(days: int = 7):
    """
    Clear all tmp files.

    Args:
        days (int): The number of days to keep the tmp files.
    """
    folder_types = TMP_FOLDER_TYPES.copy()
    for folder_type in folder_types:
        clear_tmp_files(folder_type, days)


def get_saved_pickle_path(
    folder: Path | None = None, name: str | None = None, file_prefix: str | None = None, type: str = "data"
) -> Path:
    """
    Get the path of the saved pickle file.

    Args:
        folder (Path): The folder of the pickle file.
        name (str): The folder name of the pickle file.
        file_prefix (str): The prefix of the pickled model. The file name will be {file_prefix}_{timestamp}.pkl
    Returns:
        Path: The path of the pickle file.
    """
    if folder is None:
        folder = get_tmp_folder(type) / name.lower()

    if file_prefix is None:
        files = list(folder.glob("*.pkl"))
    else:
        files = list(folder.glob(f"{file_prefix}_*.pkl"))

    if not files:
        raise FileNotFoundError(
            f"No pickle files found in {folder}/{name}" + (f" with prefix '{file_prefix}'" if file_prefix else "")
        )

    return max(files)


def get_saved_user_info_path() -> Path:
    """
    Get the path of the survey and analysis result files.
    """
    folder = get_tmp_folder("user_info")
    return folder / "survey.json", folder / "profile.json"


def get_saved_question_path(question_sheet_id: str) -> Path:
    """
    Get the path of the saved question file.
    """
    folder = get_tmp_folder("question")
    return folder / f"{question_sheet_id}.json"


def get_saved_students_path(question_sheet_id: str) -> Path:
    """
    Get the path of the saved students file.
    """
    folder = get_tmp_folder("user_info")
    return folder / f"{question_sheet_id}.json"
