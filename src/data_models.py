from typing import List

import pandas as pd


class BuildingData:

    def __init__(self, df: pd.DataFrame):
        self.data_frame = df
        self.building_types = list(set(self.data_frame.Type))
        self.services = list(set(self.data_frame.Service))

    def get_building_types(self) -> list:
        return self.building_types

    def get_meters_id_by_building_type(self, building_type: str) -> List[str]:
        if building_type not in self.building_types:
            raise Exception("The building type does not exist")
        return list(self.data_frame[self.data_frame.Type == building_type].meter_id)

    def get_meters_id_by_service(self, service: str) -> List[str]:
        if service not in self.services:
            raise Exception("The service does not exist")
        return list(self.data_frame[self.data_frame.Service == service].meter_id)

    def get_meters_by_building_and_service(self, building_type: str, service: str):

        meters_building_type = set(self.get_meters_id_by_building_type(building_type))
        meters_service = set(self.get_meters_id_by_service(service))
        return list(meters_building_type.intersection(meters_service))

    def get_meter_id_info(self, meter_id: str) -> pd.DataFrame:
        return self.data_frame[self.data_frame.meter_id == meter_id]

