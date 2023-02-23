import numpy as np
import pandas as pd
import streamlit as st
import matplotlib as mpl
from pages.gps_absolute.gps_absolute_plots import draw_hsr_sprint_plot, draw_mpe_max_sprint, draw_mpe_p_avg_rec_t, \
    draw_distance_duration
from pages.helpers.utils import authenticate, load_google_drive_data, add_download_image_button, add_page_logo, \
    add_download_pdf_from_plots_button

add_page_logo()
status = authenticate()
if status:
    mpl.style.use('ggplot')
    df = load_google_drive_data()
    st.title("GPS single session")
    st.header("Individual Analysis")

    cols_2_keep = [
        'date_time', 'athlete', 'duration_min', 'total_distance',
        'mpe_count', 'acc_events', 'dec_events', 'hsr_dist', 'sprint_dist',
        'avg_speed_(kmh)', 'avg_hr_(bmin)', 'avg_hrr%_(%)',
        'max_speed_km_h', 'max_acc_(ms²)',
        'max_dec_(ms²)', 'max_hr_(bmin)', 'max_hrr%_(%)',
        'avg_met_power_(wkg)', 'energy', 'an_energy',
        'mpe_avg_time_(s)', 'mpe_avg_power',
        'mpe_avg_rec_time', 'mpe_rec_avg_power_(wkg)',
        'speed_events', 'impacts', 'jumps', 'is_match',
    ]
    # This is different order than relative analysis
    f_df = df[cols_2_keep]
    f_df = f_df.rename(columns={
        'total_distance': 'tot_dist',
        'mpe_count': 'mpe',
        'acc_events': 'acc_num',
        'dec_events': 'dec_num',
    })

    f_df.loc[:, 'date'] = pd.to_datetime(f_df.date_time).dt.date
    f_df.loc[:, 'week'] = f_df.date.apply(lambda r: r.isocalendar()[1])
    f_df.loc[:, 'year'] = f_df.date.apply(lambda r: r.isocalendar()[0])

    st.header('Player session analysis')
    start_offset_days = 7
    session_dates = f_df.sort_values('date', ascending=False).date.unique()
    start_index = start_offset_days if len(session_dates) <= start_offset_days else len(session_dates)
    session_start_date = st.selectbox('Select start date', session_dates, index=start_offset_days)
    session_end_date = st.selectbox('Select end date', session_dates, index=0)

    select_players = f_df.athlete.unique()
    selected_player = st.selectbox('Select athlete to watch', select_players, index=len(select_players) - 1)

    player_df = f_df[
        (f_df.date >= session_start_date) &
        (f_df.date <= session_end_date) &
        (f_df.athlete == selected_player)
        ]
    fig_run, ax_run = draw_hsr_sprint_plot(player_df)
    fig_run.suptitle(selected_player)
    st.pyplot(fig_run)

    fig_mpe_s, ax1_mpe_s, ax2_mpe_s = draw_mpe_max_sprint(player_df)
    fig_mpe_s.suptitle(selected_player)
    st.pyplot(fig_mpe_s)

    fig_mpe_p, ax1_mpe_p, ax2_mpe_p = draw_mpe_p_avg_rec_t(player_df)
    fig_mpe_p.suptitle(selected_player)
    st.pyplot(fig_mpe_p)

    fig_dist_dur, ax1_dist_dur, ax2_dist_dur = draw_distance_duration(player_df)
    fig_dist_dur.suptitle(selected_player)
    st.pyplot(fig_dist_dur)

    add_download_pdf_from_plots_button(
        'Download player pdf report',
        f'{selected_player}_performance.pdf'
    )
    # -----------------------------------
    # st.header('Player week analysis')
    #
    # player_week_df = f_df[
    #     (f_df.date >= session_start_date) &
    #     (f_df.date <= session_end_date) &
    #     (f_df.athlete == selected_player)
    #     ]
    # player_week_df = player_week_df.drop(columns=['is_match', 'athlete'])
    # player_week_df = player_week_df.groupby(['week']).agg(np.sum).reset_index()
    #
    # fig_run, ax_run = draw_hsr_sprint_plot(player_week_df, x_label='Weeks', x_param='week')
    # fig_run.suptitle(selected_player)
    # st.pyplot(fig_run)
    #
    # fig_mpe_s, ax1_mpe_s, ax2_mpe_s = draw_mpe_max_sprint(
    #     player_week_df, x_label='Weeks', y_label='Weeks', x_param='week'
    # )
    # fig_mpe_s.suptitle(selected_player)
    # st.pyplot(fig_mpe_s)
    #
    # fig_mpe_p, ax1_mpe_p, ax2_mpe_p = draw_mpe_p_avg_rec_t(
    #     player_week_df, x_label='Weeks', y_label='Weeks', x_param='week'
    # )
    # fig_mpe_p.suptitle(selected_player)
    # st.pyplot(fig_mpe_p)
    #
    # fig_dist_dur, ax1_dist_dur, ax2_dist_dur = draw_distance_duration(
    #     player_week_df, x_label='Weeks', y_label='Weeks', x_param='week'
    # )
    # fig_dist_dur.suptitle(selected_player)
    # st.pyplot(fig_dist_dur)
    #
    # add_download_pdf_from_plots_button(
    #     'Download player week report pdf',
    #     f'{selected_player}_week_performance.pdf'
    # )

    # -------------------------------------
    st.header('Team analysis')
    st.text('Show values are calulated by taking a team mean for every date.')
    team_start_date = st.selectbox('Select start date', session_dates, index=start_offset_days, key='team_key_start')
    team_end_date = st.selectbox('Select end date', session_dates, index=0, key='team_key_end')

    session_df = f_df[
        (f_df.date >= team_start_date) &
        (f_df.date <= team_end_date)
        ]
    team_df = session_df.groupby('date').agg({
        'duration_min': 'mean',
        'athlete': 'count',
        'tot_dist': 'mean',
        'max_speed_km_h': 'mean',
        'mpe': 'mean',
        'acc_num': 'mean',
        'dec_num': 'mean',
        'energy': 'mean',
        'an_energy': 'mean',
        'mpe_avg_power': 'mean',
        'mpe_avg_rec_time': 'mean',
        'hsr_dist': 'mean',
        'sprint_dist': 'mean',
        'is_match': 'first'
    })
    team_df = team_df.reset_index()
    team_df = team_df.fillna(0)

    team_title = f'Team {team_start_date}_{team_end_date}'
    fig_run, ax_run = draw_hsr_sprint_plot(team_df)
    fig_run.suptitle(team_title)
    st.pyplot(fig_run)

    fig_mpe_s, ax1_mpe_s, ax2_mpe_s = draw_mpe_max_sprint(team_df)
    fig_mpe_s.suptitle(team_title)
    st.pyplot(fig_mpe_s)

    fig_mpe_p, ax1_mpe_p, ax2_mpe_p = draw_mpe_p_avg_rec_t(team_df)
    fig_mpe_p.suptitle(team_title)
    st.pyplot(fig_mpe_p)

    fig_dist_dur, ax1_dist_dur, ax2_dist_dur = draw_distance_duration(team_df)
    fig_dist_dur.suptitle(team_title)
    st.pyplot(fig_dist_dur)

    add_download_pdf_from_plots_button(
        'Download team pdf report',
        f'Team_performance_{team_start_date}_{team_end_date}.pdf'
    )
