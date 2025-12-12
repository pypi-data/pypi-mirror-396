import pandas as pd


def time_series_data_split_condition(df, time_features, threshold_time):
    """
    根据时间阈值判断是否为训练数据

    Args:
        df: pandas DataFrame
        time_features: 字典，包含时间特征及其对应的列名
            {
                'year': 'year_col',
                'month': 'month_col',
                'day': 'day_col',
                'hour': 'hour_col',
                'minute': 'minute_col',
                'second': 'second_col'
            }
        threshold_time: 字典，包含阈值时间
            {
                'year': 2023,
                'month': 1,
                'day': 1,
                'hour': 0,
                'minute': 0,
                'second': 0
            }

    Returns:
        pandas Series: 如果小于阈值返回True，否则返回False
    """
    # 初始化条件为False
    cond = pd.Series(False, index=df.index)

    # 按时间粒度从大到小处理
    time_units = ["year", "month", "day", "hour", "minute", "second"]

    for unit in time_units:
        if unit in time_features and unit in threshold_time:
            col = time_features[unit]
            threshold = threshold_time[unit]

            if col in df.columns:
                # 如果当前单位的值大于阈值，则直接返回True
                # 如果等于阈值，则继续检查下一个单位
                # 如果小于阈值，则返回False
                cond = cond | (df[col] < threshold) | ((df[col] == threshold) & cond)
            else:
                # 如果该时间特征缺失，则跳过
                continue

    return cond
