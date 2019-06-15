from typing import List

import pandas as pd

from src.data_models import BuildingData, TariffCost, MeterContractInformation, TariffType, HourTariffType
from src.exceptions import BuildingDataLoaderException, TariffDataLoaderException, MeterDoesNotExistException


class CSVDataLoader:

    def __init__(self, csv_filename: str, sep: str = ';', parse_dates: list = None):
        self.csv_filename = csv_filename
        if parse_dates is not None:
            self.data_frame = pd.read_csv(self.csv_filename, sep=sep, parse_dates=parse_dates)
        else:
            self.data_frame = pd.read_csv(self.csv_filename, sep=sep)


class BuildingDataLoader(CSVDataLoader):
    COLUMN_NAME_TYPE = "Type"
    COLUMN_NAME_SERVICE = "Service"
    COLUMN_NAME_METER = "meter_id"

    def __init__(self, csv_filename: str, sep: str = ";"):
        super().__init__(csv_filename, sep=sep)

        self.building_types = list(set(self.data_frame[self.COLUMN_NAME_TYPE]))
        self.services = list(set(self.data_frame[self.COLUMN_NAME_SERVICE]))

    def get_building_types(self) -> list:
        return self.building_types

    def get_meters_id_by_building_type(self, building_type: str) -> List[str]:
        if building_type not in self.building_types:
            raise BuildingDataLoaderException("The building type {0} does not exist".format(building_type))
        return list(self.data_frame[self.data_frame[self.COLUMN_NAME_TYPE] == building_type][self.COLUMN_NAME_METER])

    def get_meters_id_by_service(self, service: str) -> List[str]:
        if service not in self.services:
            raise BuildingDataLoaderException("The service {0} does not exist".format(service))
        return list(self.data_frame[self.data_frame[self.COLUMN_NAME_SERVICE] == service][self.COLUMN_NAME_METER])

    def get_meters_by_building_and_service(self, building_type: str, service: str):

        meters_building_type = set(self.get_meters_id_by_building_type(building_type))
        meters_service = set(self.get_meters_id_by_service(service))
        return list(meters_building_type.intersection(meters_service))

    def get_meter_id_info(self, meter_id: str) -> BuildingData:
        df_meter_id = self.data_frame[self.data_frame.meter_id == meter_id]

        if df_meter_id.shape[0] == 0:
            raise BuildingDataLoaderException("The meter ID {0} does not exist the building data.".format(meter_id))
        elif df_meter_id.shape[0] > 1:
            raise BuildingDataLoaderException(
                "More than one meter with the ID {0} exist in the building data.".format(meter_id))

        df_meter_id = df_meter_id.loc[0]
        return BuildingData(df_meter_id[self.COLUMN_NAME_TYPE], df_meter_id[self.COLUMN_NAME_SERVICE],
                            df_meter_id[self.COLUMN_NAME_METER])


class TariffDataLoader(CSVDataLoader):
    COLUMN_NAME_CONTRACTED_POWER = "Contracted Power"
    COLUMN_NAME_TARIFF_TYPE = "Tariff Type"
    COLUMN_NAME_POWER_COST_DAY = "Power Cost eur/day"
    COLUMN_NAME_PEAK_PERIODS_COST = "Peak Periods Energy Cost eur/kwh"
    COLUMN_NAME_OFF_PEAK_PERIODS = "Off-Peak periods Energy Cost eur/kwh"
    COLUMN_NAME_SUPER_OFF_PEAK = "Super Off-Peak Energy Cost eur/kwh"

    def __init__(self, csv_filename: str, sep: str = ";"):
        super().__init__(csv_filename, sep=sep)
        self.data_frame[self.COLUMN_NAME_TARIFF_TYPE] = self.data_frame[self.COLUMN_NAME_TARIFF_TYPE].apply(lambda x: TariffType.from_str(x))
        columns_to_be_parsed = [self.COLUMN_NAME_CONTRACTED_POWER, self.COLUMN_NAME_POWER_COST_DAY,
                                self.COLUMN_NAME_PEAK_PERIODS_COST,
                                self.COLUMN_NAME_SUPER_OFF_PEAK, self.COLUMN_NAME_OFF_PEAK_PERIODS]

        for column in columns_to_be_parsed:
            parsed_column = self.data_frame[column].str.replace(",", ".").astype(float)
            self.data_frame[column] = parsed_column

        self.contracted_powers = list(set(self.data_frame[self.COLUMN_NAME_CONTRACTED_POWER]))

    def get_tariff_by_contracted_tariff_type(self, contracted_power: float, tariff_type: TariffType) -> TariffCost:
        if contracted_power not in self.contracted_powers:
            raise TariffDataLoaderException("The contracted power {0} does not exist. The options are: "
                                            "{1}.".format(contracted_power, self.contracted_powers))

        columns_contracted = self.data_frame[self.COLUMN_NAME_CONTRACTED_POWER] == contracted_power
        columns_tariff = self.data_frame[self.COLUMN_NAME_TARIFF_TYPE] == tariff_type
        row = self.data_frame[columns_contracted & columns_tariff]
        if row.shape[0] == 0:
            raise TariffDataLoaderException("The is not match for the criteria")
        elif row.shape[0] > 1:
            raise TariffDataLoaderException("The is more than one match for the criteria")

        row = row.iloc[0]
        return TariffCost(row[self.COLUMN_NAME_CONTRACTED_POWER], row[self.COLUMN_NAME_TARIFF_TYPE],
                          row[self.COLUMN_NAME_POWER_COST_DAY], row[self.COLUMN_NAME_PEAK_PERIODS_COST],
                          row[self.COLUMN_NAME_OFF_PEAK_PERIODS], row[self.COLUMN_NAME_SUPER_OFF_PEAK])


