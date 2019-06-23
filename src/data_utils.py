import datetime

import pandas as pd
from fbprophet import Prophet
import datetime

from src.data_models import TariffType

def to_string_tariff(tariff: TariffType):
    if tariff == TariffType.SIMPLE:
        return "Simples"
    elif tariff == TariffType.TWO_PERIOD:
        return "Two Period"
    elif tariff == TariffType.THREE_PERIOD:
        return "Three Period"


def filter_power_by_date(power_data: pd.DataFrame, start_datetime: datetime = None,
                         end_datetime: datetime = None) -> pd.DataFrame:

    if start_datetime and end_datetime is None:
        return power_data

    elif start_datetime is None:
        return power_data.loc[:end_datetime]

    elif end_datetime is None:
        return power_data.loc[start_datetime:]
    else:
        return power_data.loc[start_datetime:end_datetime]

def predict_power(power_data: pd.DataFrame, end_datetime: str = None, days_for_prediction=365) -> pd.DataFrame:
    if end_datetime is None:
        return power_data
    else:
        idx_name=power_data.index.name
        time_real=power_data.index[power_data.shape[0]-1]

        # use only 1 year for prediction
        power_data_h=power_data[time_real-datetime.timedelta(days=days_for_prediction):]
        power_data_h=power_data_h.groupby(pd.Grouper(freq='1H')).mean()

        power_data_h=power_data_h.reset_index()
        cols=(power_data_h.columns)
        power_data_h.columns=['ds','y']

        time_pred=datetime.datetime.strptime(end_datetime, '%Y-%m-%d')
        time_gap=time_pred-time_real
        min_gap=time_gap.days*24*4+time_gap.seconds//900

        model = Prophet(
        daily_seasonality=False,
        weekly_seasonality=False,
        yearly_seasonality=False,
        changepoint_prior_scale=0.1,
        )

        model.add_seasonality(name='yearly', period=365.25, fourier_order=6)
        model.add_seasonality(name='monthly', period=30.5, fourier_order=5)
        model.add_seasonality(name='weekly', period=7, fourier_order=4)
        model.add_seasonality(name='daily', period=1, fourier_order=3)
        model.add_country_holidays(country_name='PT')

        model.fit(power_data_h);

        future_data = model.make_future_dataframe(periods=min_gap, freq = '15min')
        forecast_data = model.predict(future_data)

        forecast_data=forecast_data[['ds','yhat']]
        forecast_data.columns=cols
        forecast_data.set_index([idx_name],inplace=True)
        power_data=pd.concat([power_data,forecast_data[time_real+datetime.timedelta(minutes=15):]], sort=True)
        
        return power_data
