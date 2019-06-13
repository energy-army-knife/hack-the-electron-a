from enum import Enum


class BuildingData:

    def __init__(self, type: str, service: str, meter_id):
        self.type = type
        self.service = service
        self.meter_id = meter_id


class Season(Enum):
    Winter = 1
    Summer = 2
    ALL = Winter | Summer


class HourTariffType(Enum):
    PEAK = 1
    OFF_PEAK = 2
    SUPER_OFF_PEAK = 3

    @staticmethod
    def from_str(label: str):
        label = label.lower().strip()

        if label == "peak":
            return HourTariffType.PEAK

        elif label == "off-peak":
            return HourTariffType.OFF_PEAK

        elif label == "super off-peak":
            return HourTariffType.SUPER_OFF_PEAK

        else:
            raise NotImplementedError


class TariffType(Enum):
    SIMPLE = 1
    TWO_PERIOD = 2
    THREE_PERIOD = 3

    @staticmethod
    def from_str(label: str):
        label = label.lower().strip()

        if label == "simple tariff":
            return TariffType.SIMPLE

        elif label == "time-of-use two periods":
            return TariffType.TWO_PERIOD

        elif label == "time-of-use three periods":
            return TariffType.THREE_PERIOD

        else:
            raise NotImplementedError


class TariffCost:

    def __init__(self, contracted_power: float, tariff_type: TariffType, power_cost_per_day: float, peak_periods_cost: float,
                 off_peak_periods: float, super_peak_cost: float):
        self.contracted_power = contracted_power
        self.tariff_type = tariff_type
        self.power_cost_per_day = power_cost_per_day
        self.peak_periods_cost = peak_periods_cost
        self.off_peak_periods = off_peak_periods
        self.super_peak_cost = super_peak_cost


class MeterContractInformation:

    def __init__(self, meter_id: str, tariff: TariffType, contracted_power: float, n_phases: str):
        self.meter_id = meter_id
        self.tariff = tariff
        self.contracted_power = contracted_power
        self.n_phases = n_phases
