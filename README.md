# Hack the electron-A!

Hi, this project was developed in the scope of the competition [Hack The Electron-A](https://taikai.network/en/edp-distribuicao/challenges/hacktheelectron-a). 
The main purpose of this competition was to improve energy efficiency!

## Demo 

[![capa](https://github.com/energy-army-knife/hack-the-electron-a/blob/master/resources/screenshot_button.png)](https://streamable.com/cg6svj)

## Install

### Prerequisites
The project is developed in Python, all the libraries required to execute it successfully are in the file requirements.txt.

### Run

To run the project and see the project interface just open the terminal and go to the base directory of this project and type the following command:
```
python manage.py runserver
```
The project webapp will be running by default on port **8000**, thus to access it just type in your we browser https://127.0.0.1:8000.

## Code examples

## Dataset Loading

The dataset was providaded in *.csv* files with different structures. There are some classes to load such files, additionally this classes have different methods to facilitate the data access. 
To load the power for each meter and the information regarding each meter you just have to call the following functions:

### Contract Info and Power
```
from electron_django import settings
from src.data_loader import MetersInformation, PowerDataLoader

meters_info = MetersInformation(settings.RESOURCES + "/dataset_index.csv")
power_loader = PowerDataLoader(settings.RESOURCES + "/load_pwr.csv")

# For example to get a meter contracted information you just have to type:
meter_analyse = "meter_0"
meter_info = meters_info.get_meter_id_contract_info(meter_analyse)

# The method get_meter_id_contract_info will return the class MeterContractInformation.
print("The meter {0} has a contracted power of {1} and the tariff {2}".format(meter_analyse, meter_info.contracted_power, meter_info.tariff))

```
### Tariff
Depending on the tariff the price of power spent in a certain period may cost a lot more or less than the average. In this competition three Tariffs were made available (Simple, Two-Period and Three-Period). In the loading process each column that have information about the tariff is parsed to the *Enum TariffType* to avoid bugs. In the example bellow is the code to load the information about tariffs.
```
from electron_django import settings  
from src.data_loader import TariffPeriods, TariffDataLoader  
  
tariff_data_loader = TariffDataLoader(settings.RESOURCES + "/HackTheElectron dataset support data/Regulated Tarrifs-Table 1.csv")  
tarriff_periods = TariffPeriods(settings.RESOURCES + "/HackTheElectron dataset support data/Tariff-Periods-Table 1.csv")
```
### Building Information
```
from electron_django import settings  
from src.data_loader import BuildingDataLoader  
  
building_data_loader = BuildingDataLoader(settings.RESOURCES + "/HackTheElectron dataset support data/"  
 "Building Info-Table 1.csv")  
  
print(building_data_loader.get_meters_by_building_and_service("Small", "Clients"))
```


### Power Spent Cost
As previously mentioned the power cost depends on the tariff but also on the contracted power. For each day even without usage the client has to pay a certain amount.
The class to compute the power cost is the *BillingCalculator*, the method of this class will return the am object named *Bill*. 
```
from electron_django import settings  
from src.billing_calculator import BillingCalculator  
from src.data_loader import MetersInformation, PowerDataLoader, TariffPeriods, TariffDataLoader  
  
meter_info = MetersInformation(settings.RESOURCES + "/dataset_index.csv")  
  
power_loader = PowerDataLoader(settings.RESOURCES + "/load_pwr.csv")  
  
tarriff_periods = TariffPeriods(settings.RESOURCES + "/HackTheElectron dataset support data/"  
 "Tariff-Periods-Table 1.csv")  
  
tariff_data_load = TariffDataLoader(settings.RESOURCES + "/HackTheElectron dataset support data/"  
 "Regulated Tarrifs-Table 1.csv")  
  
meter_analyse = "meter_0"  
  
info_meter_0 = power_loader.get_power_meter_id(meter_analyse)  
meter_contract = meter_info.get_meter_id_contract_info(meter_analyse)  
meter_power_0 = power_loader.get_power_meter_id(meter_analyse)  
  
billing_calculator = BillingCalculator(tariff_data_load, tarriff_periods)  
  
total_cost_simple = billing_calculator.compute_total_cost(meter_power_0, meter_contract.contracted_power,  
  meter_contract.tariff)  
  
print(total_cost_simple.get_total())
# The real cost of the power spent WITHOUT the day's portion.
print(total_cost_simple.get_cost_without_days_cut())
```

## Services Recommendation

### Contracted Power
```
from electron_django import settings  
from src.data_loader import PowerDataLoader  
from src.recommend_contract import recommend_contract  
  
power_loader = PowerDataLoader(settings.RESOURCES + "/load_pwr.csv")  
  
meter_analyse = "meter_0"  
meter_power_0 = power_loader.get_power_meter_id(meter_analyse)  
best_contracted_power = recommend_contract(power_loader.get_power_meter_id(meter_analyse))  
print("Best contracted Power {0}".format(best_contracted_power))
```
## Authors
[Bruno Galhardo](https://www.linkedin.com/in/bruno-galhardo/), [Fátima Machado](https://www.linkedin.com/in/mfatimamachado/), [Joana Faria](https://www.linkedin.com/in/joanafaria3/), [João Domingos](https://www.linkedin.com/in/joao-domingos/), [Tiago Cerqueira](https://www.linkedin.com/in/tiago-cerqueira-a705878/)
