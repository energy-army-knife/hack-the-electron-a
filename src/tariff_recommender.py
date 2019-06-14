from src.billing_calculator import BillingCalculator
from src.data_loader import PowerDataLoader, TariffPeriods, TariffDataLoader, MetersInformation
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from src.data_models import TariffType

power_loader = PowerDataLoader("../resources/load_pwr.csv")

tarriff_periods = TariffPeriods("../resources/HackTheElectron dataset support data/"
                                "Tariff-Periods-Table 1.csv")

tariff_data_load = TariffDataLoader("../resources/HackTheElectron dataset support data/"
                                    "Regulated Tarrifs-Table 1.csv")

meter_analyse = "meter_2"

meter_info = MetersInformation("../resources/dataset_index.csv").get_meter_id_contract_info(meter_analyse)

meter_0_power = power_loader.get_power_meter_id(meter_analyse)

months = [g for n, g in meter_0_power.groupby(pd.TimeGrouper('M'))]

result = {}

# data to plot
n_groups = 5

# create plot
fig, ax = plt.subplots()
index = np.arange(n_groups)
bar_width = 0.14
opacity = 0.8

color = ["b", "g", "r"]
legend = ["Simple", "Two-Period", "Three-Period"]

for i, tariff in enumerate([TariffType.SIMPLE, TariffType.TWO_PERIOD, TariffType.THREE_PERIOD]):

    result[tariff] = [BillingCalculator(el, tariff_data_load,
                                        tarriff_periods).compute_total_cost(meter_info.contracted_power,
                                                                            tariff).get_value() for el in months]

    rects1 = plt.bar(index + bar_width*i, result[tariff][0:n_groups], bar_width,
                     alpha=opacity,
                     color=color[i],
                     label=legend[i])
legend = []
for month in months[0:n_groups]:
    legend.append(month.index[1].strftime("%B-%Y"))

plt.xlabel('Month')
plt.ylabel('Cost')
plt.title('Cost by Month')
plt.xticks(index + bar_width, legend)
plt.legend()

plt.tight_layout()
plt.show()
