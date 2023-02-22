import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from typing import Tuple
from datetime import timedelta

from pages.gps_relative.gps_relative_helpers import extract_max_features
from pages.helpers.constants import FEATURES_2_EXTRACT, RELATIVE_PARAMS_2_EXTRACT, GPS_RELATIVE_PLOT_FILL_DESIGN
from pages.rpe.rpe_plots import get_colors_and_percentages


def create_gps_single_session_plot(
        players: np.array,
        session_df: pd.DataFrame,
        whole_df: pd.DataFrame,
) -> plt.Figure:
    num_columns = 4
    num_players = players.shape[0]
    plt.style.use('dark_background')
    fig, axs = plt.subplots(figsize=(30, 20 + num_players), nrows=2, ncols=num_columns)
    facecolor = "#00001a"
    fig.set_facecolor(facecolor)

    session_date = session_df.date_time.iloc[0]
    fig.suptitle(f'Session report {session_date}', fontsize=30, weight='bold')

    ax_count = 0
    for param, ax in zip(FEATURES_2_EXTRACT, axs.reshape(-1)):
        max_features = extract_max_features(whole_df, players, param)
        ax.set_xticks([], [])
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
        ax.set_frame_on(False)
        ax.set_title(param, fontsize=25)
    return fig


ACCELERATION_PLOT_INDEX = 3
MPE_PLOT_INDEX = 5


def pick_x_values_single_relative_plot(relative_df: pd.DataFrame, plot_index: int) -> np.array:
    x_values = pd.to_datetime(relative_df.date)
    time_offset = 4
    minute_offset = 50

    if plot_index == ACCELERATION_PLOT_INDEX:
        x_values -= timedelta(hours=time_offset, minutes=minute_offset)
    elif plot_index == MPE_PLOT_INDEX:
        x_values += timedelta(hours=time_offset, minutes=minute_offset)
    return x_values


def pick_x_values_week_relative_plot(relative_df: pd.DataFrame, plot_index: int) -> np.array:
    x_values = relative_df.week.values.copy()
    x_offset = 0.2

    if plot_index == ACCELERATION_PLOT_INDEX:
        x_values -= x_offset
    elif plot_index == MPE_PLOT_INDEX:
        x_values += x_offset
    return x_values


def create_gps_relative_plot(
        title: str,
        x_label: str,
        y_label: str,
        relative_df: pd.DataFrame,
        is_week=False
) -> Tuple[plt.Figure, plt.Axes]:
    mpl.style.use('classic')
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.suptitle(title, fontsize=30, weight='bold')
    facecolor = "white"
    fig.set_facecolor(facecolor)

    bottom = None

    for i, param in enumerate(RELATIVE_PARAMS_2_EXTRACT):
        color, fill, hatch, width = GPS_RELATIVE_PLOT_FILL_DESIGN[i]
        if is_week:
            x_values = pick_x_values_week_relative_plot(relative_df, i)
        else:
            x_values = pick_x_values_single_relative_plot(relative_df, i)
        ax.bar(
            x_values,
            relative_df[param],
            width=width,
            label=param,
            bottom=bottom,
            color=color,
            fill=fill,
            hatch=hatch,
        )
        if param == RELATIVE_PARAMS_2_EXTRACT[0]:
            bottom = relative_df[param].values.copy()
        elif i < ACCELERATION_PLOT_INDEX:
            bottom += relative_df[param].values

    if is_week:
        ax.set_ylim(ymin=0, ymax=10)
    else:
        ax.set_ylim(ymin=0, ymax=3)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))

    x_tick_labels, y_tick_labels = ax.get_xticklabels(), ax.get_yticklabels()
    for x_tick_label in x_tick_labels:
        x_tick_label.set_fontsize(12)
    for y_tick_label in y_tick_labels:
        y_tick_label.set_fontsize(12)

    ax.set_ylabel(y_label, fontsize=16, weight='bold')
    ax.set_xlabel(x_label, fontsize=16, weight='bold')

    ax.legend(
        loc='upper center', labels=RELATIVE_PARAMS_2_EXTRACT,
        bbox_to_anchor=(0.5, 1.05), ncol=3, fancybox=True, shadow=True,
        fontsize=14
    )
    return fig, ax
