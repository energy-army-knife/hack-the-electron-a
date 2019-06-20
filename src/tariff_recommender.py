import base64
from io import BytesIO

from electron_django import settings
from src.billing_calculator import BillingCalculator
from src.data_loader import PowerDataLoader, TariffPeriods, TariffDataLoader, MetersInformation
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from src.data_models import TariffType


class TariffRecommender:

    TARIFFS = [TariffType.SIMPLE, TariffType.TWO_PERIOD, TariffType.THREE_PERIOD]

    def __init__(self, tariff_data_load: TariffDataLoader, tarriff_periods: TariffPeriods):
        self.tariff_data_load = tariff_data_load
        self.tarriff_periods = tarriff_periods
        self.bill_calculator = BillingCalculator(self.tariff_data_load, self.tarriff_periods)

    def get_best_tariff(self, power_data: pd.DataFrame, contracted_power: float) -> (TariffType, dict):
        costs_tariffs = self.get_costs_by_tariff(power_data, contracted_power)
        best_tariff = min(costs_tariffs, key=costs_tariffs.get)
        return best_tariff, costs_tariffs

    def get_costs_by_tariff(self, power_data: pd.DataFrame, contracted_power: float) -> dict:

        costs_tariff = {}
        for i, tariff in enumerate(self.TARIFFS):
            costs_tariff[tariff] = self.bill_calculator.compute_total_cost(power_data, contracted_power,
                                                                           tariff).get_total()

        return costs_tariff

    def get_tariff_billing_by_months(self, power_data: pd.DataFrame, contracted_power: float) -> dict:
        months = [g for n, g in power_data.groupby(pd.TimeGrouper('M'))]
        name_months = [month.index[0].strftime("%B-%Y") for month in months]

        months_billing = {}
        for i, month in enumerate(months):
            months_billing[name_months[i]] = {}
            for j, tariff in enumerate(self.TARIFFS):
                bill = self.bill_calculator.compute_total_cost(month, contracted_power, tariff).get_total()
                months_billing[name_months[i]][tariff] = bill

        return months_billing

    def plot_tariffs_by_month(self, meter_power: pd.DataFrame, contracted_power: float, extension='png'):

        months_billing_by_tariff = self.get_tariff_billing_by_months(meter_power, contracted_power)

        # data to plot
        n_groups = 25
        bar_width = 0.14
        opacity = 0.8

        color = ["b", "g", "r"]
        legend = ["Simple", "Two-Period", "Three-Period"]

        # create plot
        fig = plt.figure(figsize=(15, 10))
        index = np.arange(n_groups)

        for i, tariff in enumerate([TariffType.SIMPLE, TariffType.TWO_PERIOD, TariffType.THREE_PERIOD]):
            tariff_values = [months_billing_by_tariff[el][tariff] for el in months_billing_by_tariff]

            rects1 = plt.bar(index + bar_width * i, tariff_values, bar_width,
                             alpha=opacity,
                             color=color[i],
                             label=legend[i])

        legend = list(months_billing_by_tariff.keys())

        plt.xlabel('Month')
        plt.ylabel('Cost')
        plt.title('Cost by Month')
        plt.xticks(index + bar_width, legend)
        plt.legend()

        plt.tight_layout()

        buf = BytesIO()
        fig.savefig(buf, format=extension, bbox_inches='tight')
        plt.close()
        image_string = base64.b64encode(buf.getvalue()).decode('ascii')
        return image_string


if __name__ == '__main__':

    power_loader = PowerDataLoader(settings.RESOURCES + "/load_pwr.csv")

    tarriff_periods = TariffPeriods(settings.RESOURCES + "/HackTheElectron dataset support data/"
                                    "Tariff-Periods-Table 1.csv")

    tariff_data_load = TariffDataLoader(settings.RESOURCES + "/HackTheElectron dataset support data/"
                                        "Regulated Tarrifs-Table 1.csv")

    tariff_recommender = TariffRecommender(tariff_data_load, tarriff_periods)
    meters_info = MetersInformation(settings.RESOURCES + "/dataset_index.csv")

    meters = meters_info.get_all_meters()

    meter_analyse = "meter_64"
    meter_info = meters_info.get_meter_id_contract_info(meter_analyse)
    meter_power = power_loader.get_power_meter_id(meter_analyse)

    best_tariff, costs_tariff = tariff_recommender.get_best_tariff(meter_power, meter_info.contracted_power)
    if best_tariff != meter_info.tariff:
        print("The best tariff is {0} and not {1}. You should save: {2}.".format(best_tariff, meter_info.tariff,
                                                                                 costs_tariff[meter_info.tariff]-
                                                                                 costs_tariff[best_tariff]))

    tariff_recommender.plot_tariffs_by_month(meter_power)
