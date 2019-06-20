from io import BytesIO
import base64

import matplotlib.pyplot as plt
import matplotlib

matplotlib.rcParams.update({'font.size': 20})
PLOT_PATH = '../output/'


def plot_var(data, runtime=0, filename='filename', extension='png', ylabel='Load [kW]', legend_name=(), xlabel='', threshold=0):
    """saves image with plots from each column in Dataframe"""

    fig = plt.figure(figsize=(15, 10))
    data = data if isinstance(data, list) else [data]
    # plot time series voltage
    for d in data:
        plt.plot(d)
    plt.xticks(rotation=70)
    plt.ylabel(ylabel)
    if xlabel:
        plt.xlabel(xlabel)
    if len(legend_name) > 0:
        plt.legend(legend_name)
    if threshold:
        if not isinstance(threshold, list):
            threshold = [threshold]
        for t in threshold:
            plt.axhline(t, color='red', lw=2)
    plt.grid(axis='y', alpha=0.5)
    if runtime:
        buf = BytesIO()
        fig.savefig(buf, format=extension, bbox_inches='tight')
        plt.close()
        image_string = base64.b64encode(buf.getvalue()).decode('ascii')
        return image_string
    else:
        fig.savefig("{}/{}.{}".format(PLOT_PATH, filename, extension), bbox_inches='tight')
        plt.close()


def plot_hist(variable, filename, extension='png', bins=50, xlabel='', ylabel='', range=(), legend_name=''):
    """saves hist image for a given variable"""

    fig = plt.figure(figsize=(15, 10))
    if len(range) == 2:
        plt.hist(variable, bins=bins, range=range)
    else:
        plt.hist(variable, bins=bins)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(axis='y', alpha=0.5)
    if legend_name:
        plt.legend(legend_name)
    fig.savefig("{}/{}.{}".format(PLOT_PATH, filename, extension), bbox_inches='tight')
    plt.close()


def plot_bar(x, data, filename, extension='png', ylabel='Load [kW]', legend_name=(), xlabel='', threshold=0):
    """saves image with plots from each column in Dataframe"""

    fig = plt.figure(figsize=(30, 10))
    data = data if isinstance(data, list) else [data]
    # plot time series voltage
    for d in data:
        plt.bar(x, d)
    plt.xticks(rotation=90, fontsize=5)
    plt.ylabel(ylabel)
    if xlabel:
        plt.xlabel(xlabel)
    if len(legend_name) > 0:
        plt.legend(legend_name)
    if threshold:
        plt.axhline(threshold, color='red', lw=2)
    plt.grid(axis='y', alpha=0.5)
    fig.savefig("{}/{}.{}".format(PLOT_PATH, filename, extension), bbox_inches='tight')
    plt.close()
