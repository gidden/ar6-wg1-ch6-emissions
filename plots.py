import pandas as pd
import pyam
import matplotlib.pyplot as plt
import numpy as np
import copy

from utils import oecd, chn, asia, afr, lam

PLOT_KWARGS = {'lw': 3}

pyam.run_control().update('./plotting.yaml')
legend = dict(loc='center left', bbox_to_anchor=(1.0, 0.5), prop={'size': 16})

regions = [oecd, chn, asia, afr, lam]  # as specified by zig

# gas order
gases = ['CH4', 'BC', 'OC', 'Sulfur', 'NOx', 'CO', 'VOC', 'NH3']
units = ['Tg CH4/yr', 'Tg C/yr', 'Tg C/yr', 'Tg SO2/yr', 'Tg NO2/yr',
         'Tg CO/yr', 'Tg NMVOC/yr', 'Tg NH3/yr']

# for region plots..
ylims = [
    (0, 275),
    (0, 3.8),
    (0, 14),
    (0, 100),
    (0, 72),
    (0, 400),
    (0, 90),
    (0, 50),
]
rescale_ylim = {}
for gas in gases:
    rescale_ylim[(gas, lam)] = 2
rescale_ylim[('Sulfur', lam)] = 4
for region in [chn, asia, afr]:
    rescale_ylim[('Sulfur', region)] = 2


rename = {
    'Sulfur': 'SO2',
    'VOC': 'NMVOC'
}

#
# world data
#
wdf = pyam.IamDataFrame('./ar6-wg1-ch6-emissions-global-data.csv')

#
# regional data
#
rdf = pyam.IamDataFrame('./ar6-wg1-ch6-emissions-regional-data.csv')


def plot(df, gas, ax=None, legend=legend):
    print(gas)
    if ax is None:
        fig, ax = plt.subplots()

    variable = 'Emissions|' + gas
    df = df.filter(variable=variable)

    (df
     .filter(model='History', scenario='CMIP6')
     .line_plot(ax=ax, color='ssp-type', linestyle='type', legend=False, **PLOT_KWARGS)
     )

    (df
     .filter(model='History', scenario='CMIP5')
     .line_plot(ax=ax, color='ssp-type', linestyle='type', legend=False, **PLOT_KWARGS)
     )

    (df
     .filter(scenario='RCP*')
     .line_plot(ax=ax, alpha=0.0, color='ssp-type', fill_between=True, legend=False, **PLOT_KWARGS)
     )

    (df
     .filter(model='History', keep=False)
     .filter(scenario='RCP*', keep=False)
     .line_plot(ax=ax, color='ssp-type', linestyle='type', legend=legend, **PLOT_KWARGS)
     )

    return ax


def _plot_global_only(df, gas, unit, ax, fontsize=16):
    plot(df, gas, ax=ax, legend=False)
    gas = rename[gas] if gas in rename else gas
    ax.set_ylabel(unit, fontsize=fontsize)
    ax.set_xlabel('')
    ax.set_ylim([0, None])
    ax.set_title(gas, fontsize=fontsize)
    ax.tick_params(axis='both', which='major', labelsize=fontsize)


def plot_global_only():
    fig, axs = plt.subplots(3, 3, figsize=(5 * 3, 5 * 3))
    axs = np.ravel(axs)

    for i, (ax, gas) in enumerate(zip(axs, gases)):
        _plot_global_only(wdf, gas, units[i], ax)

    axs[-1].set_axis_off()
    fig.tight_layout()
    fig.savefig('global_only.png', bbox_inches='tight')


