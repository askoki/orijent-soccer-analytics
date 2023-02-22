import matplotlib as mpl
import matplotlib.pyplot as plt
from typing import Tuple, List
from pages.helpers.constants import RPE_LEGEND_LIST
from pages.rpe.rpe_helpers import define_RPE_colors


def create_rpe_bar_plot(
        figsize: Tuple,
        title: str,
        x_label: str,
        y_label: str,
        x_values: list,
        y_values: list,
        y_err=None
) -> plt.Figure:
    mpl.style.use('classic')
    fig, ax = plt.subplots(figsize=figsize, nrows=1, ncols=1)
    fig.suptitle(title, fontsize=20, weight='bold')
    facecolor = "white"
    fig.set_facecolor(facecolor)

    colors = define_RPE_colors(y_values)
    ax.bar(
        x_values,
        y_values,
        yerr=y_err,
        align='center',
        color=colors,
        width=0.6,
        label='RPE',
        capsize=6
    )
    for x, y in zip(x_values, y_values):
        ax.text(x, y + 0.1, f'{y}', ha='center', va='bottom', fontsize=12)

    x_tick_labels, y_tick_labels = ax.get_xticklabels(), ax.get_yticklabels()
    for x_tick_label in x_tick_labels:
        x_tick_label.set_fontweight('bold')
    for y_tick_label in y_tick_labels:
        y_tick_label.set_fontweight('bold')
        y_tick_label.set_fontsize(14)

    ax.set_ylabel(y_label, fontsize=18, weight='bold')
    ax.set_xlabel(x_label, fontsize=18, weight='bold')
    ax.set_ylim(ymin=0, ymax=10)
    ax.set_facecolor(facecolor)
    plt.xticks(rotation=90)

    ax.legend(
        handles=RPE_LEGEND_LIST, loc='upper center',
        bbox_to_anchor=(0.5, 1.07), ncol=3, fancybox=True, shadow=True,
        prop={'size': 12}
    )
    return fig


def get_colors_and_percentages(session_values: list, max_values: list, inverse_colors=False) -> Tuple[
    List[str], List[int]]:
    colors = []
    percentages = []

    COLOR_DICT = {
        'low': 'tomato',
        'neutral': 'steelblue',
        'high': 'forestgreen'
    }
    if inverse_colors:
        COLOR_DICT['low'] = 'forestgreen'
        COLOR_DICT['high'] = 'tomato'

    for val, max_v in zip(session_values, max_values):
        percentage = int(val / max_v * 100)
        LOW = 40
        HIGH = 80
        if percentage < LOW:
            color = COLOR_DICT['low']
        elif LOW < percentage < HIGH:
            color = 'steelblue'
        else:
            color = COLOR_DICT['high']
        colors.append(color)
        percentages.append(percentage)
    return colors, percentages
