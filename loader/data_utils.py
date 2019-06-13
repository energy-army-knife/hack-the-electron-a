import pandas as pd


def filter_power_by_date(power_data: pd.DataFrame, start_datetime: str = None, end_datetime: str = None):
    if start_datetime and end_datetime is None:
        return power_data

    elif start_datetime is None:
        return power_data.loc[:end_datetime]

    elif end_datetime is None:
        return power_data.loc[start_datetime:]
    else:
        return power_data.loc[start_datetime:end_datetime]