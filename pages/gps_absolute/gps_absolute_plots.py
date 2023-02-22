import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from typing import Tuple
from collections import namedtuple

AxisLabels = Tuple[str, str]
PlotLabels = Tuple[str, str]
DataFrameParameters = Tuple[str, str]
PlotColors = Tuple[str, str]

Limits = Tuple[int, int]
LimitsDoubleAxis = namedtuple('Limits', ['ax1_y_lim', 'ax2_y_lim'])
MPE_EVENTS_COLOR = '#2f4b7c'
MAX_SPEED_COLOR = 'skyblue'

MPE_P_COLOR = 'tomato'
MPE_REC_T_COLOR = 'darkred'

DISTANCE_COLOR = '#a05195'
DURATION_COLOR = '#f95d6a'


def draw_2axis_plot(df: pd.DataFrame, labels1: AxisLabels, labels2: AxisLabels, plot_label: PlotLabels,
                    df_params: DataFrameParameters, colors: PlotColors, limits: LimitsDoubleAxis):
    x = np.arange(len(df.date))
    width = 0.35

    mpl.style.use('ggplot')
    fig, ax1 = plt.subplots(figsize=(6, 4))
    ax2 = ax1.twinx()

    ax1_color = colors[0]
    ax2_color = colors[1]

    param1 = df_params[0]
    param2 = df_params[1]

    ax1.bar(x, df[param1], width=width, color=ax1_color, label=plot_label[0])
    ax2.plot(x, df[param2], marker='o', color=ax2_color, label=plot_label[1])

    for pos_x, pos_y in zip(x, df[param2]):
        ax2.text(pos_x, pos_y + 1, str(round(pos_y, 1)), color='black')

    ax1.set_xlabel(labels1[0])
    ax1.set_ylabel(labels1[1])
    ax1.yaxis.label.set_color(ax1_color)

    ax2.set_xlabel(labels2[0])
    ax2.set_ylabel(labels2[1])
    ax2.yaxis.label.set_color(ax2_color)

    ax1.set_xticks(x)
    ax1.set_xticklabels(df.date, rotation=45)

    ax1.set_ylim(limits.ax1_y_lim)
    ax2.set_ylim(limits.ax2_y_lim)

    ax1.grid(True)
    ax2.grid(False)

    fig.legend()
    plt.tight_layout()
    return fig, ax1, ax2


def draw_double_bar_plot(df: pd.DataFrame, labels: AxisLabels, plot_label: PlotLabels, df_params: DataFrameParameters,
                         colors: PlotColors, limits: Limits):
    x = np.arange(len(df.date))
    width = 0.35

    param1 = df_params[0]
    param2 = df_params[1]

    ax1_color = colors[0]
    ax2_color = colors[1]

    mpl.style.use('ggplot')
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(x - width / 2, df[param1], width=width, color=ax1_color, label=plot_label[0])
    ax.bar(x + width / 2, df[param2], width=width, color=ax2_color, label=plot_label[1])

    ax.set_xlabel(labels[0])
    ax.set_ylabel(labels[1])

    ax.set_ylim(limits)

    ax.set_xticks(x)
    ax.set_xticklabels(df.date, rotation=45)
    plt.legend()
    plt.tight_layout()
    return fig, ax


MatplotlibFigureAxis = Tuple[plt.Figure, plt.Axes]
MatplotlibFigureDoubleAxis = Tuple[plt.Figure, plt.Axes, plt.Axes]

HSR_SPRINT_LIMITS = (0, 800)
MPE_MAX_SPEED_LIMITS = LimitsDoubleAxis((0, 200), (0, 40))
MPE_POWER_REC_TIME_LIMITS = LimitsDoubleAxis((0, 30), (0, 100))
TOTAL_DISTANCE_DURATION_LIMITS = LimitsDoubleAxis((0, 15000), (0, 120))
RPE_SRPE_LIMITS = LimitsDoubleAxis((0, 10), (0, 1200))


def draw_hsr_sprint_plot(player_df: pd.DataFrame) -> MatplotlibFigureAxis:
    return draw_double_bar_plot(
        player_df,
        ('Dates', 'Distance (m)'),
        ('HSR', 'Sprint'),
        ('hsr_dist', 'sprint_dist'),
        (None, None),
        HSR_SPRINT_LIMITS
    )


def draw_mpe_max_sprint(player_df: pd.DataFrame) -> MatplotlibFigureDoubleAxis:
    return draw_2axis_plot(
        player_df,
        ('Dates', 'MPE count'),
        ('Dates', 'Max speed (km/h)'),
        ('MPE events', 'Max speed (km/h)'),
        ('mpe', 'max_speed_km_h'),
        (MPE_EVENTS_COLOR, MAX_SPEED_COLOR),
        MPE_MAX_SPEED_LIMITS
    )


def draw_mpe_p_avg_rec_t(player_df: pd.DataFrame) -> MatplotlibFigureDoubleAxis:
    return draw_2axis_plot(
        player_df,
        ('Dates', 'MPE avg power (W)'),
        ('Dates', 'MPE avg rec time (s)'),
        ('MPE avg power', 'MPE avg rec time'),
        ('mpe_avg_power', 'mpe_avg_rec_time'),
        (MPE_P_COLOR, MPE_REC_T_COLOR),
        MPE_POWER_REC_TIME_LIMITS
    )


def draw_distance_duration(player_df: pd.DataFrame) -> MatplotlibFigureDoubleAxis:
    return draw_2axis_plot(
        player_df,
        ('Dates', 'Distance (m)'),
        ('Dates', 'Duration (min)'),
        ('Distance', 'Duration'),
        ('tot_dist', 'duration_min'),
        (DISTANCE_COLOR, DURATION_COLOR),
        TOTAL_DISTANCE_DURATION_LIMITS
    )
