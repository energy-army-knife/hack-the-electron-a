from django.shortcuts import render

from electron_django import settings
from src.billing_calculator import BillingCalculator
from src.data_loader import MetersInformation, PowerDataLoader, TariffPeriods, TariffDataLoader
from src.data_models import HourTariffType
from src.data_utils import filter_power_by_date, to_string_tariff
from flask import json

from src.make_plots import plot_var
from src.recommend_contract import recommend_contract
from src.tariff_recommender import TariffRecommender

meters_info = MetersInformation(settings.RESOURCES + "/dataset_index.csv")
power_loader = PowerDataLoader(settings.RESOURCES + "/load_pwr.csv")
tarriff_periods = TariffPeriods(settings.RESOURCES + "/HackTheElectron dataset support data/Tariff-Periods-Table 1.csv")
tariff_data_load = TariffDataLoader(settings.RESOURCES + "/HackTheElectron dataset support data/"

                                                         "Regulated Tarrifs-Table 1.csv")

calculator = BillingCalculator(tariff_data_load, tarriff_periods)

MONTH_START_DEFAULT = "2016-10-01"
MONTH_END_DEFAULT = "2016-10-31"


def get_meter_id_from_query_parm(request):
    if "meter" not in request.GET:
        return "meter_0"
    else:
        return request.GET["meter"]


# Create your views here.
def index(request):
    meter = get_meter_id_from_query_parm(request)
    param = get_parameters_period_overview(meter, MONTH_START_DEFAULT, MONTH_END_DEFAULT)
    param["active_tab_dashboard"] = "class=active has-sub"
    return render(request, 'index.html', param)


def get_parameters_period_overview(meter_id, period_start, period_end):
    meter_info = meters_info.get_meter_id_contract_info(meter_id)
    power_loader_meter = filter_power_by_date(power_loader.get_power_meter_id(meter_id), period_start, period_end)

    df_power_loader_meter_hours_minuts = power_loader_meter.groupby(power_loader_meter.index.strftime('%H')).sum()
    power_loader_meter_hours_minuts = df_power_loader_meter_hours_minuts.values.flatten()

    bill = calculator.compute_total_cost(power_loader_meter, meter_info.contracted_power, meter_info.tariff)
    percentages_peak_type = {HourTariffType.PEAK: 0, HourTariffType.OFF_PEAK: 0, HourTariffType.SUPER_OFF_PEAK: 0}

    for peak_type in bill.costs_peaks_distribution:
        percentages_peak_type[peak_type] = round(
            bill.costs_peaks_distribution[peak_type] / sum(bill.costs_peaks_distribution.values()), 2)

    recommender_tariff = TariffRecommender(tariff_data_load, tarriff_periods)

    # Recommend the best tariff taken into account the two years info
    best_tariff, costs_tariffs = recommender_tariff.get_best_tariff(power_loader.get_power_meter_id(meter_id),
                                                                    meter_info.contracted_power)

    bill_total = calculator.compute_total_cost(power_loader.get_power_meter_id(meter_id), meter_info.contracted_power,
                                               meter_info.tariff)
    best_contracted_power = recommend_contract(power_loader.get_power_meter_id(meter_id))

    tariff_savings = 0
    if best_tariff != meter_info.tariff:
        tariff_savings = round(costs_tariffs[meter_info.tariff] - costs_tariffs[best_tariff], 2)

    bill_best_case = calculator.compute_total_cost(power_loader.get_power_meter_id(meter_id), best_contracted_power,
                                                   best_tariff)

    return {"contracted_power": meter_info.contracted_power,
            "bill": round(bill.get_total(), 2),
            "mean_load": round(power_loader_meter.mean().values[0] / 1000, 2),
            "peak_load": round(power_loader_meter.max().values[0] / 1000, 2),
            "meter_id": meter_id,
            "tariff": meter_info.tariff.value,
            "percentage_last_month_peak": percentages_peak_type[HourTariffType.PEAK],
            "percentage_last_month_off_peak": percentages_peak_type[HourTariffType.OFF_PEAK],
            "percentage_last_month_super_off_peak": percentages_peak_type[
                HourTariffType.SUPER_OFF_PEAK],
            "power_spent_by_hours": json.dumps(list(power_loader_meter_hours_minuts)),
            "power_spent_by_hours_label": json.dumps(list(range(0, 24))),
            "all_meters": meters_info.get_all_meters(),
            "period_start": period_start,
            "period_end": period_end,
            "best_tariff": to_string_tariff(best_tariff),
            "current_tariff": to_string_tariff(meter_info.tariff),
            "tariff_savings": round(bill_total.get_total() - bill_best_case.get_total(), 2),
            "best_contracted_power": best_contracted_power}


