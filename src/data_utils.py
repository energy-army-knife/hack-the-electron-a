import pandas as pd

from src.data_models import TariffType


def to_string_tariff(tariff: TariffType):
    if tariff == TariffType.SIMPLE:
        return "Simples"
    elif tariff == TariffType.TWO_PERIOD:
        return "Two Period"
    elif tariff == TariffType.THREE_PERIOD:
        return "Three Period"


def filter_power_by_date(power_data: pd.DataFrame, start_datetime: str = None, end_datetime: str = None) -> pd.DataFrame:
    if start_datetime and end_datetime is None:
        return power_data

    elif start_datetime is None:
        return power_data.loc[:end_datetime]

    elif end_datetime is None:
        return power_data.loc[start_datetime:]
    else:
        return power_data.loc[start_datetime:end_datetime]