import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from electron_django import settings
from src.billing_calculator import BillingCalculator
from src.data_loader import MetersInformation, PowerDataLoader, TariffPeriods, TariffDataLoader, CSVDataLoader
from src.data_models import HourTariffType, TariffType
from src.data_utils import filter_power_by_date, to_string_tariff

from src.make_plots import plot_var
from src.recommend_contract import recommend_contract
from src.tariff_recommender import TariffRecommender

###
import pandas as pd
appliances_data = pd.read_csv('resources/appliances_1month_15m.csv').drop(['Unnamed: 0'],axis=1)
###

meters_info = MetersInformation(settings.RESOURCES + "/dataset_index.csv")
power_loader = PowerDataLoader(settings.RESOURCES + "/load_pwr.csv")
tarriff_periods = TariffPeriods(settings.RESOURCES + "/HackTheElectron dataset support data/Tariff-Periods-Table 1.csv")
tariff_data_load = TariffDataLoader(settings.RESOURCES + "/HackTheElectron dataset support data/"

                                                         "Regulated Tarrifs-Table 1.csv")

pv_power = CSVDataLoader(settings.RESOURCES + "/pv_pwr.csv", parse_dates=['Date']).data_frame.set_index('Date')

calculator = BillingCalculator(tariff_data_load, tarriff_periods)
recommender_tariff = TariffRecommender(tariff_data_load, tarriff_periods)

TODAY = datetime.datetime(2018, 9, 15)
START_MONTH = TODAY.replace(day=1)

PREVIOUS_MONTH_END = START_MONTH - datetime.timedelta(days=1)
PREVIOUS_MONTH_START = PREVIOUS_MONTH_END.replace(day=1)


def get_meter_id_from_query_parm(request):
    if "meter" not in request.GET:
        return "meter_0"
    else:
        return request.GET["meter"]

######
def get_appliance_id_from_query_parm(request):
    if "appliance" not in request.GET:
        return "fridge_freezer"
    else:
        return request.GET["appliance"]
######

def get_name_tariff(tariff: TariffType):
    if tariff == TariffType.SIMPLE:
        return "Simple"
    elif tariff == TariffType.TWO_PERIOD:
        return "Two-Periods"
    elif tariff == TariffType.THREE_PERIOD:
        return "Three-Period"



def get_parameters_period_overview(meter_id, period_start, period_end):
    meter_info = meters_info.get_meter_id_contract_info(meter_id)
    power_loader_meter = filter_power_by_date(power_loader.get_power_meter_id(meter_id), period_start, period_end)

    df_power_loader_meter_hours_minuts_sum = power_loader_meter.groupby(power_loader_meter.index.strftime('%H')).sum()
    power_loader_meter_hours_minuts_sum = df_power_loader_meter_hours_minuts_sum.values.flatten()

    df_power_loader_meter_hours_max = power_loader_meter.groupby(power_loader_meter.index.strftime('%H')).max()
    power_loader_meter_hours_max = df_power_loader_meter_hours_max.values.flatten()

    bill = calculator.compute_total_cost(power_loader_meter, meter_info.contracted_power, meter_info.tariff)
    percentages_peak_type_hours = {HourTariffType.PEAK: 0, HourTariffType.OFF_PEAK: 0, HourTariffType.SUPER_OFF_PEAK: 0}
    percentages_peak_type_spent = {HourTariffType.PEAK: 0, HourTariffType.OFF_PEAK: 0, HourTariffType.SUPER_OFF_PEAK: 0}

    for peak_type in bill.times_peaks_distribution:
        percentages_peak_type_hours[peak_type] = round(
            bill.times_peaks_distribution[peak_type] / sum(bill.times_peaks_distribution.values()), 2)
        percentages_peak_type_spent[peak_type] = round(
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
            "percentage_last_month_peak": percentages_peak_type_hours[HourTariffType.PEAK],
            "percentage_last_month_off_peak": percentages_peak_type_hours[HourTariffType.OFF_PEAK],
            "percentage_last_month_super_off_peak": percentages_peak_type_hours[
                HourTariffType.SUPER_OFF_PEAK],
            "percentage_last_month_peak_cost": percentages_peak_type_spent[HourTariffType.PEAK],
            "percentage_last_month_off_peak_cost": percentages_peak_type_spent[HourTariffType.OFF_PEAK],
            "percentage_last_month_super_off_peak_cost": percentages_peak_type_spent[
                HourTariffType.SUPER_OFF_PEAK],
            "power_loader_meter_hours_max": list(power_loader_meter_hours_max / 1000),
            "power_spent_by_hours": list(power_loader_meter_hours_minuts_sum / 1000),
            "power_spent_by_hours_label": list(range(0, 24)),
            "all_meters": meters_info.get_all_meters(),
            "period_start": period_start,
            "period_end": period_end,
            "best_tariff": to_string_tariff(best_tariff),
            "current_tariff": to_string_tariff(meter_info.tariff),
            "tariff_savings": round(bill_total.get_total() - bill_best_case.get_total(), 2),
            "best_contracted_power": best_contracted_power}

