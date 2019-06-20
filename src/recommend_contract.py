from src.data_loader import LoadAll
from src.make_plots import plot_hist, plot_var, plot_bar
import numpy as np
from datetime import datetime

kW = 1000

# TODO check if 1.15 is allowed
contracts_available = [a*kW for a in [1.15, 3.45, 4.6, 5.75, 6.9, 10.35, 13.8, 17.25, 20.7]]


def recommend_contract(meter_load, percentile=100.0):
    """recommend based on value
    - 100 (max) conservative approach
    - 99 corresponds to the load value in the 99 percentile"""

    load_value = np.nanpercentile(meter_load[meter_load != 0], percentile)

    for contract in contracts_available:
        if load_value < contract:
            return contract/kW

    return contracts_available[-1]/kW


if __name__ == '__main__':

    start = datetime.now()

    print('IMPORTING DATA')

    data = LoadAll()

    print('Done.')

    # loads dataframe
    meter_power = data.meter_power.data_frame

    # info dataframe
    meter_contract = data.meter_info.data_frame.ctrct_pw

    df_meter_stats = meter_power.mean().to_frame('mean_value').join(meter_contract*kW).join(
        meter_power.max().to_frame('max_value'))
    df_meter_stats[99] = meter_power.apply(lambda x: np.nanpercentile(x, 99))
    df_meter_stats[99.9] = meter_power.apply(lambda x: np.nanpercentile(x, 99.9))
    df_meter_stats[99.99] = meter_power.apply(lambda x: np.nanpercentile(x, 99.99))
    df_meter_stats[99.999] = meter_power.apply(lambda x: np.nanpercentile(x, 99.999))

    # plot_hist(meter_contract, filename='contract_distribution', xlabel='contracts [kW]')
    #
    # chosen_per = 99.9
    # plot_bar(df_meter_stats.index, [df_meter_stats.max_value/df_meter_stats.ctrct_pw,
    #                                 df_meter_stats[chosen_per]/df_meter_stats.ctrct_pw,
    #                                 df_meter_stats.mean_value/df_meter_stats.ctrct_pw],
    #          threshold=1,
    #          filename='contracted_normalise', xlabel='load / contracted power',
    #          legend_name=['max value normalised',
    #                       '{} percentile normalised'.format(chosen_per),
    #                       'mean value normalised'])

    for per in [99, 99.9, 99.99, 99.999, 100]:
        df_meter_stats['recommendation'] = meter_power.apply(lambda x: recommend_contract(x, per) * kW)

        plot_bar(df_meter_stats.index,
                 [df_meter_stats.max_value / df_meter_stats.recommendation,
                  df_meter_stats['max_value' if per == 100 else per] / df_meter_stats.recommendation,
                  df_meter_stats.mean_value / df_meter_stats.recommendation],
                 threshold=1,
                 filename='recommendated_normalise_{}'.format(str(per).replace('.', '_')),
                 xlabel='meter id',
                 ylabel='load / contracted power',
                 legend_name=['max value normalised',
                              '{} percentile normalised'.format(per),
                              'mean value normalised'])


    # plot meter 0
    meter = 'meter_0'
    string = plot_var(meter_power[meter], runtime=1, threshold=meter_contract[meter]*kW)
    print(string)
    # check runtime
    print(datetime.now() - start)
