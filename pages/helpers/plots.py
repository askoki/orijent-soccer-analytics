from typing import Tuple, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from pages.helpers.constants import FEATURES_2_EXTRACT, RPE_LEGEND_LIST
from pages.homepage.homepage_helpers import extract_max_features
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
    fig, ax = plt.subplots(figsize=figsize, nrows=1, ncols=1)
    fig.suptitle(title, fontsize=30, weight='bold')
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


def create_gps_relative_plot(
        players: np.array,
        session_df: pd.DataFrame,
        whole_df: pd.DataFrame,
) -> plt.Figure:
    num_columns = 4
    num_players = players.shape[0]
    fig, axs = plt.subplots(figsize=(30, 20 + num_players), nrows=2, ncols=num_columns)
    TEXT_COLOR = 'lightgrey'
    plt.rcParams['text.color'] = TEXT_COLOR
    plt.rcParams['axes.labelcolor'] = TEXT_COLOR
    plt.rcParams['xtick.color'] = TEXT_COLOR
    plt.rcParams['ytick.color'] = TEXT_COLOR
    facecolor = "#00001a"
    fig.set_facecolor(facecolor)

    session_date = session_df.date_time.iloc[0]
    fig.suptitle(f'Session report {session_date}', fontsize=30, weight='bold')

    ax_count = 0
    for param, ax in zip(FEATURES_2_EXTRACT, axs.reshape(-1)):
        max_features = extract_max_features(whole_df, players, param)
        ax.set_xticks([], [])
        separation_factor = 2
        session_param_values = session_df[param].values
        is_inverse = True if param == 'mpe_avg_rec_time' else False
        colors, percentages = get_colors_and_percentages(session_param_values, max_features, inverse_colors=is_inverse)
        ax.barh(players, max_features, align='center', color='gray', height=0.6, label='Max')
        ax.barh(players, session_param_values, align='center', color=colors, height=0.4, label='Session')

        for cnt, info in enumerate(zip(session_param_values, percentages)):
            value, percentage = info
            ax.text(y=cnt - 0.1, x=value / 2, s=f'{percentage}%', fontsize=15)

        ax.yaxis.set_tick_params(labelsize=20)
        ax.xaxis.set_tick_params(labelsize=20)

        y_tick_labels = ax.get_yticklabels()
        for y_tick_label in y_tick_labels:
            y_tick_label.set_fontweight('bold')

        if ax_count % num_columns != 0:
            ax.axes.yaxis.set_ticklabels([])
        ax_count += 1
        ax.set_facecolor(facecolor)
        ax.set_title(param, fontsize=25)
    return fig
