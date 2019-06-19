import pandas as pd

from electron_django import settings
from src.data_loader import TariffPeriods, TariffDataLoader, PowerDataLoader, MetersInformation
from src.data_models import TariffCost, TariffType, HourTariffType
from src.exceptions import TariffHoursException
from src.time_peak_type_calculator import TimePeakTypesCalculator


class Bill:
    def __init__(self, costs_per_day: float, times_peaks_distribution: dict, costs_peaks_distribution: dict):
        self.costs_per_day = costs_per_day
        self.times_peaks_distribution = times_peaks_distribution
        self.costs_peaks_distribution = costs_peaks_distribution

    def get_total(self) -> float:
        return sum(self.costs_peaks_distribution.values()) + self.costs_per_day

    def get_cost_without_days_cut(self):
        return sum(self.costs_peaks_distribution.values())


class BillingCalculator:

    def __init__(self, tariff_data_loader: TariffDataLoader, tariff_periods: TariffPeriods = None):

        self.tariff_data_loader = tariff_data_loader
        self.tariff_periods = tariff_periods
        self.time_peaks_calculator = TimePeakTypesCalculator()

    def compute_total_cost(self, power_data, contracted_power: float, tariff: TariffType) -> Bill:

        contract_costs = self.tariff_data_loader.get_tariff_by_contracted_tariff_type(contracted_power, tariff)

        cost_per_days = self.compute_cost_per_days(power_data, contract_costs)
        periods_peaks = self.tariff_periods.get_periods_for_tariff(tariff)
        take_into_account_season = tariff == TariffType.THREE_PERIOD
        times_peaks_distribution = self.time_peaks_calculator.get_power_spent(power_data, periods_peaks,
                                                                              take_into_account_season)
        costs_peaks_distribution = self.tariff_hours_compute(times_peaks_distribution, contract_costs)

        return Bill(cost_per_days, times_peaks_distribution, costs_peaks_distribution)

    @staticmethod
    def compute_cost_per_days(power_data: pd.DataFrame, tariff_cost: TariffCost):
        return ((power_data.index[-1] - power_data.index[0]).days + 1) * tariff_cost.power_cost_per_day

    @staticmethod
    def tariff_hours_compute(times_peaks_distribution: dict, tariff_costs: TariffCost) -> dict:

        times_peaks_costs = times_peaks_distribution.copy()

        for peak_name, power_spent in times_peaks_costs.items():

            if peak_name == HourTariffType.PEAK:
                times_peaks_costs[peak_name] = power_spent * tariff_costs.peak_periods_cost
            elif peak_name == HourTariffType.OFF_PEAK:
                times_peaks_costs[peak_name] = power_spent * tariff_costs.off_peak_periods
            elif peak_name == HourTariffType.SUPER_OFF_PEAK:
                times_peaks_costs[peak_name] = power_spent * tariff_costs.super_peak_cost
            else:
                raise TariffHoursException(
                    "The tariff slot type {0} does to exist".format(peak_name))
        return times_peaks_costs


if __name__ == '__main__':
    power_loader = PowerDataLoader(settings.RESOURCES + "/load_pwr.csv")

    tarriff_periods = TariffPeriods(settings.RESOURCES + "/HackTheElectron dataset support data/"
                                    "Tariff-Periods-Table 1.csv")

    tariff_data_load = TariffDataLoader(settings.RESOURCES + "/HackTheElectron dataset support data/"
                                        "Regulated Tarrifs-Table 1.csv")

    meter_info = MetersInformation(settings.RESOURCES + "/dataset_index.csv")

    meter_analyse = "meter_5"

    info_meter_0 = power_loader.get_power_meter_id(meter_analyse)
    meter_contract = meter_info.get_meter_id_contract_info(meter_analyse)
    meter_power_0 = power_loader.get_power_meter_id(meter_analyse)[0:1]

    billing_calculator = BillingCalculator(tariff_data_load, tarriff_periods)

    total_cost_simple = billing_calculator.compute_total_cost(meter_power_0, meter_contract.contracted_power,
                                                              TariffType.SIMPLE)
    total_two_cost = billing_calculator.compute_total_cost(meter_power_0, meter_contract.contracted_power,
                                                           TariffType.TWO_PERIOD)
    total_three_period = billing_calculator.compute_total_cost(meter_power_0, meter_contract.contracted_power,
                                                               TariffType.THREE_PERIOD)

    print("Simple Tariff")
    print("Payed: {0}".format(total_cost_simple.get_total()))

    print("Two Tariff")
    print("Payed: {0}".format(total_two_cost.get_total()))

    print("Three Period Tariff")
    print("Payed: {0}".format(total_three_period.get_total()))


