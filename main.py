
import streamlit as st

# Configurações da página
st.set_page_config(
    page_title="Exportação (Sertranding)",
    page_icon="imagens/cotralti_logo.png",
    layout="wide",

)

pg = st.navigation(
    {

        "𝗛𝗼𝗺𝗲": [st.Page("homepage.py", title="🏢 Cotralti Corporation")],
        "Sertranding": [st.Page("exportacao.py", title="⚙️ Sertranding"),
                        st.Page("aba_dados.py",
                                title="📎 Lançamentos")],
    }

)


pg.run()
