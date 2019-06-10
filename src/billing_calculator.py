import pandas as pd
import datetime

from src.data_loader import TariffPeriods, TariffDataLoader, PowerDataLoader, MetersInformation
from src.data_models import MeterContractInformation, TariffCost, TariffType, HourTariffType
from src.exceptions import TariffHoursException


class BillingCalculator:

    WINTER_HOUR_CHANGE_2016 = datetime.datetime(2016, 10, 30)
    WINTER_HOUR_CHANGE_2017 = datetime.datetime(2017, 10, 29)
    WINTER_HOUR_CHANGE_2018 = datetime.datetime(2018, 10, 28)

    SUMMER_HOUR_CHANGE_2016 = datetime.datetime(2016, 3, 27)
    SUMMER_HOUR_CHANGE_2017 = datetime.datetime(2017, 3, 26)
    SUMMER_HOUR_CHANGE_2018 = datetime.datetime(2018, 3, 25)

    SEASONS = {"Summer": [(SUMMER_HOUR_CHANGE_2016, WINTER_HOUR_CHANGE_2016),
                          (SUMMER_HOUR_CHANGE_2017, WINTER_HOUR_CHANGE_2017),
                          (SUMMER_HOUR_CHANGE_2018, WINTER_HOUR_CHANGE_2018)],
               "Winter": [(WINTER_HOUR_CHANGE_2016, SUMMER_HOUR_CHANGE_2017),
                          (WINTER_HOUR_CHANGE_2017, SUMMER_HOUR_CHANGE_2018),
                          (WINTER_HOUR_CHANGE_2018, datetime.datetime.now())]}

    def __init__(self, meter_contract_info: MeterContractInformation, power: pd.DataFrame,
                 tariff_data_loader: TariffDataLoader, tariff_periods: TariffPeriods = None):
        self.meter_contract_info = meter_contract_info
        self.power = power
        self.tariff_data_loader = tariff_data_loader
        self.tariff_periods = tariff_periods

    @staticmethod
    def filter_by_date(power_data: pd.DataFrame, start_datetime: str = None, end_datetime: str = None):

        if start_datetime and end_datetime is None:
            return power_data

        elif start_datetime is None:
            return power_data.loc[:end_datetime]

        elif end_datetime is None:
            return power_data.loc[start_datetime:]
        else:
            return power_data.loc[start_datetime:end_datetime]

    def simple_tariff(self, start_date: str = None, end_date: str = None) -> float:

        power_data = self.filter_by_date(self.power, start_date, end_date)

        tariff_costs = self.tariff_data_loader.get_tariff_by_contracted_tariff_type(
            self.meter_contract_info.contracted_power, TariffType.SIMPLE)

        return power_data.sum() * tariff_costs.peak_periods_cost / (4 * 1000)

    def two_periods_tariff(self, start_date: str = None, end_date: str = None) -> float:

        power_data = self.filter_by_date(self.power, start_date, end_date)

        tariff_costs = self.tariff_data_loader.get_tariff_by_contracted_tariff_type(meter_contract.contracted_power,
                                                                                    TariffType.TWO_PERIOD)

        tariff_two_periods = tarriff_periods.get_periods_for_tariff(TariffType.TWO_PERIOD)
        return self.tariff_hours_compute(power_data, tariff_two_periods, tariff_costs)

    def three_period_tariff(self, start_date: str = None, end_date: str = None) -> float:

        power_data = self.filter_by_date(self.power, start_date, end_date)

        tariff_cost = self.tariff_data_loader.get_tariff_by_contracted_tariff_type(
            self.meter_contract_info.contracted_power, TariffType.THREE_PERIOD)

        tariff_hours_three = self.tariff_periods.get_periods_for_tariff(TariffType.THREE_PERIOD)

        winter_cost = self.compute_cost_by_season(power_data, "Winter", tariff_hours_three, tariff_cost)
        summer_cost = self.compute_cost_by_season(power_data, "Summer", tariff_hours_three, tariff_cost)
        return winter_cost + summer_cost

    def compute_cost_by_season(self, power_data: pd.DataFrame, season: str, tariff_hours: pd.DataFrame,
                               tariff_cost: TariffCost) -> float:
        season_tariff_hours = tariff_hours[tariff_hours["Season"] == season]

        total_season_cost = 0
        for season_period in self.SEASONS[season]:
            season_pw = power_data.loc[season_period[0]: season_period[1]]
            total_season_cost += self.tariff_hours_compute(season_pw, season_tariff_hours, tariff_cost)

        return total_season_cost

    @staticmethod
    def tariff_hours_compute(meter_power: pd.DataFrame, tarrif_hours: pd.DataFrame, tariff_costs: TariffCost):
        cost = 0

        for index, period in tarrif_hours.iterrows():
            power_spent = meter_power.between_time(period[TariffPeriods.COLUMN_NAME_START_PERIOD],
                                                   period[TariffPeriods.COLUMN_NAME_END_PERIOD]).sum() / (4 * 1000)

            if period[TariffPeriods.COLUMN_NAME_TARIFF_TYPE] == HourTariffType.PEAK:
                cost += power_spent * tariff_costs.peak_periods_cost
            elif period[TariffPeriods.COLUMN_NAME_TARIFF_TYPE] == HourTariffType.OFF_PEAK:
                cost += power_spent * tariff_costs.off_peak_periods
            elif period[TariffPeriods.COLUMN_NAME_TARIFF_TYPE] == HourTariffType.SUPER_OFF_PEAK:
                cost += power_spent * tariff_costs.super_peak_cost
            else:
                raise TariffHoursException("The tariff slot type {0} does to exist".format(period[TariffPeriods.COLUMN_NAME_TARIFF_TYPE]))
        return cost


if __name__ == '__main__':
    power_loader = PowerDataLoader("../resources/load_pwr.csv")

    tarriff_periods = TariffPeriods("../resources/HackTheElectron dataset support data/"
                                    "Tariff-Periods-Table 1.csv")

    tariff_data_load = TariffDataLoader("../resources/HackTheElectron dataset support data/"
                                        "Regulated Tarrifs-Table 1.csv")

    meter_info = MetersInformation("../resources/dataset_index.csv")

    meter_analyse = "meter_5"

    info_meter_0 = power_loader.get_power_meter_id(meter_analyse)
    meter_contract = meter_info.get_meter_id_contract_info(meter_analyse)
    meter_power_0 = power_loader.get_power_meter_id(meter_analyse)

    billing_calculator = BillingCalculator(meter_contract, meter_power_0, tariff_data_load,
                                           tarriff_periods)

    total_cost_simple = billing_calculator.simple_tariff("2017-01-01", "2017-01-02")
    total_two_cost = billing_calculator.two_periods_tariff("2017-01-01", "2017-01-02")
    total_three_period = billing_calculator.three_period_tariff("2017-01-01", "2017-01-02")

    print("Simple Tariff")
    print("Payed: {0}".format(total_cost_simple))

    print("Two Tariff")
    print("Payed: {0}".format(total_two_cost))

    print("Three Period Tariff")
    print("Payed: {0}".format(total_three_period))

