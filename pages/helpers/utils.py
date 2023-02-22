import io
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from PIL import Image
from io import StringIO

from matplotlib.backends.backend_pdf import PdfPages
from streamlit_authenticator import Authenticate
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials


def authenticate():
    credentials = {
        'usernames': {}
    }
    for user in st.secrets.auth.users:
        single_cred_dict: dict = {}
        single_cred_dict[user['username']] = {
            'email': user['email'],
            'name': user['name'],
            'password': user['password']
        }
        credentials['usernames'].update(single_cred_dict)

    authenticator = Authenticate(
        credentials,
        st.secrets.auth.cookie['name'],
        st.secrets.auth.cookie['key'],
        st.secrets.auth.cookie['expiry_days'],
    )
    name, authentication_status, username = authenticator.login('Login', 'main')

    if authentication_status:
        authenticator.logout('Logout', 'sidebar')
        st.sidebar.write(f'Welcome *{name}*')
        return authentication_status
    elif authentication_status == False:
        st.error('Username/password is incorrect')
    elif authentication_status == None:
        st.warning('Please enter your username and password')


def add_download_image_button(fig: plt.Figure, button_text: str, filename: str, bbox_inches=None):
    img = io.BytesIO()
    fig.savefig(img, format='png', facecolor=fig.get_facecolor(), bbox_inches=bbox_inches)

    btn = st.download_button(
        label=button_text,
        data=img,
        file_name=filename,
        mime="image/png"
    )


@st.cache_data
def load_google_drive_data() -> pd.DataFrame:
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
    drive_service = build('drive', 'v3', credentials=creds)
    nn_folder_id = '1RXznak6Q4gVWGxY2a9Mnma_yLjfXnVN6'

    results = drive_service.files().list(
        q=f"name='nn_gps_data.csv' and parents in '{nn_folder_id}'"
    ).execute()
    resulting_files = results.get('files', [])
    request = drive_service.files().get_media(fileId=resulting_files[0]['id'])
    content = request.execute()
    csv_data = StringIO(content.decode('utf-8'))
    df = pd.read_csv(csv_data)
    return df


def add_page_logo():
    img = Image.open('NN_logo.jpg')
    st.set_page_config(
        page_title="Nizhny Novgorod Analytics",
        page_icon=img
    )


def add_download_pdf_from_plots_button(button_text: str, filename: str):
    pdf_name = 'pdf_output.pdf'
    pdf = PdfPages(pdf_name)

    for fig in range(1, plt.gcf().number + 1):
        pdf.savefig(fig)
        plt.close()
    pdf.close()
    plt.close()

    with open(pdf_name, "rb") as pdf_file:
        pdf_byte = pdf_file.read()

    st.download_button(
        label=button_text,
        data=pdf_byte,
        file_name=filename,
        mime='application/octet-stream'
    )