class PowerDataLoader(CSVDataLoader):
    COLUMN_NAME_TIME = "Time"

    def __init__(self, csv_filename: str, sep: str = ";"):
        super().__init__(csv_filename, sep=sep, parse_dates=[self.COLUMN_NAME_TIME])
        self.data_frame = self.data_frame.set_index(self.COLUMN_NAME_TIME).drop(columns=['Unnamed: 0'])

        self.time = self.data_frame.index

    def get_power_meter_id(self, meter_id) -> pd.DataFrame:
        try:
            return self.data_frame[meter_id].to_frame()
        except KeyError:
            raise MeterDoesNotExistException


class HolidayDataLoader(CSVDataLoader):

    def __init__(self, csv_filename: str, sep: str = ";"):
        super().__init__(csv_filename, sep=sep, parse_dates=["Date"])

    def get_holidays(self) -> pd.Series:
        return self.data_frame.Date


class TariffPeriods(CSVDataLoader):
    COLUMN_NAME_START_TARIFF = "Tariff"
    COLUMN_NAME_START_PERIOD = "Start"
    COLUMN_NAME_END_PERIOD = "End"
    COLUMN_NAME_TARIFF_TYPE = "Type"
    HOUR_FORMAT = r'%H:%M'

    def __init__(self, csv_filename: str, sep: str = ";"):
        super().__init__(csv_filename, sep=sep)
        self.data_frame[self.COLUMN_NAME_START_TARIFF] = self.data_frame[self.COLUMN_NAME_START_TARIFF].apply(lambda x: TariffType.from_str(x))
        self.data_frame[self.COLUMN_NAME_TARIFF_TYPE] = self.data_frame[self.COLUMN_NAME_TARIFF_TYPE].apply(lambda x: HourTariffType.from_str(x))

    def get_periods_for_tariff(self, tariff: TariffType) -> pd.DataFrame:
        return self.data_frame[self.data_frame[self.COLUMN_NAME_START_TARIFF] == tariff]


class MetersInformation(CSVDataLoader):

    COLUMN_NAME_TARIFF = "tariff"
    COLUMN_NAME_METER = "meter_id"
    COLUMN_NAME_PHASES = "n_phases"
    COLUMN_NAME_CONTRACTED_POWER = "ctrct_pw"

    def __init__(self, csv_filename: str):
        super().__init__(csv_filename)
        self.data_frame[self.COLUMN_NAME_TARIFF] = self.data_frame[self.COLUMN_NAME_TARIFF].apply(lambda x: TariffType.from_str(x))
        self.data_frame[self.COLUMN_NAME_CONTRACTED_POWER] = self.data_frame[self.COLUMN_NAME_CONTRACTED_POWER].astype(float)
        self.data_frame.set_index(self.COLUMN_NAME_METER, inplace=True)

    def get_meter_id_contract_info(self, meter_id: str) -> MeterContractInformation:
        row = self.data_frame.loc[meter_id]
        return MeterContractInformation(meter_id, row[self.COLUMN_NAME_TARIFF], row[self.COLUMN_NAME_CONTRACTED_POWER],
                                        row[self.COLUMN_NAME_PHASES])

    def get_meters_id_by_tariff(self, tariff_type: TariffType) -> list:
        return self.data_frame.loc[self.data_frame[self.COLUMN_NAME_TARIFF] == tariff_type].index.values

    def get_all_meters(self):
        return self.data_frame.index.to_list()


class LoadAll:
    def __init__(self):
        self.meter_info = MetersInformation("../resources/dataset_index.csv")
        self.meter_power = PowerDataLoader("../resources/load_pwr.csv")


if __name__ == '__main__':

    tarriff_periods = TariffPeriods("../resources/HackTheElectron dataset support data/"
                                    "Tariff-Periods-Table 1.csv")

    tarriff_periods_tariff_2 = tarriff_periods.get_periods_for_tariff(TariffType.TWO_PERIOD)

    meter_info = MetersInformation("../resources/dataset_index.csv")

    meter_analyse = "meter_0"

    power_loader = PowerDataLoader("../resources/load_pwr.csv")

    info_meter_0 = power_loader.get_power_meter_id(meter_analyse)
    meter_contract = meter_info.get_meter_id_contract_info(meter_analyse)

    for period_info in tarriff_periods_tariff_2.iterrows():
        period = period_info[1]
        info_meter_0.between_time(period[TariffPeriods.COLUMN_NAME_START_PERIOD],
                                  period[TariffPeriods.COLUMN_NAME_END_PERIOD])
    print("Starting Periods")
    # two_period_time = time.apply(lambda x: type_tariff_operation(x, "Time-of-Use three periods", tarriff_periods))
    print("Stop")
    # print(two_period_time)

    building_data_loader = BuildingDataLoader("../resources/HackTheElectron dataset support data/"
                                              "Building Info-Table 1.csv")

    tariffDataLoader = TariffDataLoader("../resources/HackTheElectron dataset support data/"
                                        "Regulated Tarrifs-Table 1.csv")

    holiday_loader = HolidayDataLoader("../resources/HackTheElectron dataset support data/"
                                       "Holiday-Table 1.csv")

    holidays = holiday_loader.get_holidays()

    power_loader.get_power_meter_id("meter_0")
    y = tariffDataLoader.get_tariff_by_contracted_tariff_type(3.45, TariffType.SIMPLE)
    print(y.contracted_power)