import gspread
import cyrtranslit
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import streamlit as st
from datetime import datetime

from matplotlib.transforms import Bbox
from oauth2client.service_account import ServiceAccountCredentials

from pages.helpers.utils import authenticate, add_download_image_button, add_page_logo
from pages.rpe.rpe_plots import create_rpe_bar_plot
from pages.rpe.rpe_helpers import get_rpe_questioneer_df, extract_players_rpe_mean_and_std

add_page_logo()
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
    sheet = client.open(st.secrets.google_sheets.rpe_sheet_name).sheet1

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
    session_date = st.selectbox('Select training date', session_dates, index=len(session_dates) - 1)

    session_df = rpe_df[rpe_df.session_date == session_date]
    session_df = session_df.drop_duplicates(subset=['name', 'session_date'], keep='last')
    session_df.reset_index(inplace=True, drop=True)

    # ---------------------------------------------
    st.header("Session report")

    players = session_df.name.unique()
    session_param_values = session_df.rpe.values
    mean_l, std_l = extract_players_rpe_mean_and_std(session_df, rpe_df)

    fig = create_rpe_bar_plot(
        figsize=(14, 8),
        title=f'RPE session report {session_date}',
        x_label='Players',
        y_label='RPE',
        x_values=players,
        y_values=session_param_values
    )
    fig.text(0.82, -0.2, "Created by Arian Skoki", ha="center", va="bottom", fontsize=14, weight='bold')
    st.pyplot(fig)
    add_download_image_button(
        fig, "Download session report", f'RPE_session_report_{session_date}.png',
        bbox_inches=Bbox([[0, -2.5], fig.get_size_inches()])
    )

    # ---------------------------------------------
    st.markdown("""---""")
    st.header("Team report")

    rpe_df.loc[:, 'week'] = rpe_df.session_date.apply(lambda r: r.isocalendar()[1])
    rpe_df.loc[:, 'year'] = rpe_df.session_date.apply(lambda r: r.isocalendar()[0])

    start_offset_days = 7
    start_index = len(session_dates) - 1 - start_offset_days
    start_index = 0 if start_index < 0 else start_index
    session_start_date = st.selectbox('Select start date', session_dates, index=start_index)
    session_end_date = st.selectbox('Select end date', session_dates, index=len(session_dates) - 1)

    week_df = rpe_df[
        (rpe_df.session_date >= session_start_date) &
        (rpe_df.session_date <= session_end_date)
        ]
    week_df = week_df.groupby('session_date', as_index=False).agg({'rpe': ['mean', 'std']})
    week_df.columns = week_df.columns.droplevel()
    week_df = week_df.rename(columns={'': 'session_date', 'mean': 'rpe_mean', 'std': 'rpe_std'})
    week_df.rpe_mean = week_df.rpe_mean.round(2)
    week_df.rpe_std = week_df.rpe_std.round(2)

    date_obj = datetime.strptime(str(week_df.session_date.iloc[0]), '%Y-%m-%d')
    start_of_week = date_obj
    end_date_obj = datetime.strptime(str(week_df.session_date.iloc[-1]), '%Y-%m-%d')
    end_of_week = end_date_obj

    idx = pd.date_range(start_of_week, end_of_week)
    week_df.index = pd.DatetimeIndex(week_df.session_date)
    week_df = week_df.drop(columns=['session_date'])
    week_df = week_df.reindex(idx, fill_value=0)
    week_df = week_df.reset_index().rename(columns={'index': 'session_date'})
    week_df.loc[:, 'session_date'] = pd.to_datetime(week_df.session_date).dt.date

    week_values = week_df.rpe_mean.values

    team_report_title = f'RPE team report {session_start_date.strftime("%d.%m.%y")}-{session_end_date.strftime("%d.%m.%y")}'
    fig = create_rpe_bar_plot(
        figsize=(14, 8),
        title=team_report_title,
        x_label='Dates',
        y_label='RPE',
        x_values=week_df.session_date,
        y_values=week_values,
        y_err=week_df.rpe_std.values
    )
    fig.text(0.82, 0.01, "Created by Arian Skoki", ha="center", va="bottom", fontsize=14, weight='bold')
    plt.xticks(rotation=15)

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())

    st.pyplot(fig=fig)
    add_download_image_button(fig, "Download team report", f'{team_report_title}.png')
    # ---------------------------------------------
