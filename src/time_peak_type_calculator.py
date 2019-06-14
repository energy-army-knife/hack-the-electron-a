import datetime

import pandas as pd

from src.data_loader import TariffPeriods


class TimePeakTypesCalculator:
    WINTER_HOUR_CHANGE_2016 = datetime.datetime(2016, 10, 30)
    WINTER_HOUR_CHANGE_2017 = datetime.datetime(2017, 10, 29)
    WINTER_HOUR_CHANGE_2018 = datetime.datetime(2018, 10, 28)

    SUMMER_HOUR_CHANGE_2016 = datetime.datetime(2016, 3, 27)
    SUMMER_HOUR_CHANGE_2017 = datetime.datetime(2017, 3, 26)
    SUMMER_HOUR_CHANGE_2018 = datetime.datetime(2018, 3, 25)

    SEASONS = {"Summer": [(SUMMER_HOUR_CHANGE_2016, WINTER_HOUR_CHANGE_2016 - datetime.timedelta(seconds=1)),
                          (SUMMER_HOUR_CHANGE_2017, WINTER_HOUR_CHANGE_2017 - datetime.timedelta(seconds=1)),
                          (SUMMER_HOUR_CHANGE_2018, WINTER_HOUR_CHANGE_2018 - datetime.timedelta(seconds=1))],
               "Winter": [(WINTER_HOUR_CHANGE_2016, SUMMER_HOUR_CHANGE_2017 - datetime.timedelta(seconds=1)),
                          (WINTER_HOUR_CHANGE_2017, SUMMER_HOUR_CHANGE_2018 - datetime.timedelta(seconds=1)),
                          (WINTER_HOUR_CHANGE_2018, datetime.datetime.now())]}

    def __init__(self, power: pd.DataFrame):
        self.power_data = power

    def get_power_spent(self, periods_peak_types: pd.DataFrame, take_into_account_season: bool) -> dict:

        power_spent_by_type = {}

        if take_into_account_season:
            for season in self.SEASONS:
                for season_period in self.SEASONS[season]:
                    season_tariff_hours = periods_peak_types[periods_peak_types["Season"] == season]
                    season_pw = self.power_data.loc[season_period[0]: season_period[1]]

                    if season_pw.shape[0] == 0:
                        continue

                    peaks_result = self._get_power_spent_by_type(season_pw, season_tariff_hours)

                    for peak_type in peaks_result:
                        if peak_type not in power_spent_by_type:
                            power_spent_by_type[peak_type] = 0
                        power_spent_by_type[peak_type] += peaks_result[peak_type]
            return power_spent_by_type
        else:
            return self._get_power_spent_by_type(self.power_data, periods_peak_types)

    @staticmethod
    def _get_power_spent_by_type(power_data: pd.DataFrame, times_peak_types: pd.DataFrame):
        power_spent_by_type = {}
        for index, period in times_peak_types.iterrows():
            power_spent_data = power_data.between_time(period[TariffPeriods.COLUMN_NAME_START_PERIOD],
                                                  period[TariffPeriods.COLUMN_NAME_END_PERIOD])
            if power_spent_data.shape[0] > 0:
                power_spent = power_spent_data.sum().values[0] / (4 * 1000)
                peak_type = period[TariffPeriods.COLUMN_NAME_TARIFF_TYPE]
                if peak_type not in power_spent_by_type:
                    power_spent_by_type[peak_type] = 0
                power_spent_by_type[peak_type] += power_spent

        return power_spent_by_type
