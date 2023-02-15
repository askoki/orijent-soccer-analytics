import streamlit as st

from helpers import authenticate

status = authenticate()
if status:
    # st.set_page_config(
    #     page_title="Multipage app",
    #     page_icon='NN'
    # )

    st.title("Main Page")
    st.sidebar.success("Select a page above.")
