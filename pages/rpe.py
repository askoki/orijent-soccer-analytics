import streamlit as st
import gspread
import cyrtranslit
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from oauth2client.service_account import ServiceAccountCredentials

import pandas as pd

from helpers import authenticate
from pages.rpe.constants import RPE1_COLOR, RPE23_COLOR, RPE46_COLOR, RPE78_COLOR, RPE9_COLOR, RPE10_COLOR
from pages.rpe.helpers import get_rpe_questioneer_df, extract_players_rpe_mean_and_std, define_RPE_colors

st.title("RPE")

status = authenticate()

if status:
    # Use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict({
        "type": st.secrets.google_api.type,
        "project_id": st.secrets.google_api.project_id,
        "private_key_id": st.secrets.google_api.private_key_id,
        "private_key": st.secrets.google_api.private_key,
        "client_email": st.secrets.google_api.client_email,
        "client_id": st.secrets.google_api.client_id,
        "auth_uri": st.secrets.google_api.auth_uri,
        "token_uri": st.secrets.google_api.token_uri,
        "auth_provider_x509_cert_url": st.secrets.google_api.auth_provider_x509_cert_url,
        "client_x509_cert_url": st.secrets.google_api.client_x509_cert_url,
    }, scope)
    client = gspread.authorize(creds)

    # Open the Google Sheets document
    sheet = client.open('NN RPE').sheet1

    rpe_df = get_rpe_questioneer_df(worksheet=sheet)
    rpe_df = rpe_df.drop(columns=[
        'response_id', 'ip_addr', 'duration_sec',
    ], errors='ignore')
    rpe_df = rpe_df.sort_values('session_date').drop_duplicates(['session_date', 'name'], keep='last')
    rpe_df.timestamp = pd.to_datetime(rpe_df.timestamp, unit='ns', utc=False).dt.tz_localize(None)

    rpe_df.loc[:, 'name'] = rpe_df.name.apply(lambda r: cyrtranslit.to_latin(r, "ru") if r else r)
    rpe_df.session_date = pd.to_datetime(rpe_df.session_date).dt.date
    rpe_df.rpe = rpe_df.loc[:, 'rpe'].astype(int)

    session_dates = rpe_df.sort_values('session_date').session_date.unique()
    session_date = st.sidebar.selectbox('Select training date', session_dates, index=len(session_dates) - 1)

    session_df = rpe_df[rpe_df.session_date == session_date]
    session_df = session_df.drop_duplicates(subset=['name', 'session_date'], keep='last')
    session_df.reset_index(inplace=True, drop=True)

    fig, ax = plt.subplots(figsize=(14, 8), nrows=1, ncols=1)
    players = session_df.name.unique()

    fig.suptitle(f'RPE session report {session_date}', fontsize=30, weight='bold')
    facecolor = "white"
    fig.set_facecolor(facecolor)

    session_param_values = session_df.rpe.values
    mean_l, std_l = extract_players_rpe_mean_and_std(session_df, rpe_df)

    colors = define_RPE_colors(session_df.rpe.values)

    ax.bar(players, session_param_values, align='center', color=colors, width=0.6, label='RPE', capsize=6)
    for x, y in zip(players, session_param_values):
        ax.text(x, y + 0.1, f'{y}', ha='center', va='bottom', fontsize=12)

    x_tick_labels, y_tick_labels = ax.get_xticklabels(), ax.get_yticklabels()
    for x_tick_label in x_tick_labels:
        x_tick_label.set_fontweight('bold')
    for y_tick_label in y_tick_labels:
        y_tick_label.set_fontweight('bold')
        y_tick_label.set_fontsize(14)

    ax.set_ylabel('RPE', fontsize=18, weight='bold')
    ax.set_xlabel('Players', fontsize=18, weight='bold')
    ax.set_ylim(ymin=0, ymax=10)
    ax.set_facecolor(facecolor)
    plt.xticks(rotation=90)

    RPE_LEGEND_LIST = [
        mpatches.Patch(color=RPE1_COLOR, label='Very Light'),
        mpatches.Patch(color=RPE23_COLOR, label='Light'),
        mpatches.Patch(color=RPE46_COLOR, label='Moderate'),
        mpatches.Patch(color=RPE78_COLOR, label='Vigorous'),
        mpatches.Patch(color=RPE9_COLOR, label='Very Hard'),
        mpatches.Patch(color=RPE10_COLOR, label='Max Effort'),
    ]
    ax.legend(
        handles=RPE_LEGEND_LIST, loc='upper center',
        bbox_to_anchor=(0.5, 1.07), ncol=3, fancybox=True, shadow=True,
        prop={'size': 12}
    )

    # individual_report_dir = os.path.join(exports_path, 'individual_session')
    # save_path = os.path.join(individual_report_dir, f'RPE_session_report_{session_date}.png')
    plt.figtext(0.82, 0.01, "Created by Arian Skoki", ha="center", va="bottom", fontsize=14, weight='bold')
    # fig.savefig(save_path, dpi=150, facecolor=fig.get_facecolor())
    st.pyplot(fig)

    session_rpe_df = rpe_df[rpe_df.session_date == session_date].reset_index(drop=True)
    st.dataframe(session_rpe_df)
