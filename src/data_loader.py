import pandas as pd

from src.data_models import BuildingData


class DataLoader:

    def __init__(self, csv_filename: str):
        self.csv_filename = csv_filename

    def load(self):
        pass


class BuildingDataLoader(DataLoader):

    def __init__(self, csv_filename: str):
        super().__init__(csv_filename)

    def load(self) -> BuildingData:
        return BuildingData(pd.read_csv(self.csv_filename, sep=';'))


if __name__ == '__main__':

    building_data = BuildingDataLoader("../resources/HackTheElectron dataset support data/Building Info-Table 1.csv").load()
    print(building_data.get_meters_id_by_service("Clients"))