######
def get_parameters_device_simulator(meter_id, appliance_id, appliance_data, period_start):

    start_datetime = PREVIOUS_MONTH_START
    end_datetime = PREVIOUS_MONTH_END

    meter_info = meters_info.get_meter_id_contract_info(meter_id)

    appliance_data=pd.DataFrame(appliance_data[appliance_id])
    calculator = BillingCalculator(tariff_data_load, tarriff_periods)

    power_data = power_loader.get_power_meter_id(meter_id).loc[start_datetime:end_datetime]
    old_bill = calculator.compute_total_cost(power_data, meter_info.contracted_power, meter_info.tariff)

    appliance_data=appliance_data[:power_data.shape[0]]
    max_power = power_data[meter_id].max()+appliance_data[appliance_id].max()
    power_data[meter_id]=power_data[meter_id]+appliance_data[appliance_data.columns[0]].values
    new_bill = calculator.compute_total_cost(power_data, meter_info.contracted_power, meter_info.tariff)

    best_contracted_power = recommend_contract(max_power)
    return {"old_bill": round(old_bill.get_total(), 2),
            "new_bill": round(new_bill.get_total(), 2),
            "dif_bill": round(new_bill.get_total()-old_bill.get_total(), 2),
            "best_contracted_power": best_contracted_power,
            "all_meters": meters_info.get_all_meters(),
            "meter_id": meter_id,
            "all_appliances": appliances_data.columns,
            "appliance_id": appliance_id}
######

# Create your views here.
@login_required
def index(request):
    meter_id = get_meter_id_from_query_parm(request)
    meter_power = power_loader.get_power_meter_id(meter_id)
    meter_info = meters_info.get_meter_id_contract_info(meter_id)

    power_period_month = filter_power_by_date(meter_power, str(START_MONTH.date()), str(TODAY.date()))
    power_period_month_grouped_days = power_period_month.groupby(
        power_period_month.index.strftime('%D')).sum().values.flatten()

    billing_period_month = round(calculator.compute_total_cost(power_period_month, meter_info.contracted_power,
                                                               meter_info.tariff).get_total(), 2)

    same_period_last_year_start = START_MONTH.replace(year=START_MONTH.year - 1)
    same_period_last_year_today = same_period_last_year_start.replace(day=TODAY.day)

    power_period_month_last_year = filter_power_by_date(meter_power, str(same_period_last_year_start.date()),
                                                        str(same_period_last_year_today.date()))
    power_grouped_days_last_year = power_period_month_last_year.groupby(
        power_period_month_last_year.index.strftime('%D')).sum().values.flatten()

    billing_period_month_last_year = round(calculator.compute_total_cost(power_period_month_last_year,
                                                                         meter_info.contracted_power,
                                                                         meter_info.tariff).get_total(), 2)

    param = get_parameters_period_overview(meter_id, PREVIOUS_MONTH_START, PREVIOUS_MONTH_END)
    param["active_tab_dashboard"] = "class=active has-sub"
    param["billing_period_month_last_year"] = billing_period_month_last_year
    param["billing_period_month_last_year_label"] = same_period_last_year_start.strftime("%m-%Y")
    param["billing_period_month"] = billing_period_month
    param["billing_period_month_label"] = TODAY.strftime("%m-%Y")
    param["plot_current_month"] = list(power_period_month_grouped_days / 1000)
    param["plot_last_year_month"] = list(power_grouped_days_last_year / 1000)
    param["plot_axes"] = list(range(1, TODAY.day + 1))
    param["today"] = TODAY.date()
    param["start_month"] = START_MONTH.date()
    return render(request, 'index_2.html', param)


@login_required
def analyser(request):
    if request.method == "GET":

        meter = get_meter_id_from_query_parm(request)
        param = get_parameters_period_overview(meter, PREVIOUS_MONTH_START, PREVIOUS_MONTH_END)
        param["active_tab_analyser"] = "class=active has-sub"
        param["today"] = TODAY
    else:

        param = get_parameters_period_overview(request.POST["meter_id"], request.POST["date-start"],
                                               request.POST["date-end"])
        param["active_tab_analyser"] = "class=active has-sub"
        param["today"] = TODAY

    return render(request, "tariff_analyser.html", param)