def analyser(request):
    if request.method == "GET":

        meter = get_meter_id_from_query_parm(request)
        param = get_parameters_period_overview(meter, MONTH_START_DEFAULT, MONTH_END_DEFAULT)
        param["active_tab_analyser"] = "class=active has-sub"

    else:

        param = get_parameters_period_overview(request.POST["meter_id"], request.POST["date-start"],
                                               request.POST["date-end"])
        param["active_tab_analyser"] = "class=active has-sub"

    return render(request, "tariff_analyser.html", param)


def pv(request):
    meter_id = get_meter_id_from_query_parm(request)
    return render(request, "pv.html", {"active_tab_photovoltaic": "class=active has-sub",
                                       "all_meters": meters_info.get_all_meters(),
                                       "meter_id": meter_id})


def device_simulator(request):
    meter_id = get_meter_id_from_query_parm(request)
    return render(request, "device_simulator.html", {"active_tab_device_simulator": "class=active has-sub",
                                                     "all_meters": meters_info.get_all_meters(),
                                                     "meter_id": meter_id})


def contract_subscription(request):
    meter_id = get_meter_id_from_query_parm(request)
    meter_power = power_loader.get_power_meter_id(meter_id)
    meter_info = meters_info.get_meter_id_contract_info(meter_id)
    kW = 1000

    percentil_no_adjustment = 100
    percentil_small_adjustment = 99.99
    percentil_some_adjustments = 99.95

    best_contracted_power = round(recommend_contract(power_loader.get_power_meter_id(meter_id),
                                                     percentile=percentil_no_adjustment), 2)
    contracted_power_perc_small = round(recommend_contract(power_loader.get_power_meter_id(meter_id),
                                                           percentile=percentil_small_adjustment), 2)
    contracted_power_perc_some = round(recommend_contract(power_loader.get_power_meter_id(meter_id),
                                                          percentile=percentil_some_adjustments), 2)

    current_price = calculator.compute_total_cost(meter_power, meter_info.contracted_power,
                                                  meter_info.tariff).get_total()
    saving_no_adj = round(current_price - calculator.compute_total_cost(meter_power, best_contracted_power,
                                                                        meter_info.tariff).get_total(), 2)

    saving_small_adj = round(current_price-calculator.compute_total_cost(meter_power, contracted_power_perc_small,
                                                                         meter_info.tariff).get_total(), 2)

    saving_some_adj = round(current_price-calculator.compute_total_cost(meter_power, contracted_power_perc_some,
                                                                        meter_info.tariff).get_total(), 2)

    result = plot_var(meter_power, runtime=1, threshold=[a*kW for a in [meter_info.contracted_power,
                                                         best_contracted_power,
                                                         contracted_power_perc_small,
                                                         contracted_power_perc_some]])

    return render(request, "contract_subscription.html", {"active_contract_subscription": "class=active has-sub",
                                                          "no_adjustment_price": saving_no_adj,
                                                          "small_adjustment_price": saving_small_adj,
                                                          "medium_adjustment_price": saving_some_adj,
                                                          "percentil_small_adjustment": round(
                                                              100 - percentil_small_adjustment, 3),
                                                          "percentil_some_adjustments": round(
                                                              100 - percentil_some_adjustments, 2),
                                                          "all_meters": meters_info.get_all_meters(),
                                                          "meter_id": meter_id,
                                                          "result": result
                                                          })


def notifications(request):
    return render(request, 'notifications.html')
