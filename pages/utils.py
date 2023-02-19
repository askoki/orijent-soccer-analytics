import io
import matplotlib.pyplot as plt
import streamlit as st


def add_download_image_button(fig: plt.Figure, button_text: str, filename: str):
    img = io.BytesIO()
    fig.savefig(img, format='png', facecolor=fig.get_facecolor())

    btn = st.download_button(
        label=button_text,
        data=img,
        file_name=filename,
        mime="image/png"
    )
