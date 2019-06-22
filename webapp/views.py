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
import pandas as pd
import numpy as np


meters_info = MetersInformation(settings.RESOURCES + "/dataset_index.csv")
power_loader = PowerDataLoader(settings.RESOURCES + "/load_pwr.csv")
tarriff_periods = TariffPeriods(settings.RESOURCES + "/HackTheElectron dataset support data/Tariff-Periods-Table 1.csv")
tariff_data_load = TariffDataLoader(settings.RESOURCES + "/HackTheElectron dataset support data/"

                                                         "Regulated Tarrifs-Table 1.csv")

pv_power = CSVDataLoader(settings.RESOURCES + "/pv_pwr.csv", parse_dates=['Date']).data_frame.set_index('Date')

device_signal = CSVDataLoader(settings.RESOURCES + "/device_signal.csv").data_frame.drop(['Unnamed: 0'],axis=1)
device_signalsize = CSVDataLoader(settings.RESOURCES + "/device_signalsize.csv").data_frame.drop(['Unnamed: 0'],axis=1)

calculator = BillingCalculator(tariff_data_load, tarriff_periods)
recommender_tariff = TariffRecommender(tariff_data_load, tarriff_periods)

TODAY = datetime.datetime(2018, 9, 16, 23, 59)
START_MONTH = TODAY.replace(day=1)

PREVIOUS_MONTH_END = START_MONTH - datetime.timedelta(days=1)
PREVIOUS_MONTH_START = PREVIOUS_MONTH_END.replace(day=1)


def get_meter_id_from_query_parm(request):
    if "meter" not in request.GET:
        return "meter_0"
    else:
        return request.GET["meter"]


def get_device_id_from_query_parm(request):
    if "device_id" not in request.GET:
        return "Air Conditioner"
    else:
        return request.GET["device_id"]


def get_name_tariff(tariff: TariffType):
    if tariff == TariffType.SIMPLE:
        return "Simple"
    elif tariff == TariffType.TWO_PERIOD:
        return "Two-Periods"
    elif tariff == TariffType.THREE_PERIOD:
        return "Three-Period"

def get_device_daily_from_query_parm(request):
    if "device_daily" not in request.GET:
        return 0
    else:
        return request.GET["device_daily"]

def get_device_weekly_from_query_parm(request):
    if "device_weekly" not in request.GET:
        return 0
    else:
        return request.GET["device_weekly"]


def get_power_grouped_by_days(power_data: pd.DataFrame) -> pd.DataFrame:
    return power_data.groupby(power_data.index.strftime('%D')).sum().values.flatten()


