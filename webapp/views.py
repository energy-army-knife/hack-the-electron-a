from django.shortcuts import render

from electron_django import settings
from loader.billing_calculator import BillingCalculator
from loader.data_loader import MetersInformation, PowerDataLoader, TariffPeriods, TariffDataLoader
from loader.data_models import TariffType, HourTariffType
from loader.data_utils import filter_power_by_date
from loader.exceptions import TariffDoesNotExistException

meters_info = MetersInformation(settings.RESOURCES + "/dataset_index.csv")
power_loader = PowerDataLoader(settings.RESOURCES + "/load_pwr.csv")
tarriff_periods = TariffPeriods(settings.RESOURCES + "/HackTheElectron dataset support data/Tariff-Periods-Table 1.csv")
tariff_data_load = TariffDataLoader(settings.RESOURCES + "/HackTheElectron dataset support data/"
                                                         "Regulated Tarrifs-Table 1.csv")


# Create your views here.
def index(request):

    if "meter" not in request.GET:
        meter_analyse = "meter_0"
    else:
        meter_analyse = request.GET["meter"]

    meter_info = meters_info.get_meter_id_contract_info(meter_analyse)
    power_loader_meter = filter_power_by_date(power_loader.get_power_meter_id(meter_analyse), "2016-10-1", "2016-10-30")
    calculator = BillingCalculator(power_loader_meter, tariff_data_load, tarriff_periods)
    bill = calculator.compute_cost(meter_info.contracted_power, meter_info.tariff)
    if meter_info.tariff == TariffType.SIMPLE:
        percentage_last_month_peak = 100
        percentage_last_month_off_peak = 0
        percentage_last_month_super_off_peak = 0

    elif meter_info.tariff == TariffType.TWO_PERIOD:
        total = sum(bill.costs_peaks_distribution.values())
        percentage_last_month_peak = bill.costs_peaks_distribution[HourTariffType.PEAK]/total
        percentage_last_month_off_peak = bill.costs_peaks_distribution[HourTariffType.OFF_PEAK]/total
        percentage_last_month_super_off_peak = 0

    elif meter_info.tariff == TariffType.THREE_PERIOD:
        total = sum(bill.costs_peaks_distribution.values())
        percentage_last_month_peak = bill.costs_peaks_distribution[HourTariffType.PEAK]/total
        percentage_last_month_off_peak = bill.costs_peaks_distribution[HourTariffType.OFF_PEAK]/total
        percentage_last_month_super_off_peak = bill.costs_peaks_distribution[HourTariffType.SUPER_OFF_PEAK]/total
    else:
        raise TariffDoesNotExistException

    return render(request, 'index.html', {"contracted_power": meter_info.contracted_power,
                                          "current_bill": round(bill.get_value(), 2),
                                          "mean_load": round(power_loader_meter.mean()/1000, 2),
                                          "peak_load": round(power_loader_meter.max()/1000, 2),
                                          "name_user": meter_analyse, "meter_id": meter_analyse,
                                          "tariff": meter_info.tariff.value,
                                          "percentage_last_month_peak": round(percentage_last_month_peak, 2),
                                          "percentage_last_month_off_peak": round(percentage_last_month_off_peak, 2),
                                          "percentage_last_month_super_off_peak": round(percentage_last_month_super_off_peak, 2)})


def charts(request):
    return render(request, 'chart.html')


def notifications(request):
    return render(request, 'notifications.html')