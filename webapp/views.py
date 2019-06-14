from django.shortcuts import render

from electron_django import settings
from src.billing_calculator import BillingCalculator
from src.data_loader import MetersInformation, PowerDataLoader, TariffPeriods, TariffDataLoader
from src.data_models import TariffType, HourTariffType
from src.data_utils import filter_power_by_date
from src.exceptions import TariffDoesNotExistException
from flask import json

meters_info = MetersInformation(settings.RESOURCES + "/dataset_index.csv")
power_loader = PowerDataLoader(settings.RESOURCES + "/load_pwr.csv")
tarriff_periods = TariffPeriods(settings.RESOURCES + "/HackTheElectron dataset support data/Tariff-Periods-Table 1.csv")
tariff_data_load = TariffDataLoader(settings.RESOURCES + "/HackTheElectron dataset support data/"

                                                         "Regulated Tarrifs-Table 1.csv")


def get_meter_id_from_query_parm(request):
    if "meter" not in request.GET:
        return "meter_0"
    else:
        return request.GET["meter"]


# Create your views here.
def index(request):
    return display_month_overview(request, get_meter_id_from_query_parm(request), 'index.html', "2016-10-1",
                                  "2016-10-30")


def display_month_overview(request, meter_id, html_name, period_start, period_end):
    meter_info = meters_info.get_meter_id_contract_info(meter_id)
    power_loader_meter = filter_power_by_date(power_loader.get_power_meter_id(meter_id), period_start, period_end)

    df_power_loader_meter_hours_minuts = power_loader_meter.groupby(power_loader_meter.index.strftime('%H')).sum()
    power_loader_meter_hours_minuts = df_power_loader_meter_hours_minuts.values.flatten()

    calculator = BillingCalculator(power_loader_meter, tariff_data_load, tarriff_periods)
    bill = calculator.compute_total_cost(meter_info.contracted_power, meter_info.tariff)
    if meter_info.tariff == TariffType.SIMPLE:
        percentage_last_month_peak = 100
        percentage_last_month_off_peak = 0
        percentage_last_month_super_off_peak = 0

    elif meter_info.tariff == TariffType.TWO_PERIOD:
        total = sum(bill.costs_peaks_distribution.values())
        percentage_last_month_peak = bill.costs_peaks_distribution[HourTariffType.PEAK] / total
        percentage_last_month_off_peak = bill.costs_peaks_distribution[HourTariffType.OFF_PEAK] / total
        percentage_last_month_super_off_peak = 0

    elif meter_info.tariff == TariffType.THREE_PERIOD:
        total = sum(bill.costs_peaks_distribution.values())
        percentage_last_month_peak = bill.costs_peaks_distribution[HourTariffType.PEAK] / total
        percentage_last_month_off_peak = bill.costs_peaks_distribution[HourTariffType.OFF_PEAK] / total
        percentage_last_month_super_off_peak = bill.costs_peaks_distribution[HourTariffType.SUPER_OFF_PEAK] / total
    else:
        raise TariffDoesNotExistException

    return render(request, html_name, {"contracted_power": meter_info.contracted_power,
                                       "bill": round(bill.get_value(), 2),
                                       "mean_load": round(power_loader_meter.mean().values[0] / 1000, 2),
                                       "peak_load": round(power_loader_meter.max().values[0] / 1000, 2),
                                       "meter_id": meter_id,
                                       "tariff": meter_info.tariff.value,
                                       "percentage_last_month_peak": round(percentage_last_month_peak, 2),
                                       "percentage_last_month_off_peak": round(percentage_last_month_off_peak, 2),
                                       "percentage_last_month_super_off_peak": round(
                                           percentage_last_month_super_off_peak, 2),
                                       "power_spent_by_hours": json.dumps(list(power_loader_meter_hours_minuts)),
                                       "power_spent_by_hours_label": json.dumps(list(range(0, 24))),
                                       "all_meters": meters_info.get_all_meters()},

                  )


def analyser(request):
    if request.method == "GET":
        return display_month_overview(request, get_meter_id_from_query_parm(request), "tariff_analyser.html",
                                      "2016-10-01", "2016-10-31")
    else:

        return display_month_overview(request, request.POST["meter_id"], "tariff_analyser.html",
                                      request.POST["date-start"],
                                      request.POST["date-end"])


def notifications(request):
    return render(request, 'notifications.html')
