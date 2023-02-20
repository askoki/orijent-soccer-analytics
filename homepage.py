import streamlit as st
from PIL import Image
from pages.helpers.constants import FEATURES_2_EXTRACT
from pages.helpers.plots import create_gps_relative_plot
from pages.helpers.utils import authenticate, load_google_drive_data, add_download_image_button

img = Image.open('NN_logo.jpg')
st.set_page_config(
    page_title="Nizhny Novgorod Analytics",
    page_icon=img
)

status = authenticate()
if status:
    df = load_google_drive_data()
    # ------------------------------------------------------
    st.title("GPS single session")
    session_dates = df.sort_values('date_time').date_time.unique()
    session_date = st.selectbox('Select session date', session_dates, index=len(session_dates) - 1)

    session_df = df[df.date_time == session_date]
    session_df.reset_index(inplace=True, drop=True)

    for col in FEATURES_2_EXTRACT:
        session_df[col] = session_df[col].astype(float)

    players = session_df.athlete.unique()
    fig = create_gps_relative_plot(
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
    st.title("GPS week session")
    st.sidebar.success("Select a page above.")
