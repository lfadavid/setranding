import pandas as pd
import pygsheets
import streamlit.components.v1 as components
import streamlit as st

st.markdown(
    "[📄 Abrir Planilha Online](https://docs.google.com/spreadsheets/d/1l7G_4VAQGyN9cfmpsS-_bnjfzSqXRJViZMCZ8z6vXSc/edit?usp=sharing)",
    unsafe_allow_html=True
)

# Botão com link externo
st.markdown(
    """
    <a href="https://cotralti-my.sharepoint.com/:l:/g/personal/ldavid_cotralti_com_br/FGQYhiPx_vJCm4nqGhq33CIBerw20ECSlz59IFN64747bQ?nav=NTUxYTM1ODEtNDhiMC00ZTM2LWE2ZDAtNDk4NDhjMjVlNmM0"
       target="_blank">
        <button style="padding: 4px 8px; background-color: #65DDEB; color: white; border: none; border-radius: 6px; cursor: pointer;">
            📎 Enviar comprovante de Container(SharePoint)
        </button>
    </a>
    """,
    unsafe_allow_html=True
)