def get_parameters_period_overview(meter_id: str, period_start: datetime, period_end: datetime):
    meter_info = meters_info.get_meter_id_contract_info(meter_id)

    power_loader_meter = filter_power_by_date(power_loader.get_power_meter_id(meter_id), period_start, period_end)
    power_loader_meter_all_period = filter_power_by_date(power_loader.get_power_meter_id(meter_id), end_datetime=TODAY)

    df_power_loader_meter_hours_minuts_sum = power_loader_meter.groupby(power_loader_meter.index.strftime('%H')).sum()
    power_loader_meter_hours_minuts_sum = df_power_loader_meter_hours_minuts_sum.values.flatten()

    df_power_loader_meter_hours_max = power_loader_meter.groupby(power_loader_meter.index.strftime('%H')).max()
    power_loader_meter_hours_max = df_power_loader_meter_hours_max.values.flatten()

    billing_period = calculator.compute_total_cost(power_loader_meter, meter_info.contracted_power, meter_info.tariff)
    percentages_peak_type_hours = {HourTariffType.PEAK: 0, HourTariffType.OFF_PEAK: 0, HourTariffType.SUPER_OFF_PEAK: 0}
    percentages_peak_type_spent = {HourTariffType.PEAK: 0, HourTariffType.OFF_PEAK: 0, HourTariffType.SUPER_OFF_PEAK: 0}

    for peak_type in billing_period.times_peaks_distribution:
        percentages_peak_type_hours[peak_type] = round(
            billing_period.times_peaks_distribution[peak_type] / sum(billing_period.times_peaks_distribution.values()), 2)
        percentages_peak_type_spent[peak_type] = round(
            billing_period.costs_peaks_distribution[peak_type] / sum(billing_period.costs_peaks_distribution.values()), 2)

    recommender_tariff = TariffRecommender(tariff_data_load, tarriff_periods)

    # Recommend the best tariff taken into account the two years info
    best_tariff, costs_tariffs = recommender_tariff.get_best_tariff(power_loader_meter_all_period,
                                                                    meter_info.contracted_power)

    bill_total = calculator.compute_total_cost(power_loader_meter_all_period, meter_info.contracted_power,
                                               meter_info.tariff)
    best_contracted_power = recommend_contract(power_loader_meter_all_period)

    bill_best_case = calculator.compute_total_cost(power_loader_meter_all_period, best_contracted_power,
                                                   best_tariff)

    max_power_registered = min(round(power_loader_meter.max().values[0] / 1000, 2), meter_info.contracted_power)


    # Last year info
    same_period_last_year_start = period_start.replace(year=period_start.year - 1)
    same_period_last_year_end = period_end.replace(year=period_end.year-1)

    power_period_last_year = filter_power_by_date(power_loader.get_power_meter_id(meter_id),
                                                  same_period_last_year_start, same_period_last_year_end)

    billing_period_month_last_year = round(calculator.compute_total_cost(power_period_last_year,
                                                                         meter_info.contracted_power,
                                                                         meter_info.tariff).get_total(), 2)
    appliances_label = ["MicroWave", "Fridge", "Oven", "Air-Condit", "Heater", "TV", "Hair Dyer"]
    appliances_data = [90, 120, 400, 30, 200, 250, 330]

    param = {"contracted_power": meter_info.contracted_power,
             "mean_load": round(power_loader_meter.mean().values[0] / 1000, 2),
             "peak_load": round(power_loader_meter.max().values[0] / 1000, 2), "meter_id": meter_id,
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
             "power_spent_by_hours_label": list(range(0, 24)), "all_meters": meters_info.get_all_meters(),
             "period_start": period_start, "period_end": period_end, "best_tariff": to_string_tariff(best_tariff),
             "current_tariff": to_string_tariff(meter_info.tariff),
             "tariff_savings": round(bill_total.get_total() - bill_best_case.get_total(), 2),
             "best_contracted_power": best_contracted_power,
             "percentage_contracted_power_registered": max_power_registered * 100 / meter_info.contracted_power,
             "max_contracted_power_registered": max_power_registered,
             "billing_period_month_last_year": billing_period_month_last_year,
             "billing_period_month_last_year_label": same_period_last_year_start.strftime("%m-%Y"),
             "billing_period_month": billing_period.get_total(),
             "billing_period_month_label": period_start.strftime("%m-%Y"),
             "plot_current_month": list(get_power_grouped_by_days(power_loader_meter) / 1000),
             "plot_last_year_month": list(get_power_grouped_by_days(power_period_last_year) / 1000),
             "plot_axes": list(range(1, TODAY.day + 1)), "today": TODAY.date(), "start_month": START_MONTH.date(),
             "appliances_label": appliances_label,
             "appliances_data": appliances_data,
             "percentage_bill": int(
                 abs((billing_period_month_last_year - billing_period.get_total()) * 100 / billing_period_month_last_year))}

    return param