@login_required
def pv(request):
    meter_id = get_meter_id_from_query_parm(request)
    meter_power = power_loader.get_power_meter_id(meter_id)

    n_panels = int(meter_power[meter_power != 0].mean().values[0] / pv_power.mean().values[0])

    return render(request, "pv.html", {"active_tab_photovoltaic": "class=active has-sub",
                                       "plot_pv": plot_var([meter_power, n_panels * pv_power],
                                                           runtime=1, legend_name=['house load',
                                                                                   f'load from {n_panels} panels']),
                                       "all_meters": meters_info.get_all_meters(),
                                       "meter_id": meter_id,
                                       "today": TODAY})


@login_required
def device_simulator(request):
    meter_id = get_meter_id_from_query_parm(request)
    appliance_id = get_appliance_id_from_query_parm(request)
    param=get_parameters_device_simulator(meter_id, appliance_id, appliances_data, PREVIOUS_MONTH_START)

    return render(request, "device_simulator.html", param)


@login_required
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

    saving_small_adj = round(current_price - calculator.compute_total_cost(meter_power, contracted_power_perc_small,
                                                                           meter_info.tariff).get_total(), 2)

    saving_some_adj = round(current_price - calculator.compute_total_cost(meter_power, contracted_power_perc_some,
                                                                          meter_info.tariff).get_total(), 2)

    result = plot_var(meter_power, runtime=1, threshold=[a * kW for a in [meter_info.contracted_power,
                                                                          best_contracted_power,
                                                                          contracted_power_perc_small,
                                                                          contracted_power_perc_some]])

    return render(request, "contract_subscription.html", {"active_contract_subscription": "class=active has-sub",
                                                          "no_adjustment_price": saving_no_adj,
                                                          "small_adjustment_price": saving_small_adj,
                                                          "medium_adjustment_price": saving_some_adj,
                                                          "current_contract": meter_info.contracted_power,
                                                          "percentil_small_adjustment": round(
                                                              100 - percentil_small_adjustment, 3),
                                                          "percentil_some_adjustments": round(
                                                              100 - percentil_some_adjustments, 2),
                                                          "all_meters": meters_info.get_all_meters(),
                                                          "meter_id": meter_id,
                                                          "result": result
                                                          })


@login_required
def tariff_subscription(request):
    meter_id = get_meter_id_from_query_parm(request)
    meter_power = power_loader.get_power_meter_id(meter_id)
    meter_info = meters_info.get_meter_id_contract_info(meter_id)

    current_price = calculator.compute_total_cost(meter_power, meter_info.contracted_power,
                                                  meter_info.tariff).get_total()

    # Recommend the best tariff taken into account the two years info
    best_tariff, costs_tariffs = recommender_tariff.get_best_tariff(power_loader.get_power_meter_id(meter_id),
                                                                    meter_info.contracted_power)

    costs_tariffs_month = recommender_tariff.get_tariff_billing_by_months(meter_power, meter_info.contracted_power)

    label_tariff_months = list(costs_tariffs_month.keys())
    simple_tariff_months = [round(value[TariffType.SIMPLE], 2) for month, value in costs_tariffs_month.items()]
    two_tariff_months = [round(value[TariffType.TWO_PERIOD], 2) for month, value in costs_tariffs_month.items()]
    three_tariff_months = [round(value[TariffType.THREE_PERIOD], 2) for month, value in costs_tariffs_month.items()]

    return render(request, "tariff_subscription.html", {"active_tariff_subscription": "class=active has-sub",
                                                        "all_meters": meters_info.get_all_meters(),
                                                        "current_tariff": get_name_tariff(meter_info.tariff),
                                                        "meter_id": meter_id,
                                                        "simple_tariff_savings": round(
                                                            current_price - costs_tariffs[TariffType.SIMPLE], 2),
                                                        "two_tariff_savings": round(
                                                            current_price - costs_tariffs[TariffType.TWO_PERIOD], 2),
                                                        "three_tariff_savings": round(
                                                            current_price - costs_tariffs[TariffType.THREE_PERIOD], 2),
                                                        "today": TODAY,
                                                        "simple_tariff_cross_months": simple_tariff_months,
                                                        "two_tariff_cross_months": two_tariff_months,
                                                        "three_tariff_cross_months": three_tariff_months,
                                                        "months_tariff_label": label_tariff_months})


def notifications(request):
    return render(request, 'notifications.html')
