import io
import matplotlib.pyplot as plt
import streamlit as st
from streamlit_authenticator import Authenticate


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
