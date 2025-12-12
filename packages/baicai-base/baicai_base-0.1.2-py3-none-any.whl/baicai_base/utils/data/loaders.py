import sqlite3
from pathlib import Path

import pandas as pd


def load_data(path=None, **kwargs):
    """
    Load data from various data sources.

    Args:
        path (str): Path to the data source.
        name (str): Name of the example data. if name is not None, path will be ignored.
    """

    path = Path(path)

    file_extension = path.suffix.lower().strip(".")

    # Mapping of file extensions to their corresponding pandas functions
    file_readers = {
        "csv": lambda path, **kw: pd.read_csv(path, delimiter=kw.pop("delimiter", ","), low_memory=False, **kw),
        "xls": pd.read_excel,
        "xlsx": pd.read_excel,
        "json": pd.read_json,
        "html": lambda path, **kw: pd.read_html(path, **kw)[0],
        "pkl": pd.read_pickle,
        "txt": lambda path, **kw: pd.read_csv(path, delimiter=kw.pop("delimiter", "\t"), **kw),
        "xml": pd.read_xml,
    }

    if file_extension in file_readers:
        return file_readers[file_extension](path, **kwargs)
    elif file_extension == "db":
        conn = sqlite3.connect(path)
        query = kwargs.pop("query", "SELECT * FROM table_name")
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")