def get_parameters_device_simulator(meter_id, device_id, day_times, week_times):

    start_datetime = PREVIOUS_MONTH_START
    end_datetime = PREVIOUS_MONTH_END

    meter_info = meters_info.get_meter_id_contract_info(meter_id)
    calculator = BillingCalculator(tariff_data_load, tarriff_periods)
    power_data = power_loader.get_power_meter_id(meter_id).loc[start_datetime:end_datetime]

    device_data=power_data.copy()

    step_d=96//device_signalsize[device_id][0]
    start_w=4-(week_times+1)//2
    if step_d%2 == 0:
        start_d=int((step_d/2)-(day_times+1)//2)
    else:
        start_d=int(((step_d+1)/2)-(day_times+1)//2)

    active_h=device_signal[device_id][:step_d].to_list()
    inactive_h=[0 for i in range(step_d)]
    inactive_d=[0 for i in range(96)]

    active_d=[]
    for i in range(96//step_d):
        if (i >= start_d) & (i < start_d+day_times):
            active_d.extend(active_h)
        else:
            active_d.extend(inactive_h)

    active_w=[]
    for i in range(7):
        if (i >= start_w) & (i < start_w+week_times):
            active_w.extend(active_d)
        else:
            active_w.extend(inactive_d)

    active_m=[]
    for i in range(5):
            active_m.extend(active_w)

    device_data[meter_id]=active_m[:power_data.shape[0]]
    old_bill = calculator.compute_total_cost(power_data, meter_info.contracted_power, meter_info.tariff)

    max_power = power_data[meter_id].max()+device_data[meter_id].max()
    power_data[meter_id]=power_data[meter_id]+device_data[meter_id]
    new_bill = calculator.compute_total_cost(power_data, meter_info.contracted_power, meter_info.tariff)

    best_contracted_power = recommend_contract(max_power)
    return {"old_bill": round(old_bill.get_total(), 2),
            "new_bill": round(new_bill.get_total(), 2),
            "dif_bill": round(new_bill.get_total()-old_bill.get_total(), 2),
            "best_contracted_power": best_contracted_power,
            "all_meters": meters_info.get_all_meters(),
            "meter_id": meter_id,
            "all_devices": device_signalsize.columns,
            "device_id": device_id,
            "max_per_day": step_d
           }


# Create your views here.
@login_required
def index(request):
    meter_id = get_meter_id_from_query_parm(request)

    period_start = TODAY.replace(day=1)
    period_end = TODAY

    param = get_parameters_period_overview(meter_id, period_start, period_end)
    param["active_tab_dashboard"] = "class=active has-sub"

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
    dic_pv = pv_savings(meter_id)
    dic_pv_and_bat = pv_and_battery_savings(meter_id)

    return render(request, "pv.html", {"active_tab_photovoltaic": "class=active has-sub",
                                       "all_meters": meters_info.get_all_meters(),
                                       "meter_id": meter_id,
                                       "pv_data": dic_pv,
                                       "pv_and_bat_data": dic_pv_and_bat,
                                       "today": TODAY})


@login_required
def device_simulator(request):
    meter_id = get_meter_id_from_query_parm(request)
    device_id = get_device_id_from_query_parm(request)
    device_daily = get_device_daily_from_query_parm(request)
    device_weekly = get_device_weekly_from_query_parm(request)
    param=get_parameters_device_simulator(meter_id, device_id, device_daily, device_weekly)

    return render(request, "device_simulator.html", param)


@login_required
def contract_subscription(request):
    meter_id = get_meter_id_from_query_parm(request)
    meter_power = power_loader.get_power_meter_id(meter_id)
    meter_power = filter_power_by_date(meter_power, end_datetime=TODAY)

    meter_info = meters_info.get_meter_id_contract_info(meter_id)
    kW = 1000

    percentil_no_adjustment = 100
    percentil_small_adjustment = 99.99
    percentil_some_adjustments = 99.95

    best_contracted_power = round(recommend_contract(meter_power, percentile=percentil_no_adjustment), 2)
    contracted_power_perc_small = round(recommend_contract(meter_power, percentile=percentil_small_adjustment), 2)
    contracted_power_perc_some = round(recommend_contract(meter_power, percentile=percentil_some_adjustments), 2)

    df_power_loader_meter_hours_max = meter_power.groupby(meter_power.index.strftime('%Y-%m')).max()

    labels_contract_power_by_month = df_power_loader_meter_hours_max.index.to_list()
    max_contract_power_by_month = list(df_power_loader_meter_hours_max.values.flatten()/1000)

    contracted_powers_perc = list({best_contracted_power, contracted_power_perc_small, contracted_power_perc_some})

    if meter_info.contracted_power in contracted_powers_perc:
        contracted_powers_perc.remove(meter_info.contracted_power)

    contracted_powers_perc.sort(reverse=True)

    contracted_power_values = [meter_info.contracted_power for el in range(len(max_contract_power_by_month))]

    recommended_contracted_powers_perc_values = []
    recommended_contracted_powers_perc_label = []
    for contracted_power in contracted_powers_perc:
        recommended_contracted_powers_perc_values.append([contracted_power for el in range(len(max_contract_power_by_month))])
        recommended_contracted_powers_perc_label.append(str(contracted_power) + "kW")

    current_price = calculator.compute_total_cost(meter_power, meter_info.contracted_power,
                                                  meter_info.tariff).get_total()
    saving_no_adj = round(current_price - calculator.compute_total_cost(meter_power, best_contracted_power,
                                                                        meter_info.tariff).get_total(), 2)

    saving_small_adj = round(current_price - calculator.compute_total_cost(meter_power, contracted_power_perc_small,
                                                                           meter_info.tariff).get_total(), 2)

    saving_some_adj = round(current_price - calculator.compute_total_cost(meter_power, contracted_power_perc_some,
                                                                          meter_info.tariff).get_total(), 2)

    return render(request, "contract_subscription.html", {"active_contract_subscription": "class=active has-sub",
                                                          "no_adjustment_price": saving_no_adj,
                                                          "small_adjustment_price": saving_small_adj,
                                                          "medium_adjustment_price": saving_some_adj,
                                                          "current_contract": meter_info.contracted_power,
                                                          "label_current_contract": str(meter_info.contracted_power) + "kW",
                                                          "percentil_small_adjustment": round(
                                                              100 - percentil_small_adjustment, 3),
                                                          "percentil_some_adjustments": round(
                                                              100 - percentil_some_adjustments, 2),
                                                          "all_meters": meters_info.get_all_meters(),
                                                          "meter_id": meter_id,
                                                          "labels_contract_power_by_month": labels_contract_power_by_month,
                                                          "max_contract_power_by_month": max_contract_power_by_month,
                                                          "contracted_powers_perc_values": recommended_contracted_powers_perc_values,
                                                          "contracted_powers_perc_label": recommended_contracted_powers_perc_label,
                                                          "contracted_power_values": contracted_power_values,
                                                          "no_adjustment_price_contract": best_contracted_power,
                                                          "small_adjustment_price_contract": contracted_power_perc_small,
                                                          "medium_adjustment_price_contract": contracted_power_perc_some,
                                                          })


@login_required
def tariff_subscription(request):
    meter_id = get_meter_id_from_query_parm(request)
    meter_power = power_loader.get_power_meter_id(meter_id)
    meter_power = filter_power_by_date(meter_power, end_datetime=TODAY)
    meter_info = meters_info.get_meter_id_contract_info(meter_id)

    current_price = calculator.compute_total_cost(meter_power, meter_info.contracted_power,
                                                  meter_info.tariff).get_total()

    # Recommend the best tariff taken into account the two years info
    best_tariff, costs_tariffs = recommender_tariff.get_best_tariff(meter_power,
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


def pv_savings(meter_id):
    """calculated series with several pv installation scenarios"""
    meter_power = power_loader.get_power_meter_id(meter_id)
    df_solar = pd.concat([meter_power, pv_power], axis=1)
    # df_solar_nozeros = df_solar.loc[df_solar.EPV != 0]
    df_solar['n_panels'] = df_solar.apply(lambda row: row[meter_id] / row.EPV if row.EPV else 0, axis=1)

    bill_0panel = calculator.compute_total_cost(meter_power,
                                                contracted_power=meters_info.get_meter_id_contract_info(
                                                    meter_id).contracted_power,
                                                tariff=meters_info.get_meter_id_contract_info(
                                                    meter_id).tariff).get_total()

    temp_vec = []

    for percentile in [10, 20, 30, 40, 50, 60, 70, 80, 90]:

        n_panel = int(np.nanpercentile(df_solar[df_solar.EPV != 0].n_panels, percentile))

        if n_panel == 0:
            continue

        # subtract the solar power of n panels to the 2 year load profile
        df_temp = (df_solar[meter_id] - n_panel * df_solar.EPV).to_frame(meter_id)
        df_temp = df_temp[meter_id].apply(lambda x: x if x > 0 else 0)

        # adjust for contract and tariff changes with each new load profile
        contract = recommend_contract(df_temp, 99.99)
        tariff = recommender_tariff.get_best_tariff(df_temp.to_frame(), contract)[0]

        # calculate what would be the bill if there were n panels
        bill = calculator.compute_total_cost(power_data=df_temp.to_frame(),
                                             contracted_power=contract,
                                             tariff=tariff).get_total()

        # panel fixed and per panel instalation cost
        bill_installation = 100 + 600 * n_panel

        # total saving with n panels in relation to 0 panel bill (per year)
        bill_savings_year = (bill_0panel - bill) / 2

        # time until savings reach the installation cost
        time_till_paid_panels = bill_installation / bill_savings_year

        temp = {'n_panels': n_panel,
                'installation_cost': bill_installation,
                'savings per year': bill_savings_year,
                'time for return': time_till_paid_panels}

        temp_vec.append(temp)

    return temp_vec


def calc_bat(capacity, load, threshold=0):
    """auxiliar function to calculate battery <-> load transfers"""
    new_cap = []
    new_load = []

    cumsum = 0
    for c, l in zip(capacity, load):
        current_load = 0
        if c > 0:
            if threshold and cumsum + c > threshold:
                cumsum = threshold
            else:
                cumsum += c
        elif l > 0:
            if l > cumsum:
                current_load = l - cumsum
                cumsum = 0
            elif l < cumsum:
                current_load = 0
                cumsum -= l
            else:
                current_load = 0
                cumsum = 0

        new_cap.append(cumsum)
        new_load.append(current_load)
    return new_cap, new_load


def pv_and_battery_savings(meter_id):
    """calculated series with several pv and battery installation scenarios"""

    BATTERY_CAPACITY = 2000  # Wh
    BATTERY_POWER = 1500  # W
    BATTERY_COST = 3500

    meter_power = power_loader.get_power_meter_id(meter_id)
    df_solar = pd.concat([meter_power, pv_power], axis=1)
    # df_solar_nozeros = df_solar.loc[df_solar.EPV != 0]
    df_solar['n_panels'] = df_solar.apply(lambda row: row[meter_id] / row.EPV if row.EPV else 0, axis=1)

    bill_0panel = calculator.compute_total_cost(meter_power,
                                                contracted_power=meters_info.get_meter_id_contract_info(
                                                    meter_id).contracted_power,
                                                tariff=meters_info.get_meter_id_contract_info(
                                                    meter_id).tariff).get_total()
    temp_vec = []

    for percentile in [10, 20, 30, 40, 50, 60, 70, 80, 90]:

        n_battery = 1
        n_panel = int(np.nanpercentile(df_solar[df_solar.EPV != 0].n_panels, percentile))

        if n_panel == 0:
            continue

        while True:

            df_temp = df_solar[meter_id].to_frame()
            df_temp['load_with_pv'] = (df_solar[meter_id] - n_panel * df_solar.EPV).to_frame(meter_id)
            # df_temp['load_with_pv'] = df_temp[meter_id].apply(lambda x: x if x > 0 else 0)
            if n_battery:
                df_temp['bat'] = df_temp['load_with_pv'].apply(lambda x: x*-1 if x < 0 else 0)
            else:
                df_temp['bat'] = df_temp['load_with_pv'].apply(lambda x: 0)

            df_temp['bat_real'],  df_temp['load_real'] = calc_bat(df_temp['bat'].to_list(),
                                                                  df_temp['load_with_pv'],
                                                                  threshold=BATTERY_CAPACITY*n_battery)

            # adjust for contract and tariff changes with each new load profile
            contract = recommend_contract(df_temp['load_real'], 99.99)
            tariff = recommender_tariff.get_best_tariff(df_temp['load_real'].to_frame(), contract)[0]

            # calculate what would be the bill if there were n panels
            bill = calculator.compute_total_cost(power_data=df_temp['load_real'].to_frame(),
                                                 contracted_power=contract,
                                                 tariff=tariff).get_total()

            # panel fixed and per panel instalation cost
            bill_installation = 100 + 600 * n_panel + n_battery * BATTERY_COST

            # total saving with n panels in relation to 0 panel bill (per year)
            bill_savings_year = (bill_0panel - bill) / 2

            # time until savings reach the installation cost
            time_till_paid_panels = bill_installation / bill_savings_year

            temp = {'n_panels': n_panel,
                    'n_batteries': n_battery,
                    'installation_cost': bill_installation,
                    'savings per year': bill_savings_year,
                    'time for return': time_till_paid_panels}

            temp_vec.append(temp)

            if df_temp['bat_real'].max() < BATTERY_CAPACITY*n_battery or time_till_paid_panels > 30:
                break
            else:
                n_battery += 1

    return temp_vec


import matplotlib.pyplot as plt
import datetime as dt
if __name__ == "__main__":

    start = dt.datetime.now()
    meter_id = 'meter_64'


    dic = pv_and_battery_savings(meter_id)
    print(dic)
    plt.plot([d['installation_cost'] for d in dic if d['time for return'] < 15],
             [d['time for return'] for d in dic if d['time for return'] < 15], 'o-')

    dic = pv_savings(meter_id)
    print(dic)
    plt.plot([d['installation_cost'] for d in dic if d['time for return'] < 15],
             [d['time for return'] for d in dic if d['time for return'] < 15], 'o-')

    plt.savefig("../output/panel_vs_bill.png")
    # plot_hist(df_solar.n_panels, filename='npanels', range=[0, np.nanpercentile(df_solar.n_panels, 70)])
    print(dt.datetime.now() - start)