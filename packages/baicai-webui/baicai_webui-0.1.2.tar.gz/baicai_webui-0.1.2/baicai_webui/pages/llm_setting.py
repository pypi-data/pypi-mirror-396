import streamlit as st

from baicai_webui.components.model.model_settings import render_model_settings


def show():
    st.title("大模型配置")

    render_model_settings()


show()
