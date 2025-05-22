import os
import uuid
import logging
import streamlit as st


os.environ['NO_PROXY'] = 'localhost,127.0.0.1,::1'

logger = logging.getLogger(__name__)

st.set_page_config(
    page_title = "GlobalPay",
    page_icon = "🏦",
    layout = "wide",
    initial_sidebar_state = "expanded"
)

st.markdown(
    f"""
<style>
    .st-emotion-cache-kgpedg:before {{
        content: "𖡎 GenAI Hub";
        font-weight: bold;
        font-size: xx-large;
    }}
</style>""",
        unsafe_allow_html=True,
    )

st.title("🏦 GlobalPay", anchor = False)
