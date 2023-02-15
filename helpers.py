import streamlit as st
import yaml
from streamlit_authenticator import Authenticate
from yaml import SafeLoader


def authenticate():
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
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