def add_region_title(ax, region, **kwargs):
    if len(region) > len('Central and South America'):
        split = region.split()
        region = ' '.join(split[:len(split) // 2]) + \
            '\n' + ' '.join(split[len(split) // 2:])
    ax.set_title(region, **kwargs)


def _plot_region_only(df, region, gas, ax, with_ylims=False, title=True, ylabel=True,
                      annotate=dict(
                          xy=(0.05, 0.85), xytext=(0.05, 0.85),
                          xycoords='axes fraction', textcoords='axes fraction'
                      )):
    fontsize = 20
    annotate = {**annotate, **dict(fontsize=fontsize)}
    i = gases.index(gas)
    plot(df.filter(region=region), gas=gas, legend=False, ax=ax)
    if title:
        add_region_title(ax, region, fontsize=fontsize * 1.1)
    else:
        ax.set_title('')
    if with_ylims:
        f = 1 if (
            gas, region) not in rescale_ylim else rescale_ylim[(gas, region)]
        ylim = ylims[i][0], ylims[i][1] / f
        ax.set_ylim(ylim)
    else:
        ax.set_ylim([0, None])
    ax.set_xlabel('')
    if region == regions[0] and ylabel:
        label = rename[gas] if gas in rename else gas
        ax.set_ylabel('{} ({})'.format(label, units[i]), fontsize=fontsize)
    else:
        ax.set_ylabel('')
    ax.tick_params(axis='both', which='major', labelsize=fontsize)
    if with_ylims and f != 1:
        print('adding annotation', gas, region, f, annotate, ax)
        ax.annotate('Scale: 1/{}x'.format(f), **annotate)


def plot_region_only(with_ylims=False):
    nx = len(regions)
    ny = len(gases)
    fig, _axs = plt.subplots(ny, nx, figsize=(5 * nx, 4 * ny))

    for i, (axs, gas) in enumerate(zip(_axs, gases)):
        for ax, region in zip(axs, regions):
            title = gas == gases[0]
            _plot_region_only(rdf, region, gas, ax,
                              with_ylims=with_ylims, title=title)

    fig.tight_layout()
    fig.savefig('region_only.png', bbox_inches='tight')


def _unique_handles_lables(ax):
    handles, labels = ax.get_legend_handles_labels()
    handles, labels = np.array(handles), np.array(labels)
    _, idx = np.unique(labels, return_index=True)
    return handles[idx], labels[idx]


def plot_global_and_regions(_gases, save_kind):
    n = len(_gases)
    # TODO change 6 to 7 when new region introduced
    nreg = 6
    fig, _axs = plt.subplots(n, nreg, figsize=(5 * nreg, 5 * n))
    fontsize = 20

    for gas, axs in zip(_gases, _axs):
        ax = axs[0]
        unit = units[gases.index(gas)]
        _plot_global_only(wdf, gas, unit, ax)
        title = 'Global' if gas == _gases[0] else ''
        ax.set_title(title, fontsize=1.1 * fontsize)
        label = rename[gas] if gas in rename else gas
        ax.set_ylabel('{} ({})'.format(label, unit), fontsize=fontsize)
        ax.tick_params(axis='both', which='major', labelsize=fontsize)
        for region, ax in zip(regions, axs[1:]):
            title = gas == _gases[0]
            _plot_region_only(
                rdf, region, gas, ax, with_ylims=True, title=title, ylabel=False)
            plt.tight_layout()
    fig.savefig('global_and_regions_{}.png'.format(
        save_kind), bbox_inches='tight')


def make_legends():
    gas = gases[0]
    region = regions[0]

    fig, ax = plt.subplots()
    _legend = dict(loc='center left', bbox_to_anchor=(
        1.1, 0.5), prop={'size': 16})
    plot(wdf, gas, ax=ax, legend=copy.copy(_legend))
    handles, labels = _unique_handles_lables(ax)
    labels = [l if 'SSP' not in l else l.split()[0] for l in labels]
    ax.legend(handles, labels, **_legend)
    fig.savefig('global_legend.png', bbox_inches='tight')

    fig, ax = plt.subplots()
    data = rdf.filter(variable='Emissions|' + gas, region=region)
    _legend = dict(loc='upper center', bbox_to_anchor=(
        0.5, -0.2), ncol=4, prop={'size': 16})
    plot(rdf.filter(region=region), gas=gas, ax=ax, legend=copy.copy(_legend))
    handles, labels = _unique_handles_lables(ax)
    labels = [l if 'SSP' not in l else l.split()[0] for l in labels]
    ax.legend(handles, labels, **_legend)
    fig.savefig('region_legend.png', bbox_inches='tight')


if __name__ == '__main__':
    # plot_global_only()
    # plot_region_only(with_ylims=True)
    make_legends()

    _gases = ['Sulfur', 'BC', 'OC', 'NH3']
    save_kind = '6_3_a'
    plot_global_and_regions(_gases, save_kind)

    _gases = ['CH4', 'NOx', 'VOC', 'CO']
    save_kind = '6_3_b'
    plot_global_and_regions(_gases, save_kind)
