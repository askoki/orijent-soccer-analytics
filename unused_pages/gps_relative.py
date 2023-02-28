import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from matplotlib.ticker import MaxNLocator
from pages.helpers.constants import FEATURES_2_EXTRACT, RELATIVE_PARAMS_2_EXTRACT
from pages.gps_relative.gps_relative_plots import create_gps_single_session_plot, create_gps_relative_plot
from pages.helpers.utils import authenticate, load_google_drive_data, add_download_image_button, add_page_logo

add_page_logo()
status = authenticate()
if status:
    df = load_google_drive_data()
    # ------------------------------------------------------
    st.title("GPS single session")
    session_dates = df.sort_values('date_time', ascending=False).date_time.unique()
    session_date = st.selectbox('Select session date', session_dates, index=0)

    session_df = df[df.date_time == session_date]
    session_df.reset_index(inplace=True, drop=True)

    for col in FEATURES_2_EXTRACT:
        session_df[col] = session_df[col].astype(float)

    players = session_df.athlete.unique()
    fig = create_gps_single_session_plot(
        players=players,
        session_df=session_df,
        whole_df=df
    )
    fig.text(0.92, 0.1, "Created by Arian Skoki", ha="center", fontsize=18, weight='bold')
    st.pyplot(fig)
    add_download_image_button(
        fig,
        "Download session GPS report",
        f'session_report_{session_date}.png'
    )
    # ------------------------------------------------------
    st.title("GPS relative session")
    st.subheader("For trainings on the same date a mean value is taken.")
    cols_2_keep = [
        'date_time',
        'tot_dist', 'hsr_dist', 'sprint_dist', 'mpe',
        'acc_num', 'dec_num',
        'athlete', 'is_match'
    ]
    df = df.rename(columns={
        'total_distance': 'tot_dist',
        'mpe_count': 'mpe',
        'acc_events': 'acc_num',
        'dec_events': 'dec_num',
    })
    f_df = df[cols_2_keep]
    f_df.loc[:, 'date'] = pd.to_datetime(f_df.date_time).dt.date
    f_df.loc[:, 'week'] = f_df.date.apply(lambda r: r.isocalendar()[1])
    f_df.loc[:, 'year'] = f_df.date.apply(lambda r: r.isocalendar()[0])

    start_offset_days = 7
    session_dates = f_df.sort_values('date', ascending=False).date.unique()
    start_index = start_offset_days if len(session_dates) <= start_offset_days else len(session_dates)
    session_start_date = st.selectbox('Select start date', session_dates, index=start_offset_days)
    session_end_date = st.selectbox('Select end date', session_dates, index=0)

    f_df = f_df[
        (f_df.date >= session_start_date) &
        (f_df.date <= session_end_date)
        ]
    rel_date_df = f_df.drop(columns=['is_match', 'year', 'athlete']).groupby('date', as_index=False).agg(np.mean)
    rel_date_df = rel_date_df.round(2)

    start_date_obj = datetime.strptime(str(rel_date_df.date.iloc[0]), '%Y-%m-%d')
    end_date_obj = datetime.strptime(str(rel_date_df.date.iloc[-1]), '%Y-%m-%d')

    idx = pd.date_range(start_date_obj, end_date_obj)
    rel_date_df.index = pd.DatetimeIndex(rel_date_df.date)
    rel_date_df = rel_date_df.drop(columns=['date'])
    rel_date_df = rel_date_df.reindex(idx, fill_value=0)
    rel_date_df = rel_date_df.reset_index().rename(columns={'index': 'date'})
    rel_date_df.loc[:, 'date'] = pd.to_datetime(rel_date_df.date).dt.date

    ref_df = pd.DataFrame(index=[0])
    for param in RELATIVE_PARAMS_2_EXTRACT:
        best5_df = df.sort_values(param, ascending=False)[param][:5]
        ref_df.loc[:, param] = best5_df.mean()

    relative_df = rel_date_df.copy()
    for param in RELATIVE_PARAMS_2_EXTRACT:
        relative_df.loc[:, param] /= ref_df.loc[:, param].values
    relative_df = relative_df.round(2)

    fig, ax = create_gps_relative_plot(
        title='Relative session report',
        x_label='Dates',
        y_label='Game Reference',
        relative_df=relative_df
    )
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
    ax.xaxis.set_major_locator(mdates.DayLocator())
    plt.xticks(rotation=15)
    plt.figtext(0.82, 0.01, "Created by Arian Skoki", ha="center", fontsize=14, weight='bold')
    st.pyplot(fig)
    add_download_image_button(
        fig,
        "Download relative GPS report",
        f'relative_report_{session_start_date}_{session_end_date}.png'
    )
    # -------------------------------------
    st.title('GPS relative week')
    day_mean_df = f_df.drop(columns=['is_match', 'year', 'athlete']).groupby('date', as_index=False).agg(np.mean)
    week_df = day_mean_df.groupby('week', as_index=False).agg(np.sum)
    week_df = week_df.round(2)

    relative_week_df = week_df.copy()
    for param in RELATIVE_PARAMS_2_EXTRACT:
        relative_week_df.loc[:, param] /= ref_df.loc[:, param].values
    relative_week_df = relative_week_df.round(2)

    fig, ax = create_gps_relative_plot(
        title='Relative week report',
        x_label='Weeks',
        y_label='Game Reference',
        relative_df=relative_week_df,
        is_week=True
    )
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.xticks(rotation=15)
    plt.figtext(0.82, 0.01, "Created by Arian Skoki", ha="center", fontsize=14, weight='bold')
    st.pyplot(fig)
    add_download_image_button(
        fig,
        "Download relative weekly GPS report",
        f'relative_weekly_report_{session_start_date}_{session_end_date}.png'
    )

    st.sidebar.success("Select a page above.")
